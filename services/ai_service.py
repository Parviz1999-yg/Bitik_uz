from google import genai
from google.genai import types
from config import GEMINI_KEY

# Gemini mijozini sozlash
client_ai = genai.Client(api_key=GEMINI_KEY)

# Har bir user uchun chat sessiyalarini saqlash (suhbat tarixi uchun)
user_chats = {}

# Har bir til uchun Gemini'ga beriladigan ko'rsatmalar
AI_LANG_INSTRUCTIONS = {
    "uz": "Siz aqlli yordamchisiz. Iltimos, foydalanuvchi bilan muloqotda doimo ravon va adabiy o'zbek tilida javob bering.",
    "ru": "Вы умный помощник. Пожалуйста, всегда отвечайте пользователю на грамотном и вежливом русском языке.",
    "tg": "Шмо ёвари зеҳнӣ ҳастед. Лутфан, дар муошират бо корбар ҳамеша бо забони тоҷикии равон ва адабӣ ҷавоб диҳед.",
    "en": "You are a smart assistant. Please always respond to the user in fluent and professional English."
}

def get_ai_response(user_id: int, text: str, lang: str = "uz") -> str:
    """
    Foydalanuvchi xabarini Gemini chatiga yuboradi va javobni qaytaradi.
    Agar chat mavjud bo'lmasa, uning tiliga mos ravishda yangi ochadi.
    """
    try:
        # Agar foydalanuvchining chat sessiyasi hali yaratilmagan bo'lsa, ochamiz
        if user_id not in user_chats:
            system_instruction = AI_LANG_INSTRUCTIONS.get(lang, AI_LANG_INSTRUCTIONS["uz"])
            
            user_chats[user_id] = client_ai.chats.create(
                model='gemini-3.1-flash-lite',
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction
                )
            )
        
        # Chat orqali xabar yuborish
        chat = user_chats[user_id]
        response = chat.send_message(text)
        return response.text
        
    except Exception as e:
        # Xatolik chiqsa chat sessiyasini tozalaymiz va xatoni tashlaymiz
        reset_ai_chat(user_id)
        raise e

def reset_ai_chat(user_id: int):
    """Foydalanuvchining chat tarixini tozalaydi."""
    if user_id in user_chats:
        del user_chats[user_id]