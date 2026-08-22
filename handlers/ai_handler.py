import time
from pyrogram import filters
from bot import bitik
from database.users_repo import get_user_lang
from services.localization import i18n
from services.channel_service import enforce_subscription
from services.ai_service import get_ai_response, reset_ai_chat, user_chats

user_last_request = {}

# 1. /ai komandasi - AI bilan muloqot rejimini YOQISH
@bitik.on_message(filters.command("ai"))
async def start_ai_chat(client, message):
    if not await enforce_subscription(client, message):
        return
    if not message or not message.from_user:
        return
        
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    
    # Sessiyani boshlaymiz
    await message.reply(i18n.t("ai_start", lang=lang, file="message"))

# 2. AI rejimidan chiqish komandasi (/stop yoki /exit)
@bitik.on_message(filters.command("stopai"))
async def stop_ai_chat(client, message):
    if not message or not message.from_user:
        return
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    
    if user_id in user_chats:
        reset_ai_chat(user_id)
        await message.reply(i18n.t("ai_stopped", lang=lang, file="message"))
    else:
        await message.reply("Siz hozir AI rejimida emassiz.")

# 3. AI bilan muloqot qilish handler'i (Faqat AI rejimida turganlarga ishlaydi)
@bitik.on_message(filters.text & ~filters.command(["start", "admin", "tolovlar", "buy", "help", "setadmin", "create_cv", "create_cv2", "language", "ai", "balans", "exit", "stop"]))
async def handle_ai_chat(client, message):
    if not message or not message.from_user:
        return
        
    user_id = message.from_user.id
    
    # Agar foydalanuvchi /ai buyrug'ini bosib AI rejimiga KIRMAGAN bo'lsa, o'tkazib yuboramiz
    if user_id not in user_chats:
        return

    if not await enforce_subscription(client, message):
        return
        
    lang = get_user_lang(user_id)
    text = message.text.strip()
    
    # Rate-limit (30 sekundlik) tekshiruvi
    current_time = time.time()
    last_time = user_last_request.get(user_id, 0)
    
    if current_time - last_time < 30:
        remaining = int(30 - (current_time - last_time))
        raw_text = i18n.t("ai_time", lang=lang, file="message")
        limit_text = raw_text.format(remaining=remaining)
        await message.reply(limit_text)
        return

    user_last_request[user_id] = current_time
    processing_msg = await message.reply(i18n.t("ai_await", lang=lang, file="message"))
    
    try:
        # AI dan javobni olamiz
        answer = get_ai_response(user_id, text, lang)
        
        # Javob oxiriga to'xtatish haqidagi eslatmani qo'shamiz
        footer = i18n.t("ai_footer", lang=lang, file="message")
        full_response = answer + footer
        
        await processing_msg.edit_text(full_response, parse_type="html") # Yoki Pyrogram qaysi parse_mode'ni qo'llab-quvvatlasa
        
    except Exception as e:
        await processing_msg.edit_text(f"❌ Xatolik yuz berdi: {e}")