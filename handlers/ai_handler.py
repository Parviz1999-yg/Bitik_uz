import time
from pyrogram import filters
from bot import bitik
from google import genai
from database.users_repo import get_user_lang
from services.localization import i18n
from config import GEMINI_KEY

from services.channel_service import enforce_subscription

# Gemini mijozini sozlash
client_ai = genai.Client(api_key=GEMINI_KEY)

# Har bir userning oxirgi so'rov vaqtini saqlash uchun lug'at
user_last_request = {}

# Har bir user uchun chat sessiyalarini saqlash (suhbat tarixi uchun)
user_chats = {}

# 1. /ai komandasi - Suhbatni boshlash uchun
@bitik.on_message(filters.command("ai"))
async def start_ai_chat(client, message):
    if not await enforce_subscription(client, message):
        return
    if not message or not message.from_user:
        return
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    # /ai bosilganda oldingi chat tarixini tozalab, yangidan boshlaymiz
    if user_id in user_chats:
        del user_chats[user_id]
    await message.reply(i18n.t("ai_start", lang=lang, file="message"))

# 2. AI bilan muloqot qilish uchun matn handler'i
@bitik.on_message(filters.text & ~filters.command(["start", "admin", "tolovlar", "buy", "help", "setadmin", "create_cv", "create_cv2", "language", "ai", "balans"]))
async def handle_ai_chat(client, message):
    if not await enforce_subscription(client, message):
        return
    if not message or not message.from_user:
        return
        
    user_id = message.from_user.id
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

    # Vaqtni yangilaymiz
    user_last_request[user_id] = current_time
    
    # Kutish haqida xabar
    processing_msg = await message.reply(i18n.t("ai_await", lang=lang, file="message"))
    
    try:
        # Agar foydalanuvchining chat sessiyasi hali yaratilmagan bo'lsa, ochamiz
        if user_id not in user_chats:
            user_chats[user_id] = client_ai.chats.create(model='gemini-3.1-flash-lite')
        
        # Chat orqali xabar yuborish
        chat = user_chats[user_id]
        response = chat.send_message(text)
        
        answer = response.text
        await processing_msg.edit_text(answer)
        
    except Exception as e:
        # Xatolik chiqsa chat sessiyasini tozalaymiz
        if user_id in user_chats:
            del user_chats[user_id]
        await processing_msg.edit_text(f"❌ Xatolik yuz berdi: {e}")