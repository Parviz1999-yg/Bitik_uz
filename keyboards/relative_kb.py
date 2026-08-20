from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.localization import i18n

def get_relatives_keyboard(lang: str):
    # i18n xizmati orqali 4 ta til uchun tarjimalarni olish
    add_text = i18n.t("add_relative_btn", lang=lang, file="kb")
    finish_text = i18n.t("finish_cv_btn", lang=lang, file="kb")
    
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(add_text, callback_data="add_more_rel")],
        [InlineKeyboardButton(finish_text, callback_data="finish_rel")]
    ])