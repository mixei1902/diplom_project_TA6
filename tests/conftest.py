import asyncio

import pytest
from httpx import AsyncClient
from tortoise.contrib.test import finalizer, initializer

from app.core.config import settings
from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    # Используем WindowsSelectorEventLoopPolicy для совместимости с Windows
    if asyncio.get_event_loop_policy().__class__.__name__ != 'WindowsSelectorEventLoopPolicy':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="module", autouse=True)
def initialize_tests(event_loop):
    initializer(['app.db.models'], db_url='postgres://postgres:12345@localhost:5432/TA6_test', app_label='models')
    yield
    finalizer()


@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://testserver") as c:
        yield c
