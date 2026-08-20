from pyrogram import filters
from bot import bitik
from services.user_service import user_service
from services.localization import i18n

LANG_MAP = {
    "uzbek": "uz",
    "rus": "ru",
    "tadjik": "tj",
    "english": "en"
}

@bitik.on_callback_query(filters.regex("^(uzbek|tadjik|rus|english)$"))
async def handle_language_selection(client, callback_query):
    data = callback_query.data
    lang_code = LANG_MAP.get(data, "uz")

    user_service.set_language(callback_query.from_user.id, lang_code)
    
    success_text = i18n.t("lang_selected", lang=lang_code)
    
    await callback_query.message.edit_text(text=success_text)
    await callback_query.answer()