"""
bitik.uz — Telegram bot + Click webhook (bitta process).

Railway:
  PORT — HTTP (Click callback)
  Worker buyruq: python main.py
"""
from __future__ import annotations

import asyncio
import os

import uvicorn
from pyrogram import idle

from bot import bitik
from database.db import init_db
import handlers  # noqa: F401
import callbacks  # noqa: F401
from handlers.webhook_handler import app as click_app
import services.update_service


async def main():
    print("Baza tekshirilmoqda...")
    init_db()

    port = int(os.environ.get("PORT", "8000"))
    config = uvicorn.Config(
        click_app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        lifespan="on",
    )
    server = uvicorn.Server(config)

    print(f"Click webhook HTTP :{port} (POST /click/webhook)")
    server_task = asyncio.create_task(server.serve())

    print("Bot ishga tushmoqda...")
    await bitik.start()

    try:
        await services.update_service.check_and_notify_users(bitik)
    except Exception as e:
        print(f"Update service: {e}")

    print("Bot tayyor.")
    try:
        await idle()
    finally:
        server.should_exit = True
        await bitik.stop()
        await server_task


if __name__ == "__main__":
    bitik.run(main())
