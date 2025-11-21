import asyncio
import logging
import os
import json
import aiosqlite
from pathlib import Path
from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from datetime import datetime, timezone
from aiogram.filters import Command
from aiogram.types import (
    Message, FSInputFile, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
)

BASE_DIR = Path(__file__).resolve().parent

ABOUT_PDF_FILE_ID = "BQACAgIAAxkDAANGaSBTOcj-qIIW4H7OjXAr1xpTvAcAAqaMAAK5gghJ4FX5P5-pbJk2BA"

load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

def get_menu_inline_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Записаться",
                url="https://dikidi.ru/1723277"
            ),
            InlineKeyboardButton(
                text="Портфолио",
                url="https://instagram.com/ТВОЙ_INSTAGRAM"
            ),
        ],
        [
            InlineKeyboardButton(
                text="Прайс",
                callback_data="price"
            ),
            InlineKeyboardButton(
                text="Уход",
                callback_data="care"
            ),
        ],
        [
            InlineKeyboardButton(
                text="Контакты",
                callback_data="contacts"
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def load_texts_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    return {str(k): str(v) for k, v in data.items()}

TEXTS = load_texts_json(BASE_DIR / "texts.json")

async def menu_price(message: Message):
    await message.answer(TEXTS["about"])

DB_PATH = BASE_DIR / "contacts.db"
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            username TEXT,
            is_bot INTEGER,
            language_code TEXT,
            last_activity_at TEXT
        );
        """)
        await db.commit()


async def log_user(message: Message):
    user = message.from_user
    if user is None:
        return

    now = datetime.now(timezone.utc).isoformat()

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT chat_id FROM users WHERE chat_id = ?",
            (message.chat.id,)
        )
        row = await cursor.fetchone()

        if row is None:
            # Вставка нового пользователя
            await db.execute(
                """
                INSERT INTO users (
                    chat_id, first_name, last_name, username, 
                    is_bot, language_code,
                    last_activity_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    message.chat.id,
                    user.first_name,
                    user.last_name,
                    user.username,
                    int(user.is_bot),
                    user.language_code,
                    now,
                )
            )
        else:
            # Обновление существующего
            await db.execute(
                """
                UPDATE users
                SET
                    first_name = ?,
                    last_name = ?,
                    username = ?,
                    is_bot = ?,
                    language_code = ?,
                    last_activity_at = ?
                WHERE chat_id = ?
                """,
                (
                    user.first_name,
                    user.last_name,
                    user.username,
                    int(user.is_bot),
                    user.language_code,
                    now,
                    message.chat.id,
                )
            )

        await db.commit()



router = Router()

@router.message(Command("menu"))
async def cmd_menu(message: Message):
    await log_user(message)
    await message.answer(
        TEXTS["menu"],
        reply_markup=get_menu_inline_keyboard()
    )

@router.callback_query(F.data == "price")
async def cb_menu_price(callback: CallbackQuery):
    await log_user(callback.message)
    await menu_price(callback.message)
    await callback.answer()

@router.message(Command("price"))
async def cmd_menu_price(message: Message):
    await log_user(message)
    await menu_price(message)

@router.message(Command("guid"))
async def cmd_guid(message: Message):
    await log_user(message)
    caption = TEXTS["guid"]
    sent = await message.answer_document(
        ABOUT_PDF_FILE_ID,
        caption=caption
    )
    if not sent.document:
        pdf_path = BASE_DIR / "pro_rost.pdf"
        if pdf_path.exists():
            await message.answer_document(FSInputFile(pdf_path), caption=caption)

@router.message(F.text)
async def echo_handler(message: Message):
    await log_user(message)
    await message.answer(
        f"Ты написал: <b>{message.text}</b>",
        parse_mode=ParseMode.HTML
    )

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
