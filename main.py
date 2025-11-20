import asyncio
import logging
import os
import json
from pathlib import Path
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from aiogram.filters import Command, CommandStart
from aiogram.types import FSInputFile

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("Check .env")

logging.basicConfig(level=logging.INFO)

def load_texts_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    # на всякий случай убеждаемся, что это dict со строками
    return {str(k): str(v) for k, v in data.items()}

TEXTS = load_texts_json(BASE_DIR / "texts.json")

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        TEXTS["start"].format(name=message.from_user.first_name)
    )

@router.message(Command("about"))
async def cmd_start(message: Message):
    await message.answer(
        TEXTS["about"]
    )

@router.message(Command("guid"))
async def cmd_guid(message: Message):
    await message.answer(
        TEXTS["guid"]
    )
    pdf_path = BASE_DIR / "pro_rost.pdf"
    if pdf_path.exists():
        await message.answer_document(FSInputFile(pdf_path))
    else:
        await message.answer("File not found.")

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
