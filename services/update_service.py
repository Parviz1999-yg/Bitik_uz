import os
import subprocess
import asyncio
from database.db import get_connection
from database.users_repo import get_user_lang  # Foydalanuvchi tilini olish uchun repo
from services.localization import i18n        # Siz ko'rsatgan i18n xizmati[cite: 10]

def get_current_commit():
    """Git orqali joriy commit ID sini olish"""
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("ascii").strip()
    except Exception:
        return None

def get_all_user_ids():
    """Bazadagi barcha foydalanuvchilarning ID larini olish"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT tg_id FROM users")
        rows = cursor.fetchall()
        # Row formatiga qarab tg_id larni list qilib qaytaramiz
        return [row["tg_id"] if isinstance(row, dict) else row[0] for row in rows]
    finally:
        cursor.close()
        conn.close()

async def check_and_notify_users(client):
    """Deploy bo'lib bot qayta yoqilganda yangilikni tekshirish va xabar yuborish"""
    current_commit = get_current_commit()
    if not current_commit:
        return

    version_file = "last_commit.txt"
    last_commit = ""
    
    if os.path.exists(version_file):
        with open(version_file, "r") as f:
            last_commit = f.read().strip()

    # Agar yangi commit bo'lsa (demak yangi push qilinib, Railway deploy qilgan)
    if current_commit != last_commit:
        user_ids = get_all_user_ids()
        
        for user_id in user_ids:
            # 1. Bazadan foydalanuvchi tilini olish (agar topilmasa 'uz' qaytadi)
            lang = get_user_lang(user_id) or "uz"
            
            # 2. JSON fayldan (masalan: messages.json yoki o'zingizning i18n faylingizdan) tilga mos matnni olish[cite: 10]
            # 'notifications' bo'limi ichidagi 'bot_updated' kalitini chaqiramiz
            update_text = i18n.t("bot_updated", lang=lang, file="message")

            try:
                await client.send_message(user_id, update_text)
                await asyncio.sleep(0.05) # Flood wait oldini olish uchun
            except Exception:
                continue

        # Joriy commitni faylga yozib qo'yamiz, qayta takrorlanmasligi uchun
        with open(version_file, "w") as f:
            f.write(current_commit)