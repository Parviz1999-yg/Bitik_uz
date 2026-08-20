from pyrogram import filters
from bot import bitik
from services.fsm_service import fsm
from handlers.cv_handler import finish_cv # Yakunlash funksiyasi

@bitik.on_callback_query(filters.regex(r"^(add_more_rel|finish_rel)$"))
async def handle_relative_buttons(client, callback):
    user_id = callback.from_user.id
    lang = fsm.get_data(user_id).get("cv_lang", "uz")
    
    if callback.data == "add_more_rel":
        await callback.message.edit_text("Yana bir qarindosh ma'lumotlarini kiriting (Ism, Yil, Kasb, Manzil):")
    elif callback.data == "finish_rel":
        await callback.message.edit_text("Anketa yakunlanmoqda...")
        await finish_cv(callback.message, lang) # Fayl yaratish jarayoni