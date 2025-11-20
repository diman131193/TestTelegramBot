import asyncio
import logging
import os
from pathlib import Path

from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message
from aiogram.enums import ParseMode
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
	raise RuntimeError("Check .env")

logging.basicConfig(level=logging.INFO)

router = Router()

@router.message(F.text == "/start")
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я простой эхо-бот на aiogram 🤖\nНапиши мне что-нибудь."
    )

@router.message(F.text)
async def echo_handler(message: Message):
    await message.answer(
        f"Ты написал: <b>{message.text}</b>",
        parse_mode=ParseMode.HTML
    )

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
