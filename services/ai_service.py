from google import genai
from google.genai import types
from config import GEMINI_KEY

client_ai = genai.Client(api_key=GEMINI_KEY)

user_chats = {}

AI_LANG_INSTRUCTIONS = {
    "uz": "Siz aqlli yordamchisiz. Iltimos, foydalanuvchi bilan muloqotda doimo ravon va adabiy o'zbek tilida javob bering.",
    "ru": "Вы умный помощник. Пожалуйста, всегда отвечайте пользователю на грамотном и вежливом русском языке.",
    "tg": "Шмо ёвари зеҳнӣ ҳастед. Лутфан, дар муошират бо корбар ҳамеша бо забони тоҷикии равон ва адабӣ ҷавоб диҳед.",
    "en": "You are a smart assistant. Please always respond to the user in fluent and professional English."
}

def init_ai_chat(user_id: int, lang: str = "uz"):
    """Foydalanuvchi uchun AI chat sessiyasini boshlab beradi (faollashtiradi)."""
    system_instruction = AI_LANG_INSTRUCTIONS.get(lang, AI_LANG_INSTRUCTIONS["uz"])
    user_chats[user_id] = client_ai.chats.create(
        model='gemini-3.1-flash-lite',
        config=types.GenerateContentConfig(
            system_instruction=system_instruction
        )
    )

def get_ai_response(user_id: int, text: str, lang: str = "uz") -> str:
    try:
        # Agar qandaydir sabab bilan sessiya yo'q bo'lsa, qaytatan ochamiz
        if user_id not in user_chats:
            init_ai_chat(user_id, lang)
        
        chat = user_chats[user_id]
        response = chat.send_message(text)
        return response.text
        
    except Exception as e:
        reset_ai_chat(user_id)
        raise e

def reset_ai_chat(user_id: int):
    if user_id in user_chats:
        del user_chats[user_id]