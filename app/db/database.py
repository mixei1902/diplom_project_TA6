# Настройка подключения к базе данных
from tortoise import Tortoise
from app.core.config import settings

TORTOISE_ORM = {
    "connections": {"default": settings.database_url},
    "apps": {
        "models": {
            "models": ["app.db.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}


async def init_db():
    """
    Инициализирует подключение к базе данных и создает таблицы при необходимости.
    """
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()


async def close_db():
    """
    Закрывает все подключения к базе данных.
    """
    await Tortoise.close_connections()

