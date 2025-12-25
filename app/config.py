import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    PERMANENT_SESSION_LIFETIME = timedelta(
        days=int(os.getenv("PERMANENT_SESSION_LIFETIME", default=30))
    )

    DB_HOSTNAME = os.getenv("DB_HOSTNAME")
    DB_PORT = os.getenv("DB_PORT")
    DB_USERNAME = os.getenv("DB_USERNAME")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_DATABASE = os.getenv("DB_DATABASE")
    DB_SCHEMA = os.getenv("DB_SCHEMA")

    HCAPTCHA_SITE_KEY = os.getenv("HCAPTCHA_SITE_KEY")
    HCAPTCHA_SECRET_KEY = os.getenv("HCAPTCHA_SECRET_KEY")
