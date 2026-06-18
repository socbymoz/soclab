import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback-dev-key-change-in-production")
    FLASK_ENV = os.getenv("FLASK_ENV", "production")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    PASS_SCORE = 9

    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "true").lower() == "true"
    SESSION_COOKIE_HTTPONLY = os.getenv("SESSION_COOKIE_HTTPONLY", "true").lower() == "true"
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
