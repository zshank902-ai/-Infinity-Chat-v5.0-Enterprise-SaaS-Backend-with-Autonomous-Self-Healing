import os
from pathlib import Path
from dotenv import load_dotenv
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

class Config:
    GROQ_KEYS = [
        os.getenv("GROQ_API_KEY_1"),
        os.getenv("GROQ_API_KEY_2"),
    ]
    # Remove empty keys
    GROQ_KEYS = [k for k in GROQ_KEYS if k]

    GEMINI_KEYS = [
        os.getenv("GEMINI_API_KEY_1"),
        os.getenv("GEMINI_API_KEY_2"),
    ]
    GEMINI_KEYS = [k for k in GEMINI_KEYS if k]

    DEEPSEEK_KEYS = [
        os.getenv("DEEPSEEK_API_KEY_1"),
    ]
    DEEPSEEK_KEYS = [k for k in DEEPSEEK_KEYS if k]
    
    KAGGLE_USERNAME = os.getenv("KAGGLE_USERNAME")
    KAGGLE_KEY = os.getenv("KAGGLE_KEY")

    DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "groq")

config = Config()
