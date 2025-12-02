import re

from aiogram import Router, F, Bot
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import (
    Message,
    FSInputFile,
    CallbackQuery,
    InputMediaPhoto,
)

import app.const as const
import app.db as db
from app.texts import text, file, files
import app.keyboards as keyboards
from app.paths import DATA_DIR

router = Router()

ADMIN_CHATS: set[int] = set()


@router.message(Command(const.START))
async def command_start(message: Message):
    ADMIN_CHATS.discard(message.chat.id)
    await db.log_user(message.chat.id, message.from_user, const.START)
    await message.answer_photo(
        file(const.START),
        caption=text(const.START),
        parse_mode=ParseMode.HTML,
        reply_markup=keyboards.start_keyboard()
    )


@router.callback_query(F.data == const.CLIENT)
async def callback_menu_client(callback: CallbackQuery):
    ADMIN_CHATS.discard(callback.message.chat.id)
    await db.log_user(callback.message.chat.id, callback.from_user, const.CLIENT)
    await callback.message.answer_photo(
        file(const.CLIENT),
        caption=text(const.CLIENT).format(name=callback.from_user.first_name),
        parse_mode=ParseMode.HTML,
        reply_markup=keyboards.client_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == const.SERVICES)
async def callback_menu_price(callback: CallbackQuery):
    ADMIN_CHATS.discard(callback.message.chat.id)
    await db.log_user(callback.message.chat.id, callback.from_user, const.SERVICES)
    await callback.message.answer_photo(
        file(const.SERVICES),
        caption=text(const.SERVICES),
        parse_mode=ParseMode.HTML,
        reply_markup=keyboards.services_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == const.KERATIN)
async def callback_keratin(callback: CallbackQuery):
    ADMIN_CHATS.discard(callback.message.chat.id)
    await db.log_user(callback.message.chat.id, callback.from_user, const.KERATIN)
    await callback.message.answer_photo(
        file(const.KERATIN),
        caption=text(const.KERATIN),
        parse_mode=ParseMode.HTML,
        reply_markup=keyboards.services_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == const.BOTOX)
async def callback_botox(callback: CallbackQuery):
    ADMIN_CHATS.discard(callback.message.chat.id)
    await db.log_user(callback.message.chat.id, callback.from_user, const.BOTOX)
    await callback.message.answer_photo(
        file(const.BOTOX),
        caption=text(const.BOTOX),
        parse_mode=ParseMode.HTML,
        reply_markup=keyboards.services_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == const.NANOPLASTIC)
async def callback_botox(callback: CallbackQuery):
    ADMIN_CHATS.discard(callback.message.chat.id)
    await db.log_user(callback.message.chat.id, callback.from_user, const.NANOPLASTIC)
    await callback.message.answer_photo(
        file(const.NANOPLASTIC),
        caption=text(const.NANOPLASTIC),
        parse_mode=ParseMode.HTML,
        reply_markup=keyboards.services_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == const.CONSULTING)
async def callback_consulting(callback: CallbackQuery):
    ADMIN_CHATS.add(callback.message.chat.id)
    await db.log_user(callback.message.chat.id, callback.from_user, const.CONSULTING)
    await callback.message.answer(
        text(const.CONSULTING),
        parse_mode=ParseMode.HTML
    )
    await callback.answer()


async def get_reviews(message: Message):
    ADMIN_CHATS.discard(message.chat.id)
    intro = text(const.REVIEWS)
    photo_ids = files(const.REVIEWS)

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
        reply_markup=keyboards.reviews_keyboard()
    )


@router.callback_query(F.data == const.REVIEWS)
async def callback_reviews(callback: CallbackQuery):
    await db.log_user(callback.message.chat.id, callback.from_user, const.REVIEWS)
    await get_reviews(callback.message)
    await callback.answer()


@router.message(Command(const.REVIEWS))
async def command_review(message: Message):
    await db.log_user(message.chat.id, message.from_user, const.REVIEWS)
    await get_reviews(message)


@router.callback_query(F.data == const.MASTER)
async def callback_menu_master(callback: CallbackQuery):
    ADMIN_CHATS.discard(callback.message.chat.id)
    await db.log_user(callback.message.chat.id, callback.from_user, const.MASTER)
    await callback.message.answer(
        text(const.MASTER),
        parse_mode=ParseMode.HTML,
    )
    await callback.answer()


# @router.message(Command("guid"))
# async def cmd_guid(message: Message):
#     await log_user(message)
#     caption = text("guid")
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
        FSInputFile(DATA_DIR / "IMG_2358.jpg")
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
async def text_handler(message: Message):
    await db.log_user(message.chat.id, message.from_user)
    await message.answer(
        f"Некорректная команда: <b>{message.text}</b>",
        parse_mode=ParseMode.HTML
    )
