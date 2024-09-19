from tortoise import Tortoise
from app.core.config import settings

def get_tortoise_config(test: bool = False):
    if test:
        return {
            "connections": {"default": settings.test_database_url},
            "apps": {
                "models": {
                    "models": ["app.db.models", "aerich.models"],
                    "default_connection": "default",
                },
            },
        }
    else:
        return {
            "connections": {"default": settings.database_url},
            "apps": {
                "models": {
                    "models": ["app.db.models", "aerich.models"],
                    "default_connection": "default",
                },
            },
        }


async def init_db(test: bool = False):
    """
    Инициализирует подключение к базе данных и создает таблицы при необходимости.
    """
    await Tortoise.init(config=get_tortoise_config(test))
    await Tortoise.generate_schemas()


async def close_db():
    """
    Закрывает все подключения к базе данных.
    """
    await Tortoise.close_connections()
