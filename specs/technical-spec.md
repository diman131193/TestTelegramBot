# Техническая спецификация

## Стек

- Python
- `aiogram==3.29.1`
- `aiosqlite==0.22.1`
- `openpyxl==3.1.5` для импорта контентной таблицы
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
  diagnostics.py
  diagnostics_validation.py
  handlers.py
  handlers_test.py
  keyboards.py
  paths.py
  texts.py
data/
  diagnostic_factors.json
  diagnostic_rules.json
  diagnostics_snapshot.json
  files.json
  texts.json
content/
  diagnostics-content.xlsx
scripts/
  manage_diagnostics_content.py
tests/
  test_diagnostics.py
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

Тексты основных экранов загружаются при старте. Дерево диагностики читается при каждом новом вопросе, поэтому успешно опубликованные изменения доступны новым прохождениям без перезапуска.

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

Активное состояние кешируется в:

```python
TEST_PROGRESS: Dict[int, Any] = {}
```

Одновременно состояние сохраняется в SQLite-таблице `diagnostic_sessions`. После перезапуска бота прохождение продолжается с ожидаемого вопроса.

Ответ проверяется относительно ожидаемого вопроса. Повторная или старая callback-кнопка не начисляет признаки повторно.

Результат диагностики собирается через `app.diagnostics.build_recommendation`.

### `app/diagnostics.py`

Расчетный слой диагностики.

Функции:

- `analyze_answers(answers)` -> собирает признаки и выбирает состав результата;
- `build_recommendation(answers)` -> возвращает HTML-текст рекомендации.

Алгоритм:

1. Каждый `answer_id` ищется в `data/diagnostic_factors.json`.
2. Labels перезаписываются последним выбранным значением по группе.
3. Scores суммируются.
4. Tags объединяются.
5. Правила из `data/diagnostic_rules.json` выбирают один `primary`, все `alert` и не более двух `addon`.
6. Итоговый текст собирается в фиксированном продуктовом формате из опубликованного снимка `data/diagnostics_snapshot.json`.
7. Внутренние scores не показываются пользователю.

Поддерживаемые условия правил:

- `min_scores`;
- `max_scores`;
- `label_equals`;
- `label_in`;
- `any_tags`;
- `all_tags`;
- `answers_any`;
- `answers_all`;
- `answers_none`.

### `app/diagnostics_validation.py`

Проверяет данные и прогоняет все допустимые пути до публикации. Контролирует связи, наличие основного результата и лимит Telegram.

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

Таблица `diagnostic_sessions` хранит список ответов, ожидаемый вопрос и время обновления активного прохождения.

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

### `data/diagnostics_snapshot.json`

Единый атомарно публикуемый снимок содержит:

- `questions.start` — ID стартового вопроса;
- `questions.questions` — словарь вопросов;
- `content.settings` — заголовки и ограничения;
- `content.facts` — клиентские подписи признаков;
- `content.modules` — карточки рекомендаций;
- `content.services` — каталог услуг.

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

### `data/diagnostic_factors.json`

Описывает, что означает каждый вариант ответа.

Для каждого `answer_id` можно задать:

- `labels` — категориальные признаки;
- `scores` — численные признаки;
- `tags` — специальные маркеры.

### `data/diagnostic_rules.json`

Содержит:

- связи правил и модулей;
- роли `primary`, `alert`, `addon`;
- условия срабатывания и технические приоритеты;
- ID резервного основного модуля.

### `content/diagnostics-content.xlsx`

Редактор заказчика. Публикуется через `scripts/manage_diagnostics_content.py`; бот напрямую XLSX не читает.

## Нефункциональные требования

- Все пользовательские сообщения должны быть совместимы с `ParseMode.HTML`.
- Callback-data должны помещаться в лимит Telegram.
- Бот должен корректно отвечать при отсутствии необязательных данных.
- Локальная БД не должна храниться в git, если содержит реальные пользовательские данные.
- Служебные команды для загрузки media ID должны быть защищены перед production-использованием.

## Текущие технические риски

- Состояние консультации хранится только в памяти.
- Нет миграций БД.
- Команда `/load` не ограничена администратором.
