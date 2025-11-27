import aiosqlite
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "contacts.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        # await db.execute("""DROP TABLE IF EXISTS users;""")
        # await db.commit()
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            username TEXT,
            phone_number TEXT,
            is_bot INTEGER,
            language_code TEXT,
            last_activity_at TEXT,
            command TEXT
        );
        """)
        await db.commit()


async def log_user(chat_id: int,
                   user,
                   command: str = None,
                   phone_number: str = None):
    if user is None:
        return

    now = datetime.now(timezone.utc).isoformat()

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT chat_id, phone_number FROM users WHERE chat_id = ?",
            (chat_id,)
        )
        row = await cursor.fetchone()

        if row is not None and phone_number is None:
            _, existing_phone = row
            phone_number = existing_phone

        if row is None:
            # Вставка нового пользователя
            await db.execute(
                """
                INSERT INTO users (
                    chat_id, first_name, last_name, username, 
                    phone_number, is_bot, language_code,
                    last_activity_at, command
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    chat_id,
                    user.first_name,
                    user.last_name,
                    user.username,
                    phone_number,
                    int(user.is_bot),
                    user.language_code,
                    now,
                    command,
                )
            )
        else:
            # Обновление существующего
            await db.execute(
                """
                UPDATE users
                SET
                    first_name = ?,
                    last_name = ?,
                    username = ?,
                    phone_number = ?,
                    is_bot = ?,
                    language_code = ?,
                    last_activity_at = ?,
                    command = ?
                WHERE chat_id = ?
                """,
                (
                    user.first_name,
                    user.last_name,
                    user.username,
                    phone_number,
                    int(user.is_bot),
                    user.language_code,
                    now,
                    command,
                    chat_id,
                )
            )

        await db.commit()
