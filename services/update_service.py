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
    """Railway va Git muhitidan versiyani aniqlash (Xavfsiz versiya)"""
    # 1. Railway'ning o'zining deploy ID si (har bir deployda 100% o'zgaradi)
    railway_deploy_id = os.getenv("RAILWAY_DEPLOYMENT_ID")
    if railway_deploy_id:
        print(f"[INFO] Railway Deployment ID topildi: {railway_deploy_id}")
        return railway_deploy_id

    # 2. Railway Git Commit SHA
    railway_commit = os.getenv("RAILWAY_GIT_COMMIT_SHA")
    if railway_commit:
        print(f"[INFO] Railway Git Commit topildi: {railway_commit}")
        return railway_commit

    # 3. Agar local kompyuterda bo'lsa Git orqali
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL).decode("ascii").strip()
        if commit:
            return commit
    except Exception:
        pass

    # 4. Agar umuman topilmasa, vaqtinchalik unikal identifikator qaytaramiz (kod to'xtab qolmasligi uchun)
    print("[OGOHLANTIRISH] Git yoki Railway versiyasi topilmadi, zaxira versiyadan foydalanilmoqda.")
    return "railway_auto_version_1"

def get_commit_message():
    # Railway o'зи yuboradigan commit xabarini o'qiymiz
    railway_msg = os.getenv("RAILWAY_GIT_COMMIT_MESSAGE")
    if railway_msg:
        return railway_msg
        
    try:
        msg = subprocess.check_output(["git", "log", "-1", "--pretty=%B"], stderr=subprocess.DEVNULL).decode("utf-8").strip()
        if msg:
            return msg
    except Exception:
        pass
    
    return "Bot yangilandi va yanada yaxshilandi."

def translate_text(text: str, target_lang: str) -> str:
    if target_lang == "uz":
        return text  
    
    lang_names = {"ru": "русский", "tj": "тоҷикӣ", "en": "English"}
    target = lang_names.get(target_lang, "English")
    
    try:
        response = client_ai.models.generate_content(
            model='gemini-3.1-flash-lite',
            contents=f"Translate this update changelog into {target}. Keep it natural and concise: {text}"
        )
        return response.text.strip()
    except Exception:
        return text

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
    version_file = "last_commit.txt"
    last_commit = ""
    
    if os.path.exists(version_file):
        with open(version_file, "r") as f:
            last_commit = f.read().strip()

    print(f"Joriy versiya/commit: {current_commit} | Fayldagi eskisi: {last_commit}")

    # Agar versiyalar har xil bo'lsa
    if current_commit != last_commit:
        user_ids = get_all_user_ids()
        if not user_ids:
            print("Foydalanuvchilar topilmadi.")
            return

        raw_commit_msg = get_commit_message()
        translated_cache = {}
        
        print(f"Xabar yuborilmoqda: {len(user_ids)} ta foydalanuvchiga...")
        
        for user_id in user_ids:
            lang = get_user_lang(user_id) or "uz"
            
            if lang not in translated_cache:
                translated_cache[lang] = translate_text(raw_commit_msg, lang)
            
            localized_commit_msg = translated_cache[lang]
            
            raw_template = i18n.t("bot_updated", lang=lang, file="message")
            footer_text = i18n.t("feedback_footer", lang=lang, file="message")
            update_text = raw_template.format(commit_message=localized_commit_msg) + footer_text

            try:
                await client.send_message(user_id, update_text)
                await asyncio.sleep(0.05) 
            except Exception as e:
                print(f"Xatolik userlarga yuborishda: {e}")

        # Yangi versiyani yozib qo'yamiz
        with open(version_file, "w") as f:
            f.write(current_commit)
        print("Barcha foydalanuvchilarga yangilik yuborildi!")
    else:
        print("Yangi versiya aniqlanmadi, xabar yuborilmadi.")