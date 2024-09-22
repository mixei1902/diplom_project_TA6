import asyncio
import os

import pytest
from httpx import AsyncClient
from tortoise import Tortoise
from app.core.config import settings
from app.db.database import init_db, close_db, get_tortoise_config
from app.main import app

# Установите переменную окружения перед импортом app
os.environ['TESTING'] = '1'

@pytest.fixture(scope="session")
def event_loop():
    """Создаёт event loop для всей сессии тестов."""
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="module")
async def initialize_db():
    """Инициализирует и очищает тестовую базу данных перед и после тестов."""
    await init_db(test=True)
    yield
    await Tortoise._drop_databases()
    await close_db()

@pytest.fixture(scope="module")
async def client(initialize_db):
    """Предоставляет асинхронного клиента для тестирования FastAPI приложения."""
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac