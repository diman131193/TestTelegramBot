import asyncio
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message
from aiogram.enums import ParseMode
import logging
import os
from dotenv import load_dotenv
load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")

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