from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import app.constants as const
from app.texts import TEXTS

# --- Кнопки ---

MASTER_BUTTON = InlineKeyboardButton(
    text=TEXTS[f"button_{const.MASTER}"],
    callback_data=const.MASTER,
)

CLIENTS_BUTTON = InlineKeyboardButton(
    text=TEXTS[f"button_{const.CLIENT}"],
    callback_data=const.CLIENT,
)

SERVICES_BUTTON = InlineKeyboardButton(
    text=TEXTS[f"button_{const.SERVICES}"],
    callback_data=const.SERVICES,
)

PRICE_BUTTON = InlineKeyboardButton(
    text=TEXTS[f"button_{const.PRICE}"],
    callback_data=const.PRICE,
)

REVIEWS_BUTTON = InlineKeyboardButton(
    text=TEXTS[f"button_{const.REVIEWS}"],
    callback_data=const.REVIEWS,
)

SIGNING_BUTTON = InlineKeyboardButton(
    text=TEXTS[f"button_{const.SIGNING}"],
    url="https://dikidi.ru/1723277",
)

CONSULTING_BUTTON = InlineKeyboardButton(
    text=TEXTS[f"button_{const.CONSULTING}"],
    callback_data=const.CONSULTING,
)

RETURN_CLIENT_BUTTON = InlineKeyboardButton(
    text=TEXTS[f"button_return_{const.CLIENT}"],
    callback_data=const.CLIENT,
)

KERATIN_BUTTON = InlineKeyboardButton(
    text=TEXTS[f"button_{const.KERATIN}"],
    callback_data=const.KERATIN,
)

BOTOX_BUTTON = InlineKeyboardButton(
    text=TEXTS[f"button_{const.BOTOX}"],
    callback_data=const.BOTOX,
)

NANOPLASTICS_BUTTON = InlineKeyboardButton(
    text=TEXTS[f"button_{const.NANOPLASTIC}"],
    callback_data=const.NANOPLASTIC,
)


# --- Готовые клавиатуры ---


def start_keyboard() -> InlineKeyboardMarkup:
    """Меню /start: Мастер / Клиент."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [MASTER_BUTTON, CLIENTS_BUTTON],
        ]
    )


def client_menu_keyboard() -> InlineKeyboardMarkup:
    """Меню клиента: услуги, прайс, отзывы, запись, консультация."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [SERVICES_BUTTON],
            [PRICE_BUTTON, REVIEWS_BUTTON],
            [SIGNING_BUTTON, CONSULTING_BUTTON],
        ]
    )


def services_keyboard() -> InlineKeyboardMarkup:
    """Меню услуг: кератин / ботокс / нанопластика."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [KERATIN_BUTTON],
            [BOTOX_BUTTON],
            [NANOPLASTICS_BUTTON],
        ]
    )


def keratin_menu_keyboard() -> InlineKeyboardMarkup:
    """Меню после выбора кератина: прайс, отзывы, запись, консультация, назад в клиентское меню."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [PRICE_BUTTON, REVIEWS_BUTTON],
            [SIGNING_BUTTON, CONSULTING_BUTTON],
            [RETURN_CLIENT_BUTTON],
        ]
    )


def reviews_keyboard() -> InlineKeyboardMarkup:
    """Под отзывами — кнопка записи."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [SIGNING_BUTTON],
        ]
    )


def master_menu_keyboard() -> InlineKeyboardMarkup:
    """Меню мастера: пока только переход к услугам."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [SERVICES_BUTTON],
        ]
    )
