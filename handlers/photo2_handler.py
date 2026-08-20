# handlers/photo2_handler.py
from pyrogram import filters
from bot import bitik
from services.cv2_fsm import anketa2_fsm, Anketa2State
from services.photo2_service import process_user_photo_anketa2
from services.localization import i18n
from handlers.cv2_handler import anketa2_filter

@bitik.on_message(anketa2_filter & filters.photo & ~filters.command(["start", "create_cv", "create_cv2", "language"]))
async def handle_anketa2_photo(client, message):
    user_id = message.from_user.id
    state = anketa2_fsm.get_state(user_id)
    data = anketa2_fsm.get_data(user_id) or {}
    lang = data.get("cv_lang", "uz")
    
    if data.get("waiting_for_format"):
        await message.reply(i18n.t("warning_choose_format", lang=lang, file="anketa2"))
        return

    if state == Anketa2State.RASM:
        await process_user_photo_anketa2(client, message)