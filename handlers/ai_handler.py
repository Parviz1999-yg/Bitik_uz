import time
from pyrogram import filters
from bot import bitik
from google import genai
from database.users_repo import get_user_lang
from services.localization import i18n
from config import GEMINI_KEY

# Gemini mijozini sozlash
client_ai = genai.Client(api_key=GEMINI_KEY)

# Har bir userning oxirgi so'rov vaqtini saqlash uchun lug'at
user_last_request = {}

# 1. /ai komandasi - Suhbatni boshlash uchun
@bitik.on_message(filters.command("ai"))
async def start_ai_chat(client, message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    await message.reply(i18n.t("ai_start", lang=lang, file="message"))

# 2. AI bilan muloqot qilish uchun matn handler'i
@bitik.on_message(filters.text & ~filters.command(["start", "admin", "buy", "help", "setadmin", "create_cv", "create_cv2", "language", "ai", "balans"]))
async def handle_ai_chat(client, message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    text = message.text.strip()
    
    # Rate-limit (1 daqiqada 2 ta so'rov) tekshiruvi
    current_time = time.time()
    last_time = user_last_request.get(user_id, 0)
    
    if current_time - last_time < 30:
        remaining = int(30 - (current_time - last_time))
        raw_text = i18n.t("ai_time", lang=lang, file="message")
        text = raw_text.format(remaining=remaining)
        await message.reply(text)
        return

    # Vaqtni yangilaymiz
    user_last_request[user_id] = current_time
    
    # Kutish haqida xabar
    processing_msg = await message.reply(i18n.t("ai_await", lang=lang, file="message"))
    
    try:
        # Gemini API ga so'rov yuborish
        response = client_ai.models.generate_content(
            model='gemini-3.1-flash-lite',
            contents=text,
        )
        
        answer = response.text
        await processing_msg.edit_text(answer)
        
    except Exception as e:
        await processing_msg.edit_text(f"❌ Xatolik yuz berdi: {e}")