from pyrogram import idle
from bot import bitik
from database.db import init_db
import handlers  # noqa: F401 — barcha handlerlar
import callbacks  # noqa: F401 — barcha callbacklar
import services.update_service


async def main():
    print("Baza tekshirilmoqda....")
    init_db()

    print("Bot ishga tushmoqda...")
    await bitik.start()

    print("Yangiliklar tekshirilmoqda...")
    try:
        await services.update_service.check_and_notify_users(bitik)
    except Exception as e:
        print(f"Update service xatosi: {e}")

    print("Bot muvaffaqiyatli ishga tushdi va ishlamoqda...")
    await idle()
    await bitik.stop()


if __name__ == "__main__":
    bitik.run(main())
