# handlers/admin_handler.py
from pyrogram import filters
from bot import bitik
import config
from services.channel_service import enforce_subscription
from services.localization import i18n
from database.users_repo import set_admin, get_all_users_count, get_user_lang, get_connection

@bitik.on_message(filters.command(["admin", "setadmin", "tolovlar", "payments"]))
async def admin_commands(client, message):
    if not await enforce_subscription(client, message):
        return
    if not message or not message.from_user:
        return
        
    user_id = message.from_user.id
    lang = get_user_lang(user_id) or "uz"

    # 👑 Faqat asosiy admin kirishi uchun qat'iy tekshiruv
    if user_id != config.ADMIN_ID:
        text = i18n.t("no_admin_access", lang=lang, file="message")
        await message.reply(text)
        return

    command = message.command[0]

    # 1. /admin buyrug'i - umumiy ma'lumotlar
    if command == "admin":
        user_count = get_all_users_count()
        text = (
            f"👑 **Admin Paneli**\n\n"
            f"👥 Jami foydalanuvchilar: {user_count}\n\n"
            f"💡 Balans to'ldirishlar tarixini ko'rish uchun /tolovlar buyrug'ini yuboring."
        )
        await message.reply(text)

    # 2. /setadmin buyrug'i - yangi admin tayinlash[cite: 6]
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

    # 3. /payments yoki /tolovlar - Faqat adminga ko'rinadigan to'lovlar tarixi
    elif command in ["payments", "tolovlar"]:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT tg_id, amount, created_at 
                FROM payments 
                ORDER BY created_at DESC 
                LIMIT 20
            """)
            rows = cursor.fetchall()
            cursor.close()
            conn.close()

            if not rows:
                await message.reply("📭 Hozircha balans to'ldirish tarixi mavjud emas.")
                return

            text = "💰 **So'nggi balans to'ldirishlar tarixi:**\n\n"
            for row in rows:
                tg_id = row.get("tg_id")
                amount = row.get("amount")
                date = row.get("created_at")
                text += f"👤 Foydalanuvchi ID: <code>{tg_id}</code>\n"
                text += f"💵 Summa: <b>{amount:,.0f} (so'm)</b>\n"
                text += f"📅 Vaqti: {date}\n"
                text += "-------------------\n"

            await message.reply(text)
        except Exception as e:
            await message.reply(
                f"⚠️ To'lovlar tarixini olishda xatolik yuz berdi.\n"
                f"Ehtimol bazada 'payments' jadvali hali yaratilmagan.\n\nXato: {e}"
            )