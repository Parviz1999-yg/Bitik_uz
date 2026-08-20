import os

print("Railway'dagi mavjud kalitlar:", list(os.environ.keys()))

# Xavfsiz o'qish (agar bo'sh bo'lsa 0 yoki bo'sh qator oladi)
api_id_val = os.environ.get("API_ID")
API_ID = int(api_id_val) if api_id_val else 0

API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

admin_id_val = os.environ.get("ADMIN_ID")
ADMIN_ID = int(admin_id_val) if admin_id_val else 0

CLICK_PROVIDER_TOKEN = os.environ.get("CLICK_PROVIDER_TOKEN")
CLICK_MERCHANT_ID = os.environ.get("CLICK_MERCHANT_ID")
CLICK_SERVICE_ID = os.environ.get("CLICK_SERVICE_ID")
CLICK_MERCHANT_USER_ID = os.environ.get("CLICK_MERCHANT_USER_ID")
CLICK_SECRET_KEY = os.environ.get("CLICK_SECRET_KEY")

GEMINI_KEY = os.environ.get("GEMINI_KEY", "")