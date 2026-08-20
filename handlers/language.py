from pyrogram import filters
from bot import bitik
from services.localization import i18n
from keyboards.lang_kb import lang_keyboard
from services.channel_service import enforce_subscription
from database.users_repo import get_user_lang, update_user_lang

@bitik.on_message(filters.command("language"))
async def language_cmd(client, message):
    if not await enforce_subscription(client, message):
        return
    
    user_lang = get_user_lang(message.from_user.id)
    # JSON dagi "select_language" kalitidan foydalanildi
    text = i18n.t("select_language", lang=user_lang, file="message")
    
    await message.reply(text, reply_markup=lang_keyboard())

@bitik.on_callback_query(filters.regex(r"^lang:(.*)"))
async def set_language_callback(client, callback):
    lang_code = callback.data.split(":")[1]
    update_user_lang(callback.from_user.id, lang_code)
    
    # JSON dagi "lang_selected" kalitidan foydalanildi
    confirm_text = i18n.t("lang_selected", lang=lang_code, file="message")
    await callback.answer(confirm_text, show_alert=True)
    await callback.message.delete()