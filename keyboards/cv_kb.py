from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def cv_lang_keyboard(prefix: str = "cv") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("O'zbekcha", callback_data=f"{prefix}_lang:uz"),
            InlineKeyboardButton("Русский", callback_data=f"{prefix}_lang:ru")
        ],
        [
            InlineKeyboardButton("Тоҷикӣ", callback_data=f"{prefix}_lang:tj"),
            InlineKeyboardButton("English", callback_data=f"{prefix}_lang:en")
        ]
    ])