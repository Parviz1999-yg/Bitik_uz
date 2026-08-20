from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.localization import i18n  # LocalizationService obyektingiz joylashgan yo'ldan import qilasiz[cite: 3]

def get_amounts_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    """Summa tanlash tugmalari (i18n LocalizationService orqali)"""
    
    # i18n orqali bekor qilish matnini olish (masalan, 'message.json' yoki shunga o'xshash fayldan)
    cancel_text = i18n.t("btn_cancel", lang=lang, file="message")

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("3000", callback_data="pay_amt_3000"),
            InlineKeyboardButton("6000", callback_data="pay_amt_6000"),
            InlineKeyboardButton("9000", callback_data="pay_amt_9000"),
            InlineKeyboardButton("12000", callback_data="pay_amt_12000")
        ],
        [
            InlineKeyboardButton("5000", callback_data="pay_amt_5000"),
            InlineKeyboardButton("10000", callback_data="pay_amt_10000"),
            InlineKeyboardButton("15000", callback_data="pay_amt_15000"),
            InlineKeyboardButton("20000", callback_data="pay_amt_20000")
        ],
        [
            InlineKeyboardButton(cancel_text, callback_data="pay_cancel")
        ]
    ])

def get_payment_methods_keyboard(amount: int, click_web_url: str, lang: str = "uz") -> InlineKeyboardMarkup:
    """To'lov usullarini tanlash tugmalari (i18n LocalizationService orqali)"""
    
    # i18n orqali har bir til uchun matnlarni chaqirib olamiz
    btn_app = i18n.t("btn_click_app", lang=lang, file="message")
    btn_term = i18n.t("btn_click_terminal", lang=lang, file="message")
    btn_cancel = i18n.t("btn_cancel", lang=lang, file="message")

    return InlineKeyboardMarkup([
        # 1-usul: Click Ilova / veb orqali o'tish
        #[InlineKeyboardButton(btn_app, url=click_web_url)],
        # 2-usul: CLICK Terminal (Telegram orqali rasmiy Invoys/chek)
        [InlineKeyboardButton(btn_term, callback_data=f"method_clickterm_{amount}")],
        [InlineKeyboardButton(btn_cancel, callback_data="pay_cancel")]
    ])