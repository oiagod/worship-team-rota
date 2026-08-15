from datetime import timedelta
from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI") or "sqlite:///app.db"
    SECRET_KEY=os.environ.get("SECRET_KEY")

    # Session configuration for enhanced security
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False #WARN: set to true in production with HTTPS
