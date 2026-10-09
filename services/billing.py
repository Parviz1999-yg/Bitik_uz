"""Balans tekshiruvi va yechish — admin bepul."""
from typing import Optional, Tuple

import config
from core.admin import is_admin, effective_balance
from database.users_repo import deduct_balance
from services.localization import i18n
from keyboards.payment_kb import get_amounts_keyboard

CV_PRICE = getattr(config, "CV_PRICE", 5000)


def can_afford(user_id: int, price: Optional[int] = None) -> bool:
    price = price if price is not None else CV_PRICE
    if is_admin(user_id):
        return True
    return effective_balance(user_id) >= price


def charge_user(user_id: int, price: Optional[int] = None) -> Tuple[bool, Optional[float]]:
    """
    Oddiy foydalanuvchidan atomic yechadi.
    Admin uchun hech narsa yechilmaydi.
    Returns: (success, new_balance_or_None)
    """
    price = price if price is not None else CV_PRICE
    if is_admin(user_id):
        return True, effective_balance(user_id)
    new_bal = deduct_balance(user_id, float(price))
    if new_bal is None:
        return False, None
    return True, new_bal


def low_balance_text(lang: str, price: Optional[int] = None, balance: Optional[float] = None, file: str = "cv") -> str:
    price = price if price is not None else CV_PRICE
    bal = balance if balance is not None else 0.0
    try:
        return i18n.t("cv2_balance_low", lang=lang, file=file).format(
            price=f"{price:,.0f}",
            balance=f"{bal:,.0f}",
        )
    except Exception:
        return (
            f"❌ Balansingiz yetarli emas!\n"
            f"Kerakli summa: {price:,.0f} so'm\n"
            f"Joriy balans: {bal:,.0f} so'm"
        )


async def reply_need_topup(message_or_callback_msg, lang: str, price: Optional[int] = None, balance: Optional[float] = None):
    """Balans yetmasa ogohlantirish + to'lov klaviaturasi."""
    price = price if price is not None else CV_PRICE
    text = low_balance_text(lang, price, balance)
    await message_or_callback_msg.edit_text(text)
    try:
        pay_text = i18n.t("pay_select_amount", lang=lang, file="message")
    except Exception:
        pay_text = "To'lov miqdorini tanlang:"
    await message_or_callback_msg.reply(pay_text, reply_markup=get_amounts_keyboard(lang))
