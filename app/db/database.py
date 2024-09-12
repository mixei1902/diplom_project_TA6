# Настройка подключения к базе данных
from tortoise import Tortoise

TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "host": "localhost",
                "port": "5432",
                "user": "postgres",
                "password": "12345",
                "database": "TA6",
            }
        }
    },
    "apps": {
        "models": {
            "models": ["app.db.models", "aerich.models"],  # Добавляем модели для миграций с aerich
            "default_connection": "default",
        }
    },
}


async def init_db():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()


async def close_db():
    await Tortoise.close_connections()
