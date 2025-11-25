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

TEXTS_PATH = BASE_DIR / "texts.json"
FILES_PATH = BASE_DIR / "files.json"
ENV_PATH = BASE_DIR / ".env"
DB_PATH = BASE_DIR / "contacts.db"

# разделы
START = "start"
CLIENT = "client"
MASTER = "master"
SERVICES = "services"
KERATIN = "keratin"
BOTOX = "botox"
NANOPLASTICS = "nanoplastics"
PRICE = "price"
COMMENTS = "comments"
SIGNING = "signing"
CONSULTING = "consulting"

load_dotenv(ENV_PATH)

BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    return {str(k): str(v) for k, v in data.items()}


TEXTS = load_json(TEXTS_PATH)
FILES = load_json(FILES_PATH)


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            username TEXT,
            phone_number TEXT,
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
                    phone_number, is_bot, language_code,
                    last_activity_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    message.chat.id,
                    user.first_name,
                    user.last_name,
                    user.username,
                    "",
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
                    phone_number = ?,
                    is_bot = ?,
                    language_code = ?,
                    last_activity_at = ?
                WHERE chat_id = ?
                """,
                (
                    user.first_name,
                    user.last_name,
                    user.username,
                    "",
                    int(user.is_bot),
                    user.language_code,
                    now,
                    message.chat.id,
                )
            )

        await db.commit()


def get_client_services_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text=TEXTS[f"button_{PRICE}"],
                callback_data=PRICE
            ),
            InlineKeyboardButton(
                text=TEXTS[f"button_{COMMENTS}"],
                callback_data=COMMENTS
            ),
        ],
        [
            InlineKeyboardButton(
                text=TEXTS[f"button_{SIGNING}"],
                url="https://dikidi.ru/1723277"
            ),
            InlineKeyboardButton(
                text=TEXTS[f"button_{CONSULTING}"],
                callback_data=CONSULTING
            ),
        ],
        [
            InlineKeyboardButton(
                text=TEXTS[f"button_return_{CLIENT}"],
                callback_data=CLIENT
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


router = Router()


@router.message(Command(START))
async def command_start(message: Message):
    await log_user(message)
    await message.answer_photo(
        FILES[START],
        caption=TEXTS[START],
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=
            [
                [
                    InlineKeyboardButton(
                        text=TEXTS[f"button_{MASTER}"],
                        parse_mode=ParseMode.HTML,
                        callback_data=MASTER
                    ),
                    InlineKeyboardButton(
                        text=TEXTS[f"button_{CLIENT}"],
                        parse_mode=ParseMode.HTML,
                        callback_data=CLIENT
                    ),
                ],
            ]
        )
    )


@router.callback_query(F.data == CLIENT)
async def callback_menu_client(callback: CallbackQuery):
    await log_user(callback.message)
    await callback.message.answer_photo(
        FILES[CLIENT],
        caption=TEXTS[CLIENT].format(name=callback.message.from_user.first_name),
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=
            [
                [
                    InlineKeyboardButton(
                        text=TEXTS[f"button_{SERVICES}"],
                        parse_mode=ParseMode.HTML,
                        callback_data=SERVICES
                    ),
                ],
            ]
        )
    )


@router.callback_query(F.data == SERVICES)
async def cb_menu_price(callback: CallbackQuery):
    await log_user(callback.message)
    await callback.message.answer_photo(
        FILES[SERVICES],
        caption=TEXTS[SERVICES],
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=
            [
                [
                    InlineKeyboardButton(
                        text=TEXTS[f"button_{KERATIN}"],
                        parse_mode=ParseMode.HTML,
                        callback_data=KERATIN
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=TEXTS[f"button_{BOTOX}"],
                        parse_mode=ParseMode.HTML,
                        callback_data=BOTOX
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=TEXTS[f"button_{NANOPLASTICS}"],
                        parse_mode=ParseMode.HTML,
                        callback_data=NANOPLASTICS
                    ),
                ]
            ]
        )
    )


@router.callback_query(F.data == KERATIN)
async def callback_menu_client(callback: CallbackQuery):
    await log_user(callback.message)
    await callback.message.answer_photo(
        FILES[KERATIN],
        caption=TEXTS[KERATIN],
        parse_mode=ParseMode.HTML,
        reply_markup=get_client_services_keyboard()
    )


@router.callback_query(F.data == MASTER)
async def callback_menu_master(callback: CallbackQuery):
    await log_user(callback.message)
    await callback.message.answer(
        TEXTS[MASTER],
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=
            [
                [
                    InlineKeyboardButton(
                        text=TEXTS[f"button_{SERVICES}"],
                        parse_mode=ParseMode.HTML,
                        callback_data=SERVICES
                    ),
                ],
            ]
        )
    )


# @router.message(Command("guid"))
# async def cmd_guid(message: Message):
#     await log_user(message)
#     caption = TEXTS["guid"]
#     sent = await message.answer_document(
#         FILES["about_pdf"],
#         parse_mode=ParseMode.HTML,
#         caption=caption
#     )
#     if not sent.document:
#         pdf_path = BASE_DIR / "pro_rost.pdf"
#         if pdf_path.exists():
#             await message.answer_document(FSInputFile(pdf_path), caption=caption)


@router.message(Command("load"))
async def cmd_guid(message: Message):
    sent = await message.answer_photo(
        FSInputFile(BASE_DIR / "IMG_2287.jpg")
    )
    if sent.photo:
        print(sent.photo.pop().file_id)


@router.message(F.text)
async def echo_handler(message: Message):
    await log_user(message)
    await message.answer(
        f"Некорректная команда: <b>{message.text}</b>",
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
