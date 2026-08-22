import os
import subprocess
import asyncio
from google import genai
from config import GEMINI_KEY
from database.db import get_connection
from database.users_repo import get_user_lang  
from services.localization import i18n        

client_ai = genai.Client(api_key=GEMINI_KEY)

def get_current_commit():
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL).decode("ascii").strip()
        return commit
    except Exception:
        railway_commit = os.getenv("RAILWAY_GIT_COMMIT_SHA")
        return railway_commit or None

def get_commit_message():
    try:
        msg = subprocess.check_output(["git", "log", "-1", "--pretty=%B"], stderr=subprocess.DEVNULL).decode("utf-8").strip()
        if msg:
            return msg
    except Exception:
        pass
    
    return os.getenv("RAILWAY_GIT_COMMIT_MESSAGE", "Tizimda yaxshilanishlar amalga oshirildi.")

def translate_text(text: str, target_lang: str) -> str:
    """Gemini yordamida matnni foydalanuvchi tiliga tarjima qilish"""
    if target_lang == "uz":
        return text  # Asosan o'zbekcha yozsangiz, o'zbeklarga tarjima shart emas
        
    lang_names = {
        "ru": "русский",
        "tg": "тоҷикӣ",
        "en": "English"
    }
    target = lang_names.get(target_lang, "English")
    
    try:
        response = client_ai.models.generate_content(
            model='gemini-3.1-flash-lite',
            contents=f"Translate this update changelog into {target}. Keep it natural, concise, and suitable for a Telegram bot notification: {text}"
        )
        return response.text.strip()
    except Exception:
        return text  # Xatolik bo'lsa o'z holicha qoldiramiz

def get_all_user_ids():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT tg_id FROM users")
        rows = cursor.fetchall()
        return [row["tg_id"] if isinstance(row, dict) else row[0] for row in rows]
    finally:
        cursor.close()
        conn.close()

async def check_and_notify_users(client):
    current_commit = get_current_commit()
    if not current_commit:
        return

    version_file = "last_commit.txt"
    last_commit = ""
    
    if os.path.exists(version_file):
        with open(version_file, "r") as f:
            last_commit = f.read().strip()

    if current_commit != last_commit:
        user_ids = get_all_user_ids()
        raw_commit_msg = get_commit_message()
        
        # Tarjimalarni oldindan keshlash uchun lug'at (har safar bir xil tildagilarga Gemini so'rov yubormasligi uchun)
        translated_cache = {}
        
        for user_id in user_ids:
            lang = get_user_lang(user_id) or "uz"
            
            # Agar bu til uchun tarjima hali qilinmagan bo'lsa, Gemini tarjima qiladi
            if lang not in translated_cache:
                translated_cache[lang] = translate_text(raw_commit_msg, lang)
            
            localized_commit_msg = translated_cache[lang]
            
            # JSON'dan shablonni olib, mos tildagi tarjima qilingan commit'ni joylaymiz
            raw_template = i18n.t("bot_updated", lang=lang, file="message")
            update_text = raw_template.format(commit_message=localized_commit_msg)

            try:
                await client.send_message(user_id, update_text, parse_mode="HTML")
                await asyncio.sleep(0.05) 
            except Exception:
                continue

        with open(version_file, "w") as f:
            f.write(current_commit)