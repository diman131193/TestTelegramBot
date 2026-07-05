# Техническая спецификация

## Стек

- Python
- `aiogram==3.22.0`
- `aiosqlite==0.21.0`
- `python-dotenv==1.2.2`
- SQLite
- JSON-файлы для контента и медиа-ID

## Запуск

Точка входа: `main.py`.

Переменные окружения загружаются из `.env` в корне проекта через `app/config.py`.

Обязательные переменные:

```env
BOT_TOKEN=<telegram-bot-token>
ADMIN_CHAT_ID=<telegram-admin-chat-id>
```

Алгоритм запуска:

1. Загрузить `.env`.
2. Проверить, что `ADMIN_CHAT_ID` заполнен и является целым числом.
3. Проверить, что `BOT_TOKEN` заполнен и не равен placeholder.
4. Создать `Bot(token=BOT_TOKEN)`.
5. Создать `Dispatcher`.
6. Подключить роутеры `app.handlers.router` и `app.handlers_test.router`.
7. Инициализировать SQLite-базу.
8. Запустить polling.

## Структура проекта

```text
main.py
app/
  const.py
  db.py
  handlers.py
  handlers_test.py
  keyboards.py
  paths.py
  texts.py
data/
  advices.json
  files.json
  test_questions.json
  texts.json
requirements.txt
```

## Модули

### `app/const.py`

Хранит callback-ключи, command-ключи и `ADMIN_CHAT_ID`, прочитанный из env.

Требование: новые callback-data должны добавляться сюда, если используются в нескольких модулях.

### `app/config.py`

Загружает `.env` и валидирует обязательные переменные окружения.

Функции:

- `get_bot_token()` -> возвращает реальный Telegram bot token или падает с понятной ошибкой;
- `get_admin_chat_id()` -> возвращает `ADMIN_CHAT_ID` как `int` или падает с понятной ошибкой.

Файл `.env` не должен коммититься. Файл `.env.example` должен содержать список обязательных переменных без реальных секретов.

### `app/paths.py`

Определяет:

- `BASE_DIR` — корень проекта;
- `DATA_DIR` — папка `data`.

### `app/texts.py`

Загружает JSON-контент при импорте модуля.

Функции:

- `text(key)` -> текст по ключу или fallback;
- `button(key)` -> текст кнопки по ключу `button_<key>` или fallback;
- `file(key)` -> один Telegram file ID или fallback;
- `files(key)` -> список Telegram file ID;
- `load_test_config()` -> структура диагностики.

Ограничение: изменения JSON во время работы процесса не подхватываются без перезапуска.

### `app/keyboards.py`

Собирает inline-клавиатуры из констант и текстов кнопок.

Внешняя запись ведет на:

```text
https://dikidi.ru/1723277
```

### `app/handlers.py`

Основные роуты:

- `/start`;
- `/reviews`;
- `/load`;
- роль клиента;
- роль мастера;
- услуги;
- отзывы;
- консультация;
- пересылка вопроса администратору;
- ответ администратора клиенту;
- fallback на обычный текст.

Состояние консультации хранится в:

```python
ADMIN_CHATS: set[int] = set()
```

### `app/handlers_test.py`

Роуты диагностики волос.

Состояние диагностики хранится в:

```python
TEST_PROGRESS: Dict[int, Any] = {}
```

Загруженные при старте данные:

- `TEST_RULES`;
- `TEST_QUESTIONS`;
- `TEST_START`.

### `app/db.py`

Создает и обновляет SQLite-базу `data/contacts.db`.

Таблица `users`:

```sql
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
```

Поведение `log_user`:

- если `user is None`, функция ничего не делает;
- если пользователь новый, создает запись;
- если пользователь существует, обновляет профиль и последнее действие;
- если новый `phone_number` не передан, сохраняет старый номер телефона.

## Данные

### `data/texts.json`

Содержит тексты сообщений и подписи кнопок.

Правило именования:

- текст экрана: `<key>`;
- текст кнопки: `button_<key>`.

### `data/files.json`

Содержит Telegram file ID:

- строка для одного фото;
- список строк для media group отзывов.

### `data/test_questions.json`

Содержит:

- `start` — ID стартового вопроса;
- `questions` — словарь вопросов;
- `rules` — точные правила выбора совета.

Формат option:

```json
{
  "id": "1.1",
  "text": "вариант ответа",
  "next": "2"
}
```

`next` может быть:

- ID следующего вопроса;
- `advice` для завершения теста.

### `data/advices.json`

Содержит HTML-тексты советов по ключам `advice_<number>`.

## Нефункциональные требования

- Все пользовательские сообщения должны быть совместимы с `ParseMode.HTML`.
- Callback-data должны помещаться в лимит Telegram.
- Бот должен корректно отвечать при отсутствии необязательных данных.
- Локальная БД не должна храниться в git, если содержит реальные пользовательские данные.
- Служебные команды для загрузки media ID должны быть защищены перед production-использованием.

## Текущие технические риски

- Состояния консультации и диагностики хранятся в памяти.
- Нет обработчика `price`.
- Нет миграций БД.
- Нет автоматических тестов.
- Команда `/load` не ограничена администратором.
- В `handlers_test.py` есть `print(progress["answers"])`, который пишет пользовательские ответы в stdout.
