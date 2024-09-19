import pytest
from httpx import AsyncClient

from app.db.models import User
from app.schemas.user_schema import CreateUser, LoginModel
from app.services.user_service import UserService


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    # Данные для регистрации нового пользователя
    user_data = {
        "first_name": "John",
        "last_name": "Doe",
        "other_name": "Middle",
        "email": "john.doe@example.com",
        "phone": "1234567890",
        "birthday": "1990-01-01",
        "password": "password123",
        "is_admin": False,
        "city": 1,
        "additional_info": "Some additional info"
    }

    response = await client.post("/users/register", json=user_data)
    assert response.status_code == 200 or response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["first_name"] == user_data["first_name"]
    assert "password_hash" not in data  # Пароль не должен быть возвращен

    # Проверка в базе данных
    user = await User.get(email=user_data["email"])
    assert user is not None
    assert user.first_name == user_data["first_name"]
    assert user.is_admin == user_data["is_admin"]


async def test_login_user(client: AsyncClient, initialize_db):
    # Сначала создадим пользователя напрямую через сервис
    user_data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "other_name": None,
        "email": "jane.smith@example.com",
        "phone": "0987654321",
        "birthday": "1992-02-02",
        "password": "securepassword",
        "is_admin": False,
        "city": 2,
        "additional_info": None
    }

    # Создаем пользователя через сервис
    user = await UserService.create_user_service(CreateUser(**user_data))

    # Данные для логина
    login_data = {
        "email": "jane.smith@example.com",
        "password": "securepassword"
    }

    response = await client.post("/users/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_get_current_user_data(client: AsyncClient, initialize_db):
    # Создаем пользователя через сервис
    user_data = CreateUser(
        first_name="Alice",
        last_name="Wonderland",
        other_name=None,
        email="alice@example.com",
        phone="1122334455",
        birthday="1995-05-05",
        password="alicepassword",
        is_admin=False,
        city=3,
        additional_info=None
    )
    user = await UserService.create_user_service(user_data)

    # Логин пользователя для получения токена
    login_data = LoginModel(
        email="alice@example.com",
        password="alicepassword"
    )
    login_response = await client.post("/users/login", json=login_data.dict())
    assert login_response.status_code == 200
    tokens = login_response.json()
    access_token = tokens["access_token"]

    # Устанавливаем токен в cookies
    client.cookies.set("access_token", access_token)

    # Отправляем запрос на получение текущего пользователя
    response = await client.get("/users/current")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "alice@example.com"
    assert data["first_name"] == "Alice"


@pytest.mark.asyncio
async def test_update_current_user(client: AsyncClient, initialize_db):
    # Создаем пользователя через сервис
    user_data = CreateUser(
        first_name="Bob",
        last_name="Builder",
        other_name=None,
        email="bob@example.com",
        phone="2233445566",
        birthday="1985-04-04",
        password="bobpassword",
        is_admin=False,
        city=2,
        additional_info=None
    )
    user = await UserService.create_user_service(user_data)

    # Логин пользователя для получения токена
    login_data = LoginModel(
        email="bob@example.com",
        password="bobpassword"
    )
    login_response = await client.post("/users/login", json=login_data.dict())
    assert login_response.status_code == 200
    tokens = login_response.json()
    access_token = tokens["access_token"]

    # Устанавливаем токен в cookies
    client.cookies.set("access_token", access_token)

    # Данные для обновления
    update_data = {
        "first_name": "Robert",
        "phone": "3344556677"
    }

    # Отправляем PATCH-запрос на обновление текущего пользователя
    response = await client.patch("/users/current", json=update_data)
    assert response.status_code == 200
    updated_user = response.json()
    assert updated_user["first_name"] == "Robert"
    assert updated_user["phone"] == "3344556677"

    # Проверяем, что изменения отражены в базе данных
    user_in_db = await User.get(email="bob@example.com")
    assert user_in_db.first_name == "Robert"
    assert user_in_db.phone == "3344556677"
