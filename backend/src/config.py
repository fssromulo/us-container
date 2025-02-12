# Python imports
import os

# Pip imports
from decouple import config
from pydantic import BaseSettings


class Settings(BaseSettings):
    ROOT_DIR: str = os.path.dirname(os.path.abspath(__file__))
    SECRET_KEY: str = config("SECRET_KEY", default="dev-secret-key")
    ALLOWED_EXTENSIONS: list = config("ALLOWED_EXTENSIONS", default=".png,.jpg,.jpeg", cast=lambda v: v.split(","))
    EMAIL_FROM: str = config("EMAIL_FROM", default="")
    EMAIL_TO: str = config("EMAIL_TO", default="tanner@mobilestoragetech.com")
    DB_USER: str = config("DB_USER", default="hello_fastapi")
    DB_PASS: str = config("DB_PASS", default="hello_fastapi")
    DB_HOST: str = config("DB_HOST", default="db")
    DB_PORT: str = config("DB_PORT", default="5432")
    DB_NAME: str = config("DB_NAME", default="containerCrm")
    REDIS_HOST: str = config("REDIS_HOST", default="redis-server")
    REDIS_PORT: str = config("REDIST_PORT", default="6379")
    BASE_INVOICE_URL: str = config("BASE_INVOICE_URL", default="")
    STAGE: str = config("STAGE", default="dev")

    class Config:
        env_file = ".env"


settings = Settings()
