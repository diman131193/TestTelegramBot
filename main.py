#!/usr/bin/env python3
"""telegram_bot.py — aiogram‑based hair‑care assistant bot with externalized texts.

Команды:
    /start       – приветствие
    /about       – информация о мастере
    /guid        – PDF‑гайд «PROРОСТ ВОЛОС»
    /questions   – задать вопрос (отправка администратору)
    /faq         – полезные материалы
    /signup      – онлайн‑запись
    /contacts    – ссылки для связи
    /reload_texts – перезагрузить texts.json (только админу)

Запуск:
    BOT_TOKEN="<token>" ADMIN_CHAT_ID="<id>" python telegram_bot.py

Файл `texts.json` (лежит рядом со скриптом) хранит любые текстовые шаблоны.
Пример:
{
  "start": "Привет, {name}! Ты попала в пространство роскошных волос…",
  "questions_prompt": "Ты можешь задать мне любой вопрос в сфере волос 🌷, {name}!",
  "guid_send": "Лови гайд!",
  "file_missing": "Файл не найден. Проверь название или путь.",
  "about_text": "Меня зовут Татьяна, я сертифицированный трихолог…",
  "contacts_text": "Как удобно связаться со мной:"
}

Менять тексты можно без перекомпиляции — достаточно поправить JSON и (при необходимости)
послать команду /reload_texts, чтобы бот перечитал файл без перезапуска.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Final, TypedDict, Any

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup

###############################################################################
# Конфигурация
###############################################################################

BOT_TOKEN: Final[str] = os.getenv("BOT_TOKEN", "")
ADMIN_CHAT_ID: Final[int] = int(os.getenv("ADMIN_CHAT_ID", "0"))

if not BOT_TOKEN or not ADMIN_CHAT_ID:
    raise RuntimeError("Set BOT_TOKEN and ADMIN_CHAT_ID env vars")

ASSETS_DIR: Final[Path] = Path(__file__).with_name("assets")
TEXTS_FILE: Final[Path] = Path(__file__).with_name("texts.json")

###############################################################################
# Загрузка текстов из JSON
###############################################################################

class _Texts(TypedDict, total=False):
    start: str
    questions_prompt: str
    guid_send: str
    file_missing: str
    about_text: str
    contacts_text: str
    faq_intro: str
    faq_more: str
    signup_text: str

_texts: _Texts = {}


def _load_texts() -> None:
    global _texts
    try:
        with TEXTS_FILE.open(encoding="utf-8") as f:
            _texts = json.load(f)
            logging.info("Loaded %d texts from %s", len(_texts), TEXTS_FILE)
    except FileNotFoundError:
        logging.warning("texts.json not found -> using inline fallbacks")
        _texts = {}
    except json.JSONDecodeError as exc:
        logging.error("JSON parse error in %s: %s", TEXTS_FILE, exc)
        _texts = {}


@lru_cache(maxsize=None)
def t(key: str, **kwargs: Any) -> str:
    """Return text by *key* formatted with **kwargs; fallback to key itself."""
    template = _texts.get(key, key)
    try:
        return template.format(**kwargs)
    except Exception as exc:  # noqa: BLE001
        logging.error("Template error for key %s: %s", key, exc)
        return template


###############################################################################
# Бот и роутеры
###############################################################################

bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)
router = Router()
dp = Dispatcher()
dp.include_router(router)

###############################################################################
# Команды
###############################################################################


@router.message(CommandStart())
async def cmd_start(msg: types.Message) -> None:
    await msg.answer(t("start", name=msg.from_user.first_name))


@router.message(Command("questions"))
async def cmd_questions(msg: types.Message) -> None:
    await msg.answer(t("questions_prompt", name=msg.from_user.first_name))
    await bot.send_message(ADMIN_CHAT_ID, "Пришли фото")


@router.message(Command("guid"))
async def cmd_guid(msg: types.Message) -> None:
    await msg.answer(t("guid_send"))
    pdf_path = ASSETS_DIR / "pro_rost.pdf"
    if pdf_path.exists():
        await msg.answer_document(FSInputFile(pdf_path))
    else:
        await msg.answer(t("file_missing"))


@router.message(Command("signup"))
async def cmd_signup(msg: types.Message) -> None:
    markup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Записаться", url="https://dikidi.ru/1723277")]]
    )
    await msg.answer(t("signup_text", default="Онлайн-запись"), reply_markup=markup)


@router.message(Command("faq"))
async def cmd_faq(msg: types.Message) -> None:
    markup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Ещё", callback_data="more_1")]]
    )
    await msg.answer(t("faq_intro", default="Полезные материалы:"), reply_markup=markup)


@router.callback_query(lambda c: c.data == "more_1")
async def cb_more1(cb: types.CallbackQuery) -> None:
    await cb.message.answer(t("faq_more", default="Дополнительная информация"))
    await cb.answer()


@router.message(Command("about"))
async def cmd_about(msg: types.Message) -> None:
    photo_path = ASSETS_DIR / "IMG_5558.jpg"
    if photo_path.exists():
        await msg.answer_photo(FSInputFile(photo_path))
    else:
        await msg.answer(t("file_missing"))
    await msg.answer(t("about_text", default=""))


@router.message(Command("contacts"))
async def cmd_contacts(msg: types.Message) -> None:
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("Канал про уход", url="https://t.me/pro_keratin_msk")],
            [InlineKeyboardButton("Связь TG", url="https://t.me/Tatyana_domaeva")],
            [InlineKeyboardButton("Связь WhatsApp", url="https://wa.me/79536333979")],
            [InlineKeyboardButton("Taplink", url="https://taplink.cc/prokeratin_msk")],
        ]
    )
    await msg.answer(t("contacts_text"), reply_markup=markup)


###############################################################################
# Админ‑команда перезагрузки текстов
###############################################################################

@router.message(Command("reload_texts"))
async def cmd_reload_texts(msg: types.Message) -> None:
    if msg.chat.id != ADMIN_CHAT_ID:
        await msg.answer("Недостаточно прав")
        return
    _load_texts()
    t.cache_clear()  # type: ignore[attr-defined]
    await msg.answer("Тексты перезагружены ✅")


###############################################################################
# Fallback
###############################################################################

@router.message()
async def echo_unknown(msg: types.Message) -> None:
    await msg.answer("Я не совсем понял запрос. Попробуйте команду /help.")


###############################################################################
# Главный запуск
###############################################################################

async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    _load_texts()

    logging.info("Bot started as @%s", (await bot.get_me()).username)
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())