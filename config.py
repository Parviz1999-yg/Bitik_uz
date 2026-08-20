import os

# Railway (environment variables) yoki lokal fayldan o'qish uchun sozlama
API_ID = int(os.environ.get("API_ID", "37008810"))
API_HASH = os.environ.get("API_HASH","c262f78bbc578d7da99804e07a63d3eb")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8871335143:AAE51_ldUuTH9RktjmuJsjPPMJHawiH8UaU")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "7762152444"))

# Click to'lov tizimi ma'lumotlari (agar ishlatilsa)
CLICK_PROVIDER_TOKEN = os.environ.get("CLICK_PROVIDER_TOKEN", "333605228:LIVE:63513_06FAAA4E4E9415D0C0F268352C64DE3794A83C39")
CLICK_MERCHANT_ID = os.environ.get("CLICK_MERCHANT_ID", "63513")
CLICK_SERVICE_ID = os.environ.get("CLICK_SERVICE_ID", "109740")
CLICK_MERCHANT_USER_ID = os.environ.get("CLICK_MERCHANT_USER_ID", "89673")
CLICK_SECRET_KEY = os.environ.get("CLICK_SECRET_KEY", "URpDCldg49")   

#gemini key
GEMINI_KEY = os.environ.get("GEMINI_KEY")               