from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def anketa2_lang_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Uz 🇺🇿 ", callback_data="anketa2_lang:uz"),
                InlineKeyboardButton("Tj 🇹🇯 ", callback_data="anketa2_lang:tj")
            ],
            [
                InlineKeyboardButton("Ru 🇷🇺 ", callback_data="anketa2_lang:ru"),
                InlineKeyboardButton("En 🇬🇧 ", callback_data="anketa2_lang:en")
            ]
        ]
    )