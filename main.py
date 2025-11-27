import asyncio
import logging
import os
import json
import re
from pathlib import Path
from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from aiogram.filters import Command
from aiogram.types import (
    Message, FSInputFile, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
)
import app.constants as const
import app.db as db

BASE_DIR = Path(__file__).resolve().parent

TEXTS_PATH = BASE_DIR / "texts.json"
FILES_PATH = BASE_DIR / "files.json"
ENV_PATH = BASE_DIR / ".env"

ADMIN_CHATS: set[int] = set()

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

MASTER_BUTTON = InlineKeyboardButton(
    text=TEXTS[f"button_{const.MASTER}"],
    callback_data=const.MASTER
)

CLIENTS_BUTTON = InlineKeyboardButton(
    text=TEXTS[f"button_{const.CLIENT}"],
    callback_data=const.CLIENT
)

SERVICES_BUTTON = InlineKeyboardButton(
    text=TEXTS[f"button_{const.SERVICES}"],
    callback_data=const.SERVICES
)

PRICE_BUTTON = InlineKeyboardButton(
    text=TEXTS[f"button_{const.PRICE}"],
    callback_data=const.PRICE
)

REVIEWS_BUTTON = InlineKeyboardButton(
    text=TEXTS[f"button_{const.REVIEWS}"],
    callback_data=const.REVIEWS
)

SIGNING_BUTTON = InlineKeyboardButton(
    text=TEXTS[f"button_{const.SIGNING}"],
    url="https://dikidi.ru/1723277"
)

CONSULTING_BUTTON = InlineKeyboardButton(
    text=TEXTS[f"button_{const.CONSULTING}"],
    callback_data=const.CONSULTING
)

RETURN_CLIENT_BUTTON = InlineKeyboardButton(
    text=TEXTS[f"button_return_{const.CLIENT}"],
    callback_data=const.CLIENT
)

KERATIN_BUTTON = InlineKeyboardButton(
    text=TEXTS[f"button_{const.KERATIN}"],
    callback_data=const.KERATIN
)

BOTOX_BUTTON = InlineKeyboardButton(
    text=TEXTS[f"button_{const.BOTOX}"],
    callback_data=const.BOTOX
)

NANOPLASTICS_BUTTON = InlineKeyboardButton(
    text=TEXTS[f"button_{const.NANOPLASTIC}"],
    callback_data=const.NANOPLASTIC
)

router = Router()


@router.message(Command(const.START))
async def command_start(message: Message):
    ADMIN_CHATS.discard(message.chat.id)
    await db.log_user(message.chat.id, message.from_user, const.START)
    await message.answer_photo(
        FILES[const.START],
        caption=TEXTS[const.START],
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=
            [
                [MASTER_BUTTON, CLIENTS_BUTTON, ],
            ]
        )
    )


@router.callback_query(F.data == const.CLIENT)
async def callback_menu_client(callback: CallbackQuery):
    ADMIN_CHATS.discard(callback.message.chat.id)
    await db.log_user(callback.message.chat.id, callback.from_user, const.CLIENT)
    await callback.message.answer_photo(
        FILES[const.CLIENT],
        caption=TEXTS[const.CLIENT].format(name=callback.from_user.first_name),
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


@router.callback_query(F.data == const.SERVICES)
async def callback_menu_price(callback: CallbackQuery):
    ADMIN_CHATS.discard(callback.message.chat.id)
    await db.log_user(callback.message.chat.id, callback.from_user, const.SERVICES)
    await callback.message.answer_photo(
        FILES[const.SERVICES],
        caption=TEXTS[const.SERVICES],
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


@router.callback_query(F.data == const.KERATIN)
async def callback_keratin(callback: CallbackQuery):
    ADMIN_CHATS.discard(callback.message.chat.id)
    await db.log_user(callback.message.chat.id, callback.from_user, const.KERATIN)
    await callback.message.answer_photo(
        FILES[const.KERATIN],
        caption=TEXTS[const.KERATIN],
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


@router.callback_query(F.data == const.BOTOX)
async def callback_botox(callback: CallbackQuery):
    ADMIN_CHATS.discard(callback.message.chat.id)
    await db.log_user(callback.message.chat.id, callback.from_user, const.BOTOX)
    await callback.message.answer_photo(
        FILES[const.BOTOX],
        caption=TEXTS[const.BOTOX],
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


@router.callback_query(F.data == const.NANOPLASTIC)
async def callback_botox(callback: CallbackQuery):
    ADMIN_CHATS.discard(callback.message.chat.id)
    await db.log_user(callback.message.chat.id, callback.from_user, const.NANOPLASTIC)
    await callback.message.answer_photo(
        FILES[const.NANOPLASTIC],
        caption=TEXTS[const.NANOPLASTIC],
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


@router.callback_query(F.data == const.CONSULTING)
async def callback_consulting(callback: CallbackQuery):
    ADMIN_CHATS.add(callback.message.chat.id)
    await db.log_user(callback.message.chat.id, callback.from_user, const.CONSULTING)
    await callback.message.answer(
        TEXTS[const.CONSULTING],
        parse_mode=ParseMode.HTML
    )


async def get_reviews(message: Message):
    ADMIN_CHATS.discard(message.chat.id)
    intro = TEXTS[const.REVIEWS]
    photo_ids = FILES[const.REVIEWS]

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


@router.callback_query(F.data == const.REVIEWS)
async def callback_reviews(callback: CallbackQuery):
    await db.log_user(callback.message.chat.id, callback.from_user, const.REVIEWS)
    await get_reviews(callback.message)


@router.message(Command(const.REVIEWS))
async def command_review(message: Message):
    await db.log_user(message.chat.id, message.from_user, const.REVIEWS)
    await get_reviews(message)


@router.callback_query(F.data == const.MASTER)
async def callback_menu_master(callback: CallbackQuery):
    ADMIN_CHATS.discard(callback.message.chat.id)
    await db.log_user(callback.message.chat.id, callback.from_user, const.MASTER)
    await callback.message.answer(
        TEXTS[const.MASTER],
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
        FSInputFile(BASE_DIR / "IMG_2358.jpg")
    )
    if sent.photo:
        print(sent.photo.pop().file_id)


@router.message(F.chat.id == const.ADMIN_CHAT_ID, F.reply_to_message)
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
        const.ADMIN_CHAT_ID,
        admin_text,
        parse_mode=ParseMode.HTML
    )

    await message.answer(
        "Отправила твой вопрос мастеру 💛\n"
        "Она ответит сюда в чат в ближайшее время."
    )


@router.message(F.text)
async def echo_handler(message: Message):
    await db.log_user(message.chat.id, message.from_user)
    await message.answer(
        f"Некорректная команда: <b>{message.text}</b>",
        parse_mode=ParseMode.HTML
    )


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await db.init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
