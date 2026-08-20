import os

# Railway (environment variables) yoki lokal fayldan o'qish uchun sozlama
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))

# Click to'lov tizimi ma'lumotlari (agar ishlatilsa)
CLICK_PROVIDER_TOKEN = os.environ.get("CLICK_PROVIDER_TOKEN")
CLICK_MERCHANT_ID = os.environ.get("CLICK_MERCHANT_ID")
CLICK_SERVICE_ID = os.environ.get("CLICK_SERVICE_ID")
CLICK_MERCHANT_USER_ID = os.environ.get("CLICK_MERCHANT_USER_ID")
CLICK_SECRET_KEY = os.environ.get("CLICK_SECRET_KEY")   

#gemini key
GEMINI_KEY = os.environ.get("GEMINI_KEY")               