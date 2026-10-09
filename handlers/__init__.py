"""Barcha handlerlarni import qilish (side-effect: decoratorlar ro'yxatdan o'tadi)."""
from handlers import (  # noqa: F401
    start,
    language,
    cv_handler,
    cv2_handler,
    photo_handler,
    photo2_handler,
    ai_handler,
    balans_handler,
    admin_handler,
    help_handler,
    payment_handler,
    webhook_handler,
)
