from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import app.const as const
from app.texts import button

MASTER_BUTTON = InlineKeyboardButton(
    text=button(const.MASTER),
    callback_data=const.MASTER,
)

CLIENTS_BUTTON = InlineKeyboardButton(
    text=button(const.CLIENT),
    callback_data=const.CLIENT,
)

SERVICES_BUTTON = InlineKeyboardButton(
    text=button(const.SERVICES),
    callback_data=const.SERVICES,
)

PRICE_BUTTON = InlineKeyboardButton(
    text=button(const.PRICE),
    callback_data=const.PRICE,
)

REVIEWS_BUTTON = InlineKeyboardButton(
    text=button(const.REVIEWS),
    callback_data=const.REVIEWS,
)

SIGNING_BUTTON = InlineKeyboardButton(
    text=button(const.SIGNING),
    url="https://dikidi.ru/1723277",
)

CONSULTING_BUTTON = InlineKeyboardButton(
    text=button(const.CONSULTING),
    callback_data=const.CONSULTING,
)

RETURN_CLIENT_BUTTON = InlineKeyboardButton(
    text=button(const.CLIENT),
    callback_data=const.CLIENT,
)

KERATIN_BUTTON = InlineKeyboardButton(
    text=button(const.KERATIN),
    callback_data=const.KERATIN,
)

BOTOX_BUTTON = InlineKeyboardButton(
    text=button(const.BOTOX),
    callback_data=const.BOTOX,
)

NANOPLASTICS_BUTTON = InlineKeyboardButton(
    text=button(const.NANOPLASTIC),
    callback_data=const.NANOPLASTIC,
)

TEST_BUTTON = InlineKeyboardButton(
    text=button(const.TEST),
    callback_data=const.TEST,
)


def start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [MASTER_BUTTON, CLIENTS_BUTTON],
        ]
    )


def client_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [SERVICES_BUTTON],
            [PRICE_BUTTON, REVIEWS_BUTTON],
            [TEST_BUTTON],
            [SIGNING_BUTTON, CONSULTING_BUTTON],
        ]
    )


def services_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [KERATIN_BUTTON],
            [BOTOX_BUTTON],
            [NANOPLASTICS_BUTTON],
        ]
    )


def services_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [PRICE_BUTTON, REVIEWS_BUTTON],
            [SIGNING_BUTTON, CONSULTING_BUTTON],
            [RETURN_CLIENT_BUTTON],
        ]
    )


def reviews_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [SIGNING_BUTTON],
        ]
    )


def master_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [SERVICES_BUTTON],
        ]
    )
