import time
import asyncio
from pyrogram import filters
from bot import bitik
from google import genai
from database.users_repo import get_user_lang
from services.localization import i18n
from config import GEMINI_KEY

client_ai = genai.Client(api_key=GEMINI_KEY)

user_last_request = {}
user_chats = {}
user_last_active = {} # Foydalanuvchining oxirgi faollik vaqti

# RAMni tozalab turuvchi fon jarayoni (Background task)
async def cleanup_memory():
    while True:
        await asyncio.sleep(600) # Har 10 daqiqada tekshiradi
        now = time.time()
        # 30 daqiqadan (1800 sekund) ko'p yozmaganlarning tarixini o'chiramiz
        inactive_users = [uid for uid, last_time in user_last_active.items() if now - last_time > 1800]
        for uid in inactive_users:
            user_chats.pop(uid, None)
            user_last_request.pop(uid, None)
            user_last_active.pop(uid, None)

# Bot ishga tushganda buni chaqirib qo'yish kerak (masalan, main faylda):
# asyncio.create_task(cleanup_memory())

@bitik.on_message(filters.command("ai"))
async def start_ai_chat(client, message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    if user_id in user_chats:
        del user_chats[user_id]
    await message.reply(i18n.t("ai_start", lang=lang, file="message"))

@bitik.on_message(filters.text & ~filters.command(["start", "admin", "buy", "help", "setadmin", "create_cv", "create_cv2", "language", "ai", "balans"]))
async def handle_ai_chat(client, message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    text = message.text.strip()
    
    current_time = time.time()
    last_time = user_last_request.get(user_id, 0)
    
    if current_time - last_time < 30:
        remaining = int(30 - (current_time - last_time))
        raw_text = i18n.t("ai_time", lang=lang, file="message")
        limit_text = raw_text.format(remaining=remaining)
        await message.reply(limit_text)
        return

    user_last_request[user_id] = current_time
    user_last_active[user_id] = current_time # Faollik vaqtini yangilaymiz
    
    processing_msg = await message.reply(i18n.t("ai_await", lang=lang, file="message"))
    
    try:
        if user_id not in user_chats:
            # Model nomini o'zingiz ishlatayotgan to'g'ri nomga tekshirib qo'ying (masalan: gemini-2.5-flash)
            user_chats[user_id] = client_ai.chats.create(model='gemini-3.1-flash-lite')
        
        chat = user_chats[user_id]
        response = chat.send_message(text)
        
        answer = response.text
        await processing_msg.edit_text(answer)
        
    except Exception as e:
        if user_id in user_chats:
            del user_chats[user_id]
        await processing_msg.edit_text("❌ Tizimda xatolik yuz berdi, iltimos keyinroq urinib ko'ring.")