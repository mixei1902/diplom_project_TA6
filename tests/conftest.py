import asyncio

import pytest
from httpx import AsyncClient
from tortoise.contrib.test import finalizer, initializer

from app.core.config import settings
from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture(scope="module", autouse=True)
async def initialize_tests():
    # Инициализируем базу данных для тестирования
    initializer(['app.db.models'], db_url=settings.test_database_url, app_label='models')
    yield
    # Завершаем работу с базой данных после тестов
    finalizer()


@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://testserver") as c:
        yield c
