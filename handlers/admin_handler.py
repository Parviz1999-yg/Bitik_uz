from pyrogram import filters
from bot import bitik
import config
from core.admin import is_admin
from services.channel_service import enforce_subscription
from services.localization import i18n
from database.db import get_connection
from database.users_repo import set_admin, get_all_users_count, get_user_lang


@bitik.on_message(filters.command(["admin", "setadmin", "tolovlar", "payments"]))
async def admin_commands(client, message):
    if not await enforce_subscription(client, message):
        return
    if not message or not message.from_user:
        return

    user_id = message.from_user.id
    lang = get_user_lang(user_id) or "uz"

    if not is_admin(user_id):
        text = i18n.t("no_admin_access", lang=lang, file="message")
        await message.reply(text)
        return

    command = message.command[0]

    if command == "admin":
        user_count = get_all_users_count()
        text = (
            f"👑 **Admin Paneli**\n\n"
            f"👥 Jami foydalanuvchilar: {user_count}\n\n"
            f"💡 Balans to'ldirishlar tarixini ko'rish uchun /tolovlar buyrug'ini yuboring."
        )
        await message.reply(text)

    elif command == "setadmin":
        if len(message.command) > 1:
            try:
                target_id = int(message.command[1])
                set_admin(target_id)
                await message.reply(f"✅ ID: {target_id} admin etib tayinlandi!")
            except ValueError:
                await message.reply("⚠️ Noto'g'ri ID format kiritildi!")
        else:
            await message.reply("⚠️ Foydalanish: /setadmin [tg_id]")

    elif command in ("payments", "tolovlar"):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """
                    SELECT tg_id, amount, created_at
                    FROM payments
                    ORDER BY created_at DESC
                    LIMIT 20
                    """
                )
                rows = cursor.fetchall()
            finally:
                cursor.close()
                conn.close()

            if not rows:
                await message.reply("📭 Hozircha balans to'ldirish tarixi mavjud emas.")
                return

            text = "💰 **So'nggi balans to'ldirishlar tarixi:**\n\n"
            for row in rows:
                text += (
                    f"👤 Foydalanuvchi ID: <code>{row.get('tg_id')}</code>\n"
                    f"💵 Summa: <b>{row.get('amount'):,.0f} (so'm)</b>\n"
                    f"📅 Vaqti: {row.get('created_at')}\n"
                    f"-------------------\n"
                )
            await message.reply(text)
        except Exception as e:
            await message.reply(
                f"⚠️ To'lovlar tarixini olishda xatolik.\n"
                f"Ehtimol 'payments' jadvali hali yaratilmagan.\n\nXato: {e}"
            )
