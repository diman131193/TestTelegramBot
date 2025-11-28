import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import app.db as db
import app.handlers as handlers
from app.paths import BASE_DIR

ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)

BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(handlers.router)
    await db.init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
