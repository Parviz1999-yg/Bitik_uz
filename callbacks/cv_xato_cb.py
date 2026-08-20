# callbacks/cv_xato_cb.py
from pyrogram import filters
from bot import bitik
from services.cv_fsm import fsm
from services.localization import i18n
from keyboards.format_kb import get_format_keyboard

@bitik.on_callback_query(filters.regex(r"^cv_confirm_"))
async def cv_confirmation_callback(client, callback):
    
    user_id = callback.from_user.id
    data = fsm.get_data(user_id) or {}
    lang = data.get("cv_lang", "uz")
    
    await callback.answer()
    
    if callback.data == "cv_confirm_yes":
        fsm.set_state(user_id, None)
        fsm.update_data(user_id, "waiting_for_format", True)
        
        text = i18n.t("choose_document_format", lang=lang, file="cv")
        
        try:
            await callback.message.delete()
        except Exception:
            pass
            
        await client.send_message(
            chat_id=user_id,
            text=text,
            reply_markup=get_format_keyboard(prefix="cv")
        )
            
    elif callback.data == "cv_confirm_edit":
        fsm.finish(user_id)
        text = i18n.t("cv_restarted", lang=lang, file="cv")
        
        try:
            await callback.message.delete()
        except Exception:
            pass
            
        await client.send_message(
            chat_id=user_id,
            text=text if text else "❌ Ma'lumotlar tozalandi. Qaytadan boshlash uchun /create_cv buyrug'ini bosing."
        )