import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
APP_STORAGE_DIR = Path(os.getenv("APP_STORAGE_DIR", "generated"))
APP_STORAGE_DIR = (BASE_DIR / APP_STORAGE_DIR).resolve()
APP_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
