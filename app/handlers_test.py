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
from app.texts import text, TEST_QUESTIONS
import app.keyboards as keyboards
from app.handlers import ADMIN_CHATS  # используем общий сет для консультации

router = Router()

TEST_PROGRESS: Dict[int, Dict[str, Any]] = {}


@router.callback_query(F.data == const.TEST)
async def callback_test(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    ADMIN_CHATS.discard(callback.message.chat.id)
    await db.log_user(callback.message.chat.id, callback.from_user, const.TEST)
    # инициализируем прогресс
    TEST_PROGRESS[chat_id] = {"index": 0, "score": 0}

    # intro + первый вопрос
    intro = text(const.TEST)
    if intro:
        await callback.message.answer(intro, parse_mode=ParseMode.HTML)

    await send_test_question(callback.message, chat_id)
    await callback.answer()


async def send_test_question(message: Message, chat_id: int):
    progress = TEST_PROGRESS.get(chat_id)
    if progress is None:
        # на всякий случай инициализация
        progress = {"index": 0, "score": 0}
        TEST_PROGRESS[chat_id] = progress

    idx = progress["index"]

    # если вопросы кончились — показываем результат
    if idx >= len(TEST_QUESTIONS):
        await send_test_result(message, chat_id)
        return

    q = TEST_QUESTIONS[idx]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=opt["text"],
                    callback_data=f"{const.TEST}:{idx}:{opt['score']}",
                )
            ]
            for opt in q["options"]
        ]
    )

    await message.answer(
        f"<b>Вопрос {idx + 1} из {len(TEST_QUESTIONS)}</b>\n\n{q['text']}",
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
    )


async def send_test_result(message: Message, chat_id: int):
    progress = TEST_PROGRESS[chat_id]
    if progress is None:
        return

    total = progress["score"]
    # очищаем состояние
    TEST_PROGRESS.pop(chat_id, None)

    # границы можешь подправить на вкус
    if total <= 3:
        result = text(const.TEST + "_result_low")
    elif total <= 7:
        result = text(const.TEST + "_result_medium")
    else:
        result = text(const.TEST + "_result_high")

    await message.answer(
        result,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboards.client_keyboard(),
    )


@router.callback_query(F.data.startswith(const.TEST + ":"))
async def callback_test_answer(callback: CallbackQuery):
    parts = callback.data.split(":")
    if len(parts) != 3:
        await callback.answer()
        return

    _, q_idx_str, score_str = parts

    try:
        q_idx = int(q_idx_str)
        score = int(score_str)
    except ValueError:
        await callback.answer()
        return

    chat_id = callback.message.chat.id
    progress = TEST_PROGRESS.get(chat_id)

    # если по какой-то причине состояние потерялось — начнем заново
    if progress is None:
        TEST_PROGRESS[chat_id] = {"index": 0, "score": 0}
        progress = TEST_PROGRESS[chat_id]

    # принимаем только “ожидаемый” вопрос
    if q_idx != progress["index"]:
        await callback.answer("Этот вопрос уже обработан 😊", show_alert=False)
        return

    # обновляем прогресс
    progress["score"] += score
    progress["index"] += 1

    # следующий вопрос или результат
    await send_test_question(callback.message, chat_id)
    await callback.answer()
