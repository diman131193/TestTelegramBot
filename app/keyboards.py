from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

import app.const as const
from app.texts import button

SIGNING_URL = "https://dikidi.ru/1723277"


def _button(key: str) -> KeyboardButton:
    return KeyboardButton(text=button(key))


def _keyboard(rows: list[list[str]]) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [_button(key) for key in row]
            for row in rows
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие",
    )


def start_keyboard() -> ReplyKeyboardMarkup:
    return _keyboard([
        [const.MASTER, const.CLIENT],
    ])


def client_keyboard() -> ReplyKeyboardMarkup:
    return _keyboard([
        [const.SERVICES],
        [const.PRICE, const.REVIEWS],
        [const.TEST],
        [const.SIGNING, const.CONSULTING],
    ])


def services_keyboard() -> ReplyKeyboardMarkup:
    return _keyboard([
        [const.KERATIN],
        [const.BOTOX],
        [const.NANOPLASTIC],
        [const.CLIENT],
    ])


def services_menu_keyboard() -> ReplyKeyboardMarkup:
    return _keyboard([
        [const.PRICE, const.REVIEWS],
        [const.SIGNING, const.CONSULTING],
        [const.CLIENT],
    ])


def reviews_keyboard() -> ReplyKeyboardMarkup:
    return _keyboard([
        [const.SIGNING],
        [const.CLIENT],
    ])


def master_keyboard() -> ReplyKeyboardMarkup:
    return _keyboard([
        [const.SERVICES],
        [const.CLIENT],
    ])
