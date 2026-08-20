from pyrogram import filters
from bot import bitik
from services.cv2_fsm import anketa2_fsm, Anketa2State
from services.localization import i18n
from pyrogram.errors import MessageNotModified

LANG_MAP = {
    "uzbek": "uz",
    "rus": "ru",
    "tadjik": "tj",
    "english": "en"
}

@bitik.on_callback_query(filters.regex(r"^anketa2_lang_(uzbek|tadjik|rus|english)$"))
async def handle_anketa2_language_selection(client, callback_query):
    # Callback data dan til nomini ajratib olamiz (masalan: anketa2_lang_uzbek -> uzbek)
    data = callback_query.data.replace("anketa2_lang_", "")
    lang_code = LANG_MAP.get(data, "uz")
    user_id = callback_query.from_user.id

    # Anketa2 FSM ma'lumotlariga tilni saqlaymiz va format kutishni o'chiramiz
    anketa2_fsm.update_data(user_id, "cv_lang", lang_code)
    anketa2_fsm.update_data(user_id, "waiting_for_format", False)
    
    flow = anketa2_fsm.QUESTIONS_FLOW
    if not flow:
        return
        
    first_state = flow[0]
    anketa2_fsm.set_state(user_id, first_state)
    
    try:
        await callback_query.message.edit_text(i18n.t("cv_starting", lang=lang_code, file="message"))
    except MessageNotModified:
        pass
    
    key = anketa2_fsm.get_question_key(first_state)
    await callback_query.message.reply(i18n.t(key, lang=lang_code, file="anketa2"))
    await callback_query.answer()