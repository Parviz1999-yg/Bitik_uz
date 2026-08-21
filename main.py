import asyncio
from pyrogram import idle
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


async def main():
    print("Baza tekshirilmoqda...")
    init_db()

    print("Bot ishga tushmoqda...")
    # Python 3.13 va Pyrogram uchun xavfsiz ulanish
    await bitik.start()
    
    print("Yangiliklar tekshirilmoqda va foydalanuvchilarga xabar yuborilmoqda...")
    try:
        await services.update_service.check_and_notify_users(bitik)
    except Exception as e:
        print(f"Update service xatosi: {e}")

    print("Bot muvaffaqiyatli ishga tushdi va ishlamoqda...")
    await idle()
    await bitik.stop()

if __name__ == "__main__":
    bitik.run(main())