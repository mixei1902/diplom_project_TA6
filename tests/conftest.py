import asyncio
import os

import pytest
from httpx import AsyncClient

os.environ['TESTING'] = '1'

from app.db.database import init_db, close_db
from app.main import app

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
    await close_db()

@pytest.fixture(scope="module")
async def client(initialize_db):
    """Предоставляет асинхронного клиента для тестирования FastAPI приложения."""
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac