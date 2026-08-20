# callbacks/cv2_xato_cb.py
from pyrogram import filters
from bot import bitik
from services.cv2_fsm import anketa2_fsm
from services.localization import i18n
from keyboards.format2_kb import get_format2_keyboard

@bitik.on_callback_query(filters.regex(r"^anketa2_confirm_"))
async def cv2_confirmation_callback(client, callback):
    
    user_id = callback.from_user.id
    data = anketa2_fsm.get_data(user_id) or {}
    lang = data.get("cv_lang", "uz")
    
    await callback.answer()
    
    if callback.data == "anketa2_confirm_yes":
        anketa2_fsm.set_state(user_id, None)
        anketa2_fsm.update_data(user_id, "waiting_for_format", True)
        
        try:
            text = i18n.t("choose_document_format", lang=lang, file="anketa2")
        except Exception:
            text = "📁 Hujjat formatini tanlang:"
        
        try:
            await callback.message.delete()
        except Exception:
            pass
            
        await client.send_message(
            chat_id=user_id,
            text=text,
            reply_markup=get_format2_keyboard(prefix="anketa2")
        )
        
    elif callback.data == "anketa2_confirm_edit":
        anketa2_fsm.finish(user_id)
        
        try:
            text = i18n.t("cv_restarted", lang=lang, file="anketa2")
        except Exception:
            text = "❌ Ma'lumotlar tozalandi. Qaytadan boshlash uchun /create_cv2 buyrug'ini bosing:"
        
        try:
            await callback.message.delete()
        except Exception:
            pass
            
        await client.send_message(
            chat_id=user_id,
            text=text
        )