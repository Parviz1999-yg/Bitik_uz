"""Admin huquqi va balans ko'rsatish (cheksiz / bepul saqlanadi)."""
import config
from database.users_repo import get_user_balance

ADMIN_DISPLAY_BALANCE = 999_999_999.0


def is_admin(user_id: int) -> bool:
    """Asosiy admin (ADMIN_ID) — barcha pullik amallar bepul."""
    return bool(config.ADMIN_ID) and user_id == config.ADMIN_ID


def effective_balance(user_id: int) -> float:
    """UI uchun balans: admin bo'lsa cheksiz ko'rsatiladi."""
    if is_admin(user_id):
        return ADMIN_DISPLAY_BALANCE
    return float(get_user_balance(user_id) or 0.0)
