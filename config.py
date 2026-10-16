
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import URL


# Project root: the folder containing run.py and config.py
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from the project-root .env file
ENV_FILE = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_FILE, override=True)


class Config:
    # Flask security
    SECRET_KEY = os.getenv("SECRET_KEY")

    if not SECRET_KEY:
        raise RuntimeError(
            f"SECRET_KEY is missing. Please add it to: {ENV_FILE}"
        )

    # MySQL database settings
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_NAME = os.getenv("DB_NAME", "bank_fraud_db")

    # SQLAlchemy connection
    SQLALCHEMY_DATABASE_URI = URL.create(
        drivername="mysql+pymysql",
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        query={"charset": "utf8mb4"},
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File upload limit: 5 MB
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    # Upload and machine-learning model directories
    UPLOAD_FOLDER = str(BASE_DIR / "data" / "uploads")
    MODEL_FOLDER = str(BASE_DIR / "models")
