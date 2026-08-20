# keyboards/cv2_davom_kb.py
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.localization import i18n

def get_cv2_davom_keyboard(lang: str) -> InlineKeyboardMarkup:
    """ /create_cv2 buyrug'i uchun narx va balans chiqgandagi davom etish tugmasi """
    btn_continue = i18n.t("btn_continue", lang=lang, file="cv") 
    btn_cancel = i18n.t("btn_cancel", lang=lang, file="cv") 
    
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"✅ {btn_continue}", callback_data="cv2_proceed")],
        [InlineKeyboardButton(f"❌ {btn_cancel}", callback_data="cv2_cancel")]
    ])