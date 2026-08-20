from database.users_repo import add_user, get_user_lang, update_user_lang

class UserService:
    def register_or_update(self, user):
        """
        Handlerlarda har safar xabar kelganda chaqiriladi.
        Foydalanuvchini bazaga qo'shadi yoki faolligini yangilaby boradi.
        """
        if not user:
            return
        add_user(user)

    def set_language(self, tg_id: int, lang: str):
        """Foydalanuvchi tilini o'zgartirish"""
        update_user_lang(tg_id, lang)

    def get_language(self, tg_id: int) -> str:
        """Foydalanuvchi tilini olish"""
        return get_user_lang(tg_id)

# Loyiha bo'ylab ishlatish uchun obyekt yaratamiz
user_service = UserService()