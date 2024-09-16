# Основная конфигурация приложения (переменные среды, настройки базы данных)
from pydantic import BaseSettings


class Settings(BaseSettings):
    database_url: str
    secret_key: str = "your_secret_key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"


settings = Settings()
