import asyncio

import psycopg2
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from tortoise import Tortoise

from app.core.auth import get_password_hash
from app.core.config import settings
from app.db.models import User
from app.main import app


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Синхронная фикстура для настройки тестовой базы данных
@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Фикстура для настройки тестовой базы данных:
    - Подключается к базе данных 'postgres'.
    - Завершает все соединения с 'TA6_test'.
    - Удаляет и создаёт базу данных 'TA6_test'.
    """
    conn = psycopg2.connect(
        dbname='postgres',
        user='postgres',
        password='12345',
        host='localhost',
        port='5432'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    try:
        # Завершение всех активных соединений с 'TA6_test'
        cursor.execute("""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = 'TA6_test'
              AND pid <> pg_backend_pid();
        """)
        # Удаление базы данных 'TA6_test', если она существует
        cursor.execute('DROP DATABASE IF EXISTS "TA6_test";')
        # Создание базы данных 'TA6_test'
        cursor.execute('CREATE DATABASE "TA6_test";')
    except Exception as e:
        print(f"Ошибка при настройке тестовой базы данных: {e}")
    finally:
        cursor.close()
        conn.close()

    yield


# Асинхронная фикстура для инициализации Tortoise ORM
@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_tortoise_fixture():
    """
    Инициализация Tortoise ORM с тестовой базой данных.
    """
    await Tortoise.init(
        db_url=settings.test_database_url,
        modules={'models': ['app.db.models']}
    )
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


# Асинхронная фикстура для создания клиента HTTP
@pytest.fixture
async def client():
    """
    Создание асинхронного клиента HTTP для тестов.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c


# Асинхронная фикстура для создания администратора
@pytest.fixture
async def admin_user():
    """
    Создание и удаление администратора.
    """
    password_hash = get_password_hash("adminpass")
    admin = await User.create(
        first_name="Admin",
        last_name="User",
        email="admin@example.com",
        password_hash=password_hash,
        is_admin=True
    )
    yield admin
    await admin.delete()


# Асинхронная фикстура для создания обычного пользователя
@pytest.fixture
async def regular_user():
    """
    Создание и удаление обычного пользователя.
    """
    password_hash = get_password_hash("password123")
    user = await User.create(
        first_name="Regular",
        last_name="User",
        email="user@example.com",
        password_hash=password_hash,
        is_admin=False
    )
    yield user
    await user.delete()
