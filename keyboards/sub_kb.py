from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.localization import i18n

def get_sub_keyboard(lang: str) -> InlineKeyboardMarkup:
    """A'zo bo'lish va tekshirish tugmalari"""
    # file="kb" parametrini qo'shdik, chunki tugma matnlari kb.json da joylashgan
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(i18n.t("btn_go_to_channel", lang=lang, file="kb"), url="https://t.me/tm_bitik_uz")],
        [InlineKeyboardButton(i18n.t("btn_check_sub", lang=lang, file="kb"), callback_data="check_sub_again")]
    ])