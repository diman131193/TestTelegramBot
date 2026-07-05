from __future__ import annotations

from typing import Dict, Any, List

from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

import app.const as const
import app.db as db
from app.texts import TEXTS, TEST_CONFIG, ADVICES, button
import app.keyboards as keyboards
from app.handlers import ADMIN_CHATS

router = Router()

TEST_PROGRESS: Dict[int, Any] = {}
TEST_RULES = TEST_CONFIG.get("rules", [])
TEST_QUESTIONS = TEST_CONFIG.get("questions", {})
TEST_START = TEST_CONFIG.get("start")


async def send_test_question(message: Message, chat_id: int, question_id: str):
    if not TEST_START or not TEST_QUESTIONS or not question_id:
        await message.answer(
            "Тест временно недоступен — вопросы не найдены 🕊",
            parse_mode=ParseMode.HTML,
        )
        return

    question = TEST_QUESTIONS.get(question_id)

    if not question:
        # если по какой-то причине вопрос не найден — сразу уходим в результат по path
        await send_test_result(message, chat_id)
        return

    options = question.get("options", [])
    if not options:
        await send_test_result(message, chat_id)
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=opt["text"],
                    # callback_data: "test:<answer_id>:<next_question_id>"
                    callback_data=f"{const.TEST}:{opt['id']}:{opt['next']}",
                )
            ]
            for opt in options
        ]
    )

    await message.answer(
        question["text"],
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
    )


async def send_test_result(message: Message, chat_id: int):
    progress = TEST_PROGRESS.get(chat_id)
    answers: List[str] = progress["answers"] if progress else []

    TEST_PROGRESS.pop(chat_id, None)

    advice_key = None

    if answers:
        key = "|".join(answers)
        advice_key = TEST_RULES.get(key)

    if advice_key is None:
        # Если конкретного правила нет — мягкий фолбэк
        text = (
            "Я сохранила твои ответы 💛\n\n"
            "Сейчас у меня нет готового подробного алгоритма именно под такую комбинацию, "
            "но ты можешь написать в консультацию, и я разберу твой случай персонально."
        )
    else:
        text = ADVICES.get(advice_key, "No advices")

    await message.answer(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboards.client_keyboard(),
    )


@router.callback_query(F.data == const.TEST)
async def callback_test_start(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    ADMIN_CHATS.discard(chat_id)
    await db.log_user(chat_id, callback.from_user, const.TEST)

    TEST_PROGRESS[chat_id] = {"answers": []}

    await send_test_question(callback.message, chat_id, TEST_START)
    await callback.answer()


@router.message(F.text == button(const.TEST), ~F.reply_to_message)
async def message_test_start(message: Message):
    chat_id = message.chat.id
    ADMIN_CHATS.discard(chat_id)
    await db.log_user(chat_id, message.from_user, const.TEST)

    TEST_PROGRESS[chat_id] = {"answers": []}

    await send_test_question(message, chat_id, TEST_START)


@router.callback_query(F.data.startswith(f"{const.TEST}:"))
async def callback_test_answer(callback: CallbackQuery):
    """
    Обработка ответов:
    callback_data = "test:<answer_id>:<next_question_id>"
    """
    parts = callback.data.split(":")
    if len(parts) != 3:
        await callback.answer()
        return

    _, answer_id, next_question_id = parts

    chat_id = callback.message.chat.id

    # проверяем и обновляем прогресс
    progress = TEST_PROGRESS.get(chat_id)
    if progress is None:
        # если по какой-то причине состояние потерялось — стартуем заново
        progress = {"answers": []}
        TEST_PROGRESS[chat_id] = progress

    progress["answers"].append(answer_id)

    print(progress["answers"])

    if next_question_id == "advice":
        await send_test_result(callback.message, chat_id)
    elif next_question_id and next_question_id in TEST_QUESTIONS:
        await send_test_question(callback.message, chat_id, next_question_id)
    else:
        await send_test_result(callback.message, chat_id)

    await callback.answer()
