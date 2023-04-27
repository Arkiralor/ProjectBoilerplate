from os import path, makedirs
from pydantic import BaseSettings
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):

    APP_NAME: str
    DOMAIN_URL: str
    OWNER_EMAIL: str
    CONTACT_EMAIL: str

    SECRET_KEY: str
    DEBUG: bool
    ENV_TYPE:str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    DB_NAME: str
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASSWORD: str

    MONGO_URI: str
    MONGO_NAME:str
    MONGO_HOST:str
    MONGO_PORT:str
    MONGO_USER:Optional[str]
    MONGO_PASSWORD:Optional[str]

    SNS_SENDER_ID: str
    AWS_ACCESS_KEY_ID:str
    AWS_SECRET_ACCESS_KEY:str
    AWS_REGION_NAME:str

    BASE_PATH = Path(__file__).resolve().parent.parent
    MAX_ITEMS_PER_PAGE: int = 15


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

if __name__ == "__main__":
    pass