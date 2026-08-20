from pyrogram import filters
from bot import bitik
from database.users_repo import get_user_lang
from services.localization import i18n
from services.channel_service import enforce_subscription

@bitik.on_message(filters.command("help"))
async def help_command(client, message):
    if not await enforce_subscription(client, message):
        return
    user_id = message.from_user.id
    # Foydalanuvchi tilini bazadan olish
    lang = get_user_lang(user_id) or "uz"
    
    # JSON fayldan matnni olish
    text = i18n.t("help_text", lang=lang, file="message")
    
    await message.reply(text)