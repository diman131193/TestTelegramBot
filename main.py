import asyncio
import logging
from aiogram import Bot, Dispatcher
import app.db as db
from app.config import get_bot_token
from app.handlers import router as main_router
from app.handlers_test import router as test_router

logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(token=get_bot_token())
    dp = Dispatcher()
    dp.include_router(test_router)
    dp.include_router(main_router)
    await db.init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
