# callbacks/cv2_davom_cb.py
from pyrogram import filters
from bot import bitik
from services.cv2_fsm import anketa2_fsm # FSM o'zgardi
from keyboards.cv2_kb import anketa2_lang_keyboard # Keyboard o'zgardi
from keyboards.payment_kb import get_amounts_keyboard
from services.localization import i18n
from database.users_repo import get_user_lang, get_user_balance

CV_PRICE = 5000  # Ma'lumotnoma yaratish narxi

# --- DAVOM ETISH CALLBACK'I ---
@bitik.on_callback_query(filters.regex(r"^cv2_proceed$"))
async def cv2_proceed_callback(client, callback):
    user_id = callback.from_user.id
    lang = get_user_lang(user_id)
    balance = get_user_balance(user_id)
    
    if balance >= CV_PRICE:
        anketa2_fsm.finish(user_id) # FSM o'zgardi
        anketa2_fsm.update_data(user_id, "cv_lang", lang) # FSM o'zgardi
        anketa2_fsm.update_data(user_id, "waiting_for_format", False) # FSM o'zgardi
        
        text = i18n.t("select_cv_language", lang=lang, file="message")
        success_msg = i18n.t("cv2_balance_enough", lang=lang, file="cv")
        
        await callback.message.edit_text(success_msg)
        # Til tugmasi keyboard'i o'zgardi
        await callback.message.reply(text, reply_markup=anketa2_lang_keyboard())
    else:
        warning_text = i18n.t("cv2_balance_low", lang=lang, file="cv").format(
            price=f"{CV_PRICE:,.0f}",
            balance=f"{balance:,.0f}"
        )
        await callback.message.edit_text(warning_text)
        await callback.message.reply(
            i18n.t("pay_select_amount", lang=lang, file="message"),
            reply_markup=get_amounts_keyboard(lang)
        )
        
    await callback.answer()


# --- BEKOR QILISH CALLBACK'I ---
@bitik.on_callback_query(filters.regex(r"^cv2_cancel$"))
async def cv2_cancel_callback(client, callback):
    user_id = callback.from_user.id
    lang = get_user_lang(user_id)
    cancel_text = i18n.t("payment_cancelled", lang=lang, file="message")
    
    await callback.message.edit_text(cancel_text)
    await callback.answer()