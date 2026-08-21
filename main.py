import asyncio
from bot import bitik

import handlers.start
import handlers.language
import handlers.cv2_handler
import handlers.cv_handler
import handlers.photo2_handler
import handlers.photo_handler
import handlers.ai_handler
import handlers.balans_handler
import handlers.admin_handler
import handlers.help_handler

import handlers.webhook_handler

import callbacks.language_cv_cb
import callbacks.language_cv2_cb
import callbacks.sub_cb
import callbacks.format_cb
import callbacks.format2_cb
import callbacks.cv_xato_cb
import callbacks.cv2_xato_cb
import callbacks.cv_davom_cb
import callbacks.cv2_davom_cb
from database.db import init_db

import services.update_service

import handlers.payment_handler


if __name__ == "__main__":
    print("Baza tekshirilmoqda...")
    init_db()

    print("bot ishga tushdi....")
    
    try:
        bitik.run()
    except Exception as e:
        print(f"Botni ishga tushirishda xatolik: {e}")