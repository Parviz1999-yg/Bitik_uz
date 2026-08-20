# keyboards/cv_xato_kb.py
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def cv_xato_keyboard(btn_confirm: str, btn_edit: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(btn_confirm, callback_data="cv_confirm_yes")],
        [InlineKeyboardButton(btn_edit, callback_data="cv_confirm_edit")]
    ])