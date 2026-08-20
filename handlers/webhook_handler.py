from fastapi import FastAPI, Request, HTTPException
import hashlib
import config
from database.users_repo import update_balance, get_user_balance, get_user_lang
from services.localization import i18n  # LocalizationService ni import qilish[cite: 3]

from bot import bitik 

app = FastAPI()

SECRET_KEY = config.CLICK_SECRET_KEY  # Click merchant kabinetidan olingan maxfiy kalit

@app.post("/click/webhook")
async def click_webhook(request: Request):
    data = await request.form()
    
    click_trans_id = data.get("click_trans_id")
    service_id = data.get("service_id")
    merchant_trans_id = data.get("merchant_trans_id") 
    amount = float(data.get("amount", 0))
    action = int(data.get("action", -1))
    sign_time = data.get("sign_time")
    sign_string = data.get("sign_string")
    
    # 1. Imzolarni (Sign) tekshirish (Xavfsizlik uchun)
    # ...
    
    try:
        parts = merchant_trans_id.split("_")
        user_id = int(parts[2])
    except Exception:
        return {"error": -1, "error_note": "Invalid merchant_trans_id"}

    # 2. Action bo'yicha ajratish: 0 - Prepare (Tayyorgarlik), 1 - Complete (Yakunlash)
    if action == 0:
        current_balance = get_user_balance(user_id)
        if current_balance is None:
            return {"error": -5, "error_note": "User not found"}
            
        return {
            "click_trans_id": click_trans_id,
            "merchant_trans_id": merchant_trans_id,
            "error": 0,
            "error_note": "Success"
        }
        
    elif action == 1:
        # Balansni yangilash
        update_balance(user_id, amount)
        new_balance = get_user_balance(user_id)
        
        # Foydalanuvchining bazadagi tilini aniqlaymiz (uz, ru, en, toj)
        user_lang = get_user_lang(user_id)
        
        # i18n orqali foydalanuvchining tiliga mos matnlarni olamiz[cite: 3]
        title_text = i18n.t("payment_success_title", lang=user_lang, file="message")
        added_text = i18n.t("payment_added", lang=user_lang, file="message")
        balance_text = i18n.t("payment_current_balance", lang=user_lang, file="message")
        
        # 3. Foydalanuvchiga Telegram orqali uning tilida xabar yuborish
        try:
            await bitik.send_message(
                chat_id=user_id,
                text=(
                    f"{title_text}\n\n"
                    f"{added_text}: `{amount:,.0f}`\n"
                    f"{balance_text} `{new_balance:,.0f}`"
                )
            )
        except Exception as e:
            print(f"Foydalanuvchiga xabar yuborib bo'lmadi: {e}")

        return {
            "click_trans_id": click_trans_id,
            "merchant_trans_id": merchant_trans_id,
            "merchant_confirm_id": click_trans_id,
            "error": 0,
            "error_note": "Success"
        }
        
    return {"error": -3, "error_note": "Action not found"}