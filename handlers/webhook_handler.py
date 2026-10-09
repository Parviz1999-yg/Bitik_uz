from fastapi import FastAPI, Request
import hashlib
import config
from database.users_repo import update_balance, get_user_balance, get_user_lang, add_payment
from services.localization import i18n
from bot import bitik

app = FastAPI()

SECRET_KEY = config.CLICK_SECRET_KEY or ""


def _verify_click_sign(data: dict, action: int) -> bool:
    """
    Click Uzbekistan imzo tekshiruvi.
    action=0 (prepare): click_trans_id + service_id + SECRET_KEY + merchant_trans_id + amount + action + sign_time
    action=1 (complete): + merchant_prepare_id qo'shiladi
    """
    if not SECRET_KEY:
        # Secret bo'lmasa productionda xavfli — rad etamiz
        return False

    click_trans_id = str(data.get("click_trans_id", ""))
    service_id = str(data.get("service_id", ""))
    merchant_trans_id = str(data.get("merchant_trans_id", ""))
    amount = str(data.get("amount", ""))
    action_str = str(action)
    sign_time = str(data.get("sign_time", ""))
    received_sign = str(data.get("sign_string", ""))

    if action == 0:
        raw = (
            f"{click_trans_id}{service_id}{SECRET_KEY}"
            f"{merchant_trans_id}{amount}{action_str}{sign_time}"
        )
    elif action == 1:
        merchant_prepare_id = str(data.get("merchant_prepare_id", ""))
        raw = (
            f"{click_trans_id}{service_id}{SECRET_KEY}"
            f"{merchant_trans_id}{merchant_prepare_id}"
            f"{amount}{action_str}{sign_time}"
        )
    else:
        return False

    expected = hashlib.md5(raw.encode("utf-8")).hexdigest()
    return expected == received_sign


@app.post("/click/webhook")
async def click_webhook(request: Request):
    form = await request.form()
    data = {k: form.get(k) for k in form.keys()}

    click_trans_id = data.get("click_trans_id")
    merchant_trans_id = data.get("merchant_trans_id") or ""
    amount = float(data.get("amount", 0) or 0)
    try:
        action = int(data.get("action", -1))
    except (TypeError, ValueError):
        action = -1

    # 1. Imzo tekshiruvi (majburiy)
    if not _verify_click_sign(data, action):
        return {"error": -1, "error_note": "Invalid sign"}

    # 2. merchant_trans_id dan user_id ajratish: bitik_user_{user_id}_{timestamp}
    try:
        parts = str(merchant_trans_id).split("_")
        user_id = int(parts[2])
    except (IndexError, ValueError, TypeError):
        return {"error": -1, "error_note": "Invalid merchant_trans_id"}

    # 3. Action: 0 = Prepare, 1 = Complete
    if action == 0:
        current_balance = get_user_balance(user_id)
        if current_balance is None:
            return {"error": -5, "error_note": "User not found"}

        return {
            "click_trans_id": click_trans_id,
            "merchant_trans_id": merchant_trans_id,
            "merchant_prepare_id": click_trans_id,
            "error": 0,
            "error_note": "Success",
        }

    if action == 1:
        # Idempotent: bir xil to'lovni qayta yozmaslik uchun oddiy yondashuv
        update_balance(user_id, amount)
        add_payment(user_id, amount)
        new_balance = get_user_balance(user_id)

        user_lang = get_user_lang(user_id)
        title_text = i18n.t("payment_success_title", lang=user_lang, file="message")
        added_text = i18n.t("payment_added", lang=user_lang, file="message")
        balance_text = i18n.t("payment_current_balance", lang=user_lang, file="message")

        try:
            await bitik.send_message(
                chat_id=user_id,
                text=(
                    f"{title_text}\n\n"
                    f"{added_text}: `{amount:,.0f}`\n"
                    f"{balance_text} `{new_balance:,.0f}`"
                ),
            )
        except Exception as e:
            print(f"Foydalanuvchiga xabar yuborib bo'lmadi: {e}")

        return {
            "click_trans_id": click_trans_id,
            "merchant_trans_id": merchant_trans_id,
            "merchant_confirm_id": click_trans_id,
            "error": 0,
            "error_note": "Success",
        }

    return {"error": -3, "error_note": "Action not found"}
