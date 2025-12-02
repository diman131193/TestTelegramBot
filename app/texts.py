import json
from pathlib import Path
from app.paths import DATA_DIR

TEXTS_PATH = DATA_DIR / "texts.json"
FILES_PATH = DATA_DIR / "files.json"
ADVICES_PATH = DATA_DIR / "advices.json"
TEST_QUESTIONS_PATH = DATA_DIR / "test_questions.json"


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    return {str(k): v for k, v in data.items()}


TEXTS = load_json(TEXTS_PATH)
FILES = load_json(FILES_PATH)
ADVICES = load_json(ADVICES_PATH)


def text(key: str) -> str:
    return TEXTS.get(key, f"[no text: {key}]")


def button(key: str) -> str:
    return TEXTS.get(f"button_{key}", f"[no button: {key}]")


def file(key: str) -> str:
    return FILES.get(key, f"[no file: {key}]")


def files(key: str) -> list[str]:
    return FILES.get(key, [])


def load_test_config() -> dict:
    if not TEST_QUESTIONS_PATH.exists():
        return {"start": None, "questions": {}, "rules": []}

    with TEST_QUESTIONS_PATH.open(encoding="utf-8") as f:
        data = json.load(f)

    start = data.get("start")
    questions = data.get("questions", {})
    rules = data.get("rules", [])

    return {"start": start, "questions": questions, "rules": rules}


TEST_CONFIG = load_test_config()
