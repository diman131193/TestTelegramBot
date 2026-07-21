from __future__ import annotations

from typing import Dict, Any

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
from app.diagnostics import build_recommendation
from app.texts import load_test_config, button
import app.keyboards as keyboards
from app.handlers import ADMIN_CHATS

router = Router()

TEST_PROGRESS: Dict[int, Any] = {}


async def get_progress(chat_id: int) -> dict[str, Any] | None:
    progress = TEST_PROGRESS.get(chat_id)
    if progress is not None:
        return progress
    progress = await db.load_diagnostic_session(chat_id)
    if progress is not None:
        TEST_PROGRESS[chat_id] = progress
    return progress


async def save_progress(chat_id: int, progress: dict[str, Any]):
    TEST_PROGRESS[chat_id] = progress
    await db.save_diagnostic_session(
        chat_id,
        progress.get("answers", []),
        progress.get("question_id", ""),
    )


async def clear_progress(chat_id: int):
    TEST_PROGRESS.pop(chat_id, None)
    await db.delete_diagnostic_session(chat_id)


async def send_test_question(message: Message, chat_id: int, question_id: str):
    test_config = load_test_config()
    test_questions = test_config.get("questions", {})
    test_start = test_config.get("start")
    if not test_start or not test_questions or not question_id:
        await message.answer(
            "Тест временно недоступен — вопросы не найдены 🕊",
            parse_mode=ParseMode.HTML,
        )
        return

    question = test_questions.get(question_id)

    if not question:
        # если по какой-то причине вопрос не найден — сразу уходим в результат по path
        await send_test_result(message, chat_id)
        return

    options = question.get("options", [])
    if not options:
        await send_test_result(message, chat_id)
        return

    progress = await get_progress(chat_id) or {"answers": []}
    progress["question_id"] = question_id
    await save_progress(chat_id, progress)

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
    progress = await get_progress(chat_id)
    answers = progress["answers"] if progress else []

    await message.answer(
        build_recommendation(answers),
        parse_mode=ParseMode.HTML,
        reply_markup=keyboards.client_keyboard(),
    )
    await clear_progress(chat_id)


@router.callback_query(F.data == const.TEST)
async def callback_test_start(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    ADMIN_CHATS.discard(chat_id)
    await db.log_user(chat_id, callback.from_user, const.TEST)

    test_start = load_test_config().get("start")
    await save_progress(chat_id, {"answers": [], "question_id": test_start or ""})
    await send_test_question(callback.message, chat_id, test_start)
    await callback.answer()


@router.message(F.text == button(const.TEST), ~F.reply_to_message)
async def message_test_start(message: Message):
    chat_id = message.chat.id
    ADMIN_CHATS.discard(chat_id)
    await db.log_user(chat_id, message.from_user, const.TEST)

    test_start = load_test_config().get("start")
    await save_progress(chat_id, {"answers": [], "question_id": test_start or ""})
    await send_test_question(message, chat_id, test_start)


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

    _, answer_id, callback_next_question_id = parts

    chat_id = callback.message.chat.id

    # проверяем и обновляем прогресс
    progress = await get_progress(chat_id)
    if progress is None:
        test_start = load_test_config().get("start")
        await save_progress(chat_id, {"answers": [], "question_id": test_start or ""})
        await send_test_question(callback.message, chat_id, test_start)
        await callback.answer(
            "Предыдущее прохождение завершено. Я начала диагностику заново.",
            show_alert=True,
        )
        return

    test_config = load_test_config()
    questions = test_config.get("questions", {})
    question_id = progress.get("question_id")
    question = questions.get(question_id, {})
    option = next(
        (item for item in question.get("options", []) if item.get("id") == answer_id),
        None,
    )
    if option is None:
        await callback.answer("Этот ответ уже неактуален.", show_alert=True)
        return

    next_question_id = option.get("next")
    if callback_next_question_id != next_question_id:
        await callback.answer("Кнопка устарела. Начни диагностику заново.", show_alert=True)
        return

    progress["answers"].append(answer_id)
    progress["answers"] = list(dict.fromkeys(progress["answers"]))

    if next_question_id == "advice":
        progress["question_id"] = "__finishing__"
        await save_progress(chat_id, progress)
        await send_test_result(callback.message, chat_id)
    elif next_question_id and next_question_id in questions:
        progress["question_id"] = next_question_id
        await save_progress(chat_id, progress)
        await send_test_question(callback.message, chat_id, next_question_id)
    else:
        await save_progress(chat_id, progress)
        await send_test_result(callback.message, chat_id)

    await callback.answer()
