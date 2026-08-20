from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def lang_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Uz 🇺🇿 ", callback_data="lang:uz"),
                InlineKeyboardButton("Tj 🇹🇯 ", callback_data="lang:tj")
            ],
            [
                InlineKeyboardButton("Ru 🇷🇺 ", callback_data="lang:ru"),
                InlineKeyboardButton("En 🇬🇧 ", callback_data="lang:en")
            ]
        ]
    )