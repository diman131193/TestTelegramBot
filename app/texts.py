import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

TEXTS_PATH = BASE_DIR / "texts.json"
FILES_PATH = BASE_DIR / "files.json"


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    return {str(k): v for k, v in data.items()}


TEXTS = load_json(TEXTS_PATH)
FILES = load_json(FILES_PATH)
