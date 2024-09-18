# Основная конфигурация приложения (переменные среды, настройки базы данных)
from typing import Optional

from pydantic import BaseSettings, PostgresDsn, validator


class Settings(BaseSettings):
    # Настройки базы данных
    db_host: Optional[str] = "localhost"
    db_port: Optional[str] = "5432"
    db_user: Optional[str] = "postgres"
    db_password: Optional[str] = "12345"
    db_name: Optional[str] = "TA6"
    database_url: Optional[PostgresDsn] = None
    test_database_url: Optional[PostgresDsn] = "postgres://postgres:12345@localhost:5432/TA6_test"

    # Настройки приложения
    secret_key: str  = "your_secret_key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"

    @validator("database_url", pre=True)
    def assemble_db_connection(cls, v, values):
        """
        Собирает URL для подключения к базе данных из отдельных компонентов
        """
        if isinstance(v, str) and v != "":
            return v
        db_user = values.get("db_user")
        db_password = values.get("db_password")
        db_host = values.get("db_host")
        db_port = values.get("db_port")
        db_name = values.get("db_name")
        if not all([db_user, db_password, db_host, db_port, db_name]):
            raise ValueError("Недостаточно параметров для сборки database_url. Проверьте настройки базы данных в .env")
        return PostgresDsn.build(
            scheme="postgresql",
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
            path=f"/{db_name}",
        )

    @validator("test_database_url", pre=True)
    def assemble_test_db_connection(cls, v, values):
        """
        Собирает URL для подключения к тестовой базе данных из отдельных компонентов
        """
        if isinstance(v, str) and v != "":
            return v
        db_user = values.get("db_user")
        db_password = values.get("db_password")
        db_host = values.get("db_host")
        db_port = values.get("db_port")
        db_name = values.get("db_name")
        if not all([db_user, db_password, db_host, db_port, db_name]):
            raise ValueError(
                "Недостаточно параметров для сборки test_database_url. Проверьте настройки базы данных в .env")
        test_db_name = f"{db_name}_test"
        return PostgresDsn.build(
            scheme="postgresql",
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
            path=f"/{test_db_name}",
        )


settings = Settings()
