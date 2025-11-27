import asyncio
import logging
import os
import json
import aiosqlite
import re
from pathlib import Path
from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from datetime import datetime, timezone
from aiogram.filters import Command
from aiogram.types import (
    Message, FSInputFile, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
)

BASE_DIR = Path(__file__).resolve().parent

TEXTS_PATH = BASE_DIR / "texts.json"
FILES_PATH = BASE_DIR / "files.json"
ENV_PATH = BASE_DIR / ".env"
DB_PATH = BASE_DIR / "contacts.db"

ADMIN_CHAT_ID = 982065213
ADMIN_CHATS: set[int] = set()

# разделы
START = "start"
CLIENT = "client"
MASTER = "master"
SERVICES = "services"
KERATIN = "keratin"
BOTOX = "botox"
NANOPLASTICS = "nanoplastics"
PRICE = "price"
REVIEWS = "reviews"
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
    return {str(k): v for k, v in data.items()}


TEXTS = load_json(TEXTS_PATH)
FILES = load_json(FILES_PATH)


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        # await db.execute("""DROP TABLE IF EXISTS users;""")
        # await db.commit()
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            username TEXT,
            phone_number TEXT,
            is_bot INTEGER,
            language_code TEXT,
            last_activity_at TEXT,
            command TEXT
        );
        """)
        await db.commit()


async def log_user(chat_id: int,
                   user,
                   command: str = None,
                   phone_number: str = None):
    if user is None:
        return

    now = datetime.now(timezone.utc).isoformat()

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT chat_id, phone_number FROM users WHERE chat_id = ?",
            (chat_id,)
        )
        row = await cursor.fetchone()

        if row is not None and phone_number is None:
            _, existing_phone = row
            phone_number = existing_phone

        if row is None:
            # Вставка нового пользователя
            await db.execute(
                """
                INSERT INTO users (
                    chat_id, first_name, last_name, username, 
                    phone_number, is_bot, language_code,
                    last_activity_at, command
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    chat_id,
                    user.first_name,
                    user.last_name,
                    user.username,
                    phone_number,
                    int(user.is_bot),
                    user.language_code,
                    now,
                    command,
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
                    last_activity_at = ?,
                    command = ?
                WHERE chat_id = ?
                """,
                (
                    user.first_name,
                    user.last_name,
                    user.username,
                    phone_number,
                    int(user.is_bot),
                    user.language_code,
                    now,
                    command,
                    chat_id,
                )
            )

        await db.commit()


MASTER_BUTTON = InlineKeyboardButton(
    text=TEXTS[f"button_{MASTER}"],
    callback_data=MASTER
)

CLIENTS_BUTTON = InlineKeyboardButton(
    text=TEXTS[f"button_{CLIENT}"],
    callback_data=CLIENT
)

SERVICES_BUTTON = InlineKeyboardButton(
    text=TEXTS[f"button_{SERVICES}"],
    callback_data=SERVICES
)

PRICE_BUTTON = InlineKeyboardButton(
    text=TEXTS[f"button_{PRICE}"],
    callback_data=PRICE
)

REVIEWS_BUTTON = InlineKeyboardButton(
    text=TEXTS[f"button_{REVIEWS}"],
    callback_data=REVIEWS
)

SIGNING_BUTTON = InlineKeyboardButton(
    text=TEXTS[f"button_{SIGNING}"],
    url="https://dikidi.ru/1723277"
)

CONSULTING_BUTTON = InlineKeyboardButton(
    text=TEXTS[f"button_{CONSULTING}"],
    callback_data=CONSULTING
)

RETURN_CLIENT_BUTTON = InlineKeyboardButton(
    text=TEXTS[f"button_return_{CLIENT}"],
    callback_data=CLIENT
)

KERATIN_BUTTON = InlineKeyboardButton(
    text=TEXTS[f"button_{KERATIN}"],
    callback_data=KERATIN
)

BOTOX_BUTTON = InlineKeyboardButton(
    text=TEXTS[f"button_{BOTOX}"],
    callback_data=BOTOX
)

NANOPLASTICS_BUTTON = InlineKeyboardButton(
    text=TEXTS[f"button_{NANOPLASTICS}"],
    callback_data=NANOPLASTICS
)

router = Router()


@router.message(Command(START))
async def command_start(message: Message):
    ADMIN_CHATS.discard(message.chat.id)
    await log_user(message.chat.id, message.from_user, START)
    await message.answer_photo(
        FILES[START],
        caption=TEXTS[START],
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=
            [
                [MASTER_BUTTON, CLIENTS_BUTTON, ],
            ]
        )
    )


@router.callback_query(F.data == CLIENT)
async def callback_menu_client(callback: CallbackQuery):
    ADMIN_CHATS.discard(callback.message.chat.id)
    await log_user(callback.message.chat.id, callback.from_user, CLIENT)
    await callback.message.answer_photo(
        FILES[CLIENT],
        caption=TEXTS[CLIENT].format(name=callback.from_user.first_name),
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=
            [
                [SERVICES_BUTTON, ],
                [PRICE_BUTTON, REVIEWS_BUTTON, ],
                [SIGNING_BUTTON, CONSULTING_BUTTON, ],
            ]
        )
    )


@router.callback_query(F.data == SERVICES)
async def callback_menu_price(callback: CallbackQuery):
    ADMIN_CHATS.discard(callback.message.chat.id)
    await log_user(callback.message.chat.id, callback.from_user, SERVICES)
    await callback.message.answer_photo(
        FILES[SERVICES],
        caption=TEXTS[SERVICES],
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=
            [
                [KERATIN_BUTTON, ],
                [BOTOX_BUTTON, ],
                [NANOPLASTICS_BUTTON, ],
            ]
        )
    )


@router.callback_query(F.data == KERATIN)
async def callback_keratin(callback: CallbackQuery):
    ADMIN_CHATS.discard(callback.message.chat.id)
    await log_user(callback.message.chat.id, callback.from_user, KERATIN)
    await callback.message.answer_photo(
        FILES[KERATIN],
        caption=TEXTS[KERATIN],
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=
            [
                [PRICE_BUTTON, REVIEWS_BUTTON, ],
                [SIGNING_BUTTON, CONSULTING_BUTTON, ],
                [RETURN_CLIENT_BUTTON, ],
            ]
        )
    )


@router.callback_query(F.data == BOTOX)
async def callback_botox(callback: CallbackQuery):
    ADMIN_CHATS.discard(callback.message.chat.id)
    await log_user(callback.message.chat.id, callback.from_user, BOTOX)
    await callback.message.answer_photo(
        FILES[BOTOX],
        caption=TEXTS[BOTOX],
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=
            [
                [PRICE_BUTTON, REVIEWS_BUTTON, ],
                [SIGNING_BUTTON, CONSULTING_BUTTON, ],
                [RETURN_CLIENT_BUTTON, ],
            ]
        )
    )


@router.callback_query(F.data == CONSULTING)
async def callback_consulting(callback: CallbackQuery):
    ADMIN_CHATS.add(callback.message.chat.id)
    await log_user(callback.message.chat.id, callback.from_user, CONSULTING)
    await callback.message.answer(
        TEXTS[CONSULTING],
        parse_mode=ParseMode.HTML
    )


async def get_reviews(message: Message):
    ADMIN_CHATS.discard(message.chat.id)
    intro = TEXTS[REVIEWS]
    photo_ids = FILES[REVIEWS]

    if not photo_ids:
        await message.answer(intro, parse_mode=ParseMode.HTML)
        return

    media = [
        InputMediaPhoto(media=pid)
        for pid in photo_ids
    ]

    await message.answer_media_group(media)

    await message.answer(
        intro,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=
            [
                [SIGNING_BUTTON, ]
            ]
        )
    )


@router.callback_query(F.data == REVIEWS)
async def callback_reviews(callback: CallbackQuery):
    await log_user(callback.message.chat.id, callback.from_user, REVIEWS)
    await get_reviews(callback.message)


@router.message(Command(REVIEWS))
async def command_review(message: Message):
    await log_user(message.chat.id, message.from_user, REVIEWS)
    await get_reviews(message)


@router.callback_query(F.data == MASTER)
async def callback_menu_master(callback: CallbackQuery):
    ADMIN_CHATS.discard(callback.message.chat.id)
    await log_user(callback.message.chat.id, callback.from_user, MASTER)
    await callback.message.answer(
        TEXTS[MASTER],
        parse_mode=ParseMode.HTML,
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
async def cmd_load(message: Message):
    sent = await message.answer_photo(
        FSInputFile(BASE_DIR / "IMG_2355.jpg")
    )
    if sent.photo:
        print(sent.photo.pop().file_id)


@router.message(F.chat.id == ADMIN_CHAT_ID, F.reply_to_message)
async def admin_reply(message: Message, bot: Bot):
    original = message.reply_to_message
    if not original or not original.text:
        return

    match = re.search(r"ID:\s*(\d+)", original.text)
    if not match:
        return

    client_chat_id = int(match.group(1))

    await bot.send_message(
        client_chat_id,
        message.text
    )


@router.message(F.text & ~F.text.startswith("/"))
async def handle_message(message: Message, bot: Bot):
    if message.chat.id not in ADMIN_CHATS:
        return

    user = message.from_user
    username = f"@{user.username}" if user.username else "—"

    admin_text = (
        "📩 <b>Новое сообщение для консультации</b>\n\n"
        f"<b>От:</b> {user.first_name or ''} {user.last_name or ''} ({username})\n"
        f"<b>ID:</b> {message.chat.id}\n\n"
        f"{message.text}"
    )

    await bot.send_message(
        ADMIN_CHAT_ID,
        admin_text,
        parse_mode=ParseMode.HTML
    )

    await message.answer(
        "Отправила твой вопрос мастеру 💛\n"
        "Она ответит сюда в чат в ближайшее время."
    )


@router.message(F.text)
async def echo_handler(message: Message):
    await log_user(message.chat.id, message.from_user)
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
