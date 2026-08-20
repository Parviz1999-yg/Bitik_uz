from pyrogram import filters
from bot import bitik
from services.user_service import user_service
from services.localization import i18n

@bitik.on_message(filters.command("start"))
async def start(client, message):

    user_service.register_or_update(message.from_user)

    text_uz = i18n.t("start_welcome", lang="uz")
    text_tj = i18n.t("start_welcome", lang="tj")
    text_ru = i18n.t("start_welcome", lang="ru")
    text_en = i18n.t("start_welcome", lang="en")
    
    full_text = f"{text_uz}\n\n{text_tj}\n\n{text_ru}\n\n{text_en}"
    await message.reply(text=full_text)
