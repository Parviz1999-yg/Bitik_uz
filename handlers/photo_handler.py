# handlers/photo_handler.py
from pyrogram import filters
from bot import bitik
from services.cv_fsm import fsm, CVState
from services.localization import i18n
from handlers.cv_handler import cv_filter
from services.photo_service import process_user_photo

@bitik.on_message(cv_filter & filters.photo & ~filters.command(["start", "create_cv", "create_cv2", "language"]))
async def handle_cv_photo(client, message):
    user_id = message.from_user.id
    state = fsm.get_state(user_id)
    data = fsm.get_data(user_id) or {}
    lang = data.get("cv_lang", "uz")
    
    if data.get("waiting_for_format"):
        await message.reply(i18n.t("warning_choose_format", lang=lang, file="cv"))
        retur

    if state == CVState.RASM:
        # Rasm qabul qilish va kesish ishlari to'liq service orqali bajariladi
        await process_user_photo(client, message)