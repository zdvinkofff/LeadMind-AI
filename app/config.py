import os

from dotenv import load_dotenv

load_dotenv()

raw_ai_mode = os.getenv("AI_MODE", "demo").strip().lower()

if raw_ai_mode == "":
    raw_ai_mode = "demo"

AI_MODE = raw_ai_mode
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()

DB_HOST = os.getenv("DB_HOST", "localhost").strip()
DB_PORT = int(os.getenv("DB_PORT", "5432").strip())
DB_NAME = os.getenv("DB_NAME", "leadmind_ai").strip()
DB_USER = os.getenv("DB_USER", "postgres").strip()
DB_PASSWORD = os.getenv("DB_PASSWORD", "").strip()