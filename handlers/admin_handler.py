from pyrogram import filters
from bot import bitik
import config
from services.localization import i18n
from database.users_repo import set_admin, get_all_users_count, get_user_lang

@bitik.on_message(filters.command(["admin", "setadmin"]))
async def admin_commands(client, message):
    if not message or not message.from_user:
        return
        
    user_id = message.from_user.id
    lang = get_user_lang(user_id) or "uz"

    # Admin ekanligini tekshirish
    if user_id != config.ADMIN_ID:
        # Admin bo'lmaganlar uchun xabar
        text = i18n.t("no_admin_access", lang=lang, file="message")
        await message.reply(text)
        return

    # Agar admin bo'lsa, buyruqlarni bajarish
    if message.command[0] == "admin":
        user_count = get_all_users_count()
        text = f"👑 **Admin Paneli**\n\n👥 Jami foydalanuvchilar: {user_count}"
        await message.reply(text)

    elif message.command[0] == "setadmin":
        if len(message.command) > 1:
            target_id = int(message.command[1])
            set_admin(target_id)
            await message.reply(f"✅ ID: {target_id} admin etib tayinlandi!")
        else:
            await message.reply("⚠️ Foydalanish: /setadmin [tg_id]")