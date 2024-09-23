import os
import pytest
import asyncio
from httpx import AsyncClient
from tortoise import Tortoise

# Установите переменную окружения перед импортом приложения
os.environ['TESTING'] = '1'

from app.main import app  # Импортируйте после установки переменной окружения
from app.db.database import init_db, close_db  # Убедитесь, что пути правильные

@pytest.fixture(scope="session")
def event_loop():
    """
    Создает и возвращает event loop для всей сессии тестов.
    Использует дефолтный event loop policy.
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def initialize_db():
    """
    Фикстура для инициализации Tortoise ORM с использованием SQLite in-memory базы данных.
    Автоматически применяется ко всей сессии тестов.
    """
    await init_db()  # Инициализация базы данных через функцию из app.db.database
    yield
    await close_db()  # Закрытие соединений после тестов

@pytest.fixture
async def client():
    """
    Фикстура для создания AsyncClient.
    Использует приложение FastAPI для отправки запросов.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
