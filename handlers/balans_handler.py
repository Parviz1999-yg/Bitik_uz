import sys
import os



from pyrogram import filters
from bot import bitik
from database.users_repo import get_user_balance, get_user_lang, get_user_points
from services.localization import i18n


@bitik.on_message(filters.command("balans"))
async def balance_command(client, message):
    user_id = message.from_user.id
    balance = get_user_balance(user_id)  
    points = get_user_points(user_id)
    lang = get_user_lang(user_id) or "uz"

    formatted_balance = f"{balance:,.2f}"
    raw_text = i18n.t("user_balance", lang=lang, file="message")

    text = raw_text.format(balance=formatted_balance, points=points)
    
    await message.reply(text)