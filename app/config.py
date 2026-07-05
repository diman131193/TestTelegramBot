import os

from dotenv import load_dotenv

from app.paths import BASE_DIR

ENV_PATH = BASE_DIR / ".env"
BOT_TOKEN_PLACEHOLDER = "replace_with_telegram_bot_token"

load_dotenv(ENV_PATH)


def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or not value.strip():
        raise RuntimeError(
            f"Environment variable {name} is required. "
            f"Set it in {ENV_PATH}."
        )
    return value.strip()


def get_bot_token() -> str:
    token = get_required_env("BOT_TOKEN")
    if token == BOT_TOKEN_PLACEHOLDER:
        raise RuntimeError(
            f"Replace BOT_TOKEN placeholder in {ENV_PATH} with a real "
            "Telegram bot token from BotFather."
        )
    return token


def get_admin_chat_id() -> int:
    raw_value = get_required_env("ADMIN_CHAT_ID")
    try:
        return int(raw_value)
    except ValueError as exc:
        raise RuntimeError(
            f"ADMIN_CHAT_ID must be an integer, got {raw_value!r}."
        ) from exc
