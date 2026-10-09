"""
Click Uzbekistan webhook (FastAPI).

Merchant kabinetda URL:
  https://<YOUR_PUBLIC_HOST>/click/webhook

Prepare (action=0) va Complete (action=1) — imzo majburiy.
"""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from services.click_service import (
    verify_sign,
    parse_user_id_from_merchant_trans,
    error_response,
)
from database.payments_repo import record_click_payment, payment_exists, user_exists
from database.users_repo import get_user_lang
from services.localization import i18n
from bot import bitik

app = FastAPI(title="bitik.uz Click Webhook", docs_url=None, redoc_url=None)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "bitik-click"}


@app.post("/click/webhook")
async def click_webhook(request: Request):
    form = await request.form()
    data = {k: form.get(k) for k in form.keys()}

    try:
        action = int(data.get("action", -1))
    except (TypeError, ValueError):
        return JSONResponse(error_response(-3, "Action not found"))

    click_trans_id = data.get("click_trans_id")
    merchant_trans_id = str(data.get("merchant_trans_id") or "")
    try:
        amount = float(data.get("amount") or 0)
    except (TypeError, ValueError):
        amount = 0.0

    if not verify_sign(data, action):
        return JSONResponse(error_response(-1, "Invalid sign"))

    user_id = parse_user_id_from_merchant_trans(merchant_trans_id)
    if user_id is None:
        return JSONResponse(error_response(-8, "Invalid merchant_trans_id"))

    # --- Prepare ---
    if action == 0:
        if not user_exists(user_id):
            return JSONResponse(error_response(-5, "User does not exist"))

        # Allaqachon to'langan tranzaksiya
        if click_trans_id and payment_exists(str(click_trans_id)):
            return JSONResponse(
                error_response(
                    -4,
                    "Already paid",
                    click_trans_id=click_trans_id,
                    merchant_trans_id=merchant_trans_id,
                )
            )

        # merchant_prepare_id — keyingi Complete da qaytariladi
        prepare_id = str(click_trans_id)
        return {
            "click_trans_id": click_trans_id,
            "merchant_trans_id": merchant_trans_id,
            "merchant_prepare_id": prepare_id,
            "error": 0,
            "error_note": "Success",
        }

    # --- Complete ---
    if action == 1:
        if not user_exists(user_id):
            return JSONResponse(error_response(-5, "User does not exist"))

        is_new, new_balance = record_click_payment(
            tg_id=user_id,
            amount=amount,
            click_trans_id=str(click_trans_id or ""),
            merchant_trans_id=merchant_trans_id,
        )

        if is_new:
            lang = get_user_lang(user_id)
            title = i18n.t("payment_success_title", lang=lang, file="message")
            added = i18n.t("payment_added", lang=lang, file="message")
            bal_lbl = i18n.t("payment_current_balance", lang=lang, file="message")
            try:
                await bitik.send_message(
                    chat_id=user_id,
                    text=(
                        f"{title}\n\n"
                        f"{added}: `{amount:,.0f}`\n"
                        f"{bal_lbl} `{new_balance:,.0f}`"
                    ),
                )
            except Exception as e:
                print(f"Click notify xato: {e}")

        return {
            "click_trans_id": click_trans_id,
            "merchant_trans_id": merchant_trans_id,
            "merchant_confirm_id": click_trans_id,
            "error": 0,
            "error_note": "Success",
        }

    return JSONResponse(error_response(-3, "Action not found"))
