import uuid

import pytest
from httpx import AsyncClient

from app.db.models import User
from app.schemas.user_schema import LoginModel, CreateUser
from app.services.user_service import UserService


def generate_unique_email(prefix="user"):
    """Генерирует уникальный email для тестов."""
    unique_id = uuid.uuid4()
    return f"{prefix}_{unique_id}@example.com"


@pytest.mark.asyncio
async def test_admin_get_users(client: AsyncClient, initialize_db):
    # Создаем администратора с уникальным email
    admin_email = generate_unique_email("admin")
    admin_data = CreateUser(
        first_name="Admin8",
        last_name="User8",
        other_name=None,
        email=admin_email,
        phone="5555555555",
        birthday="1980-01-01",
        password="adminpassword8",
        is_admin=True,
        city=1,
        additional_info=None
    )
    admin = await UserService.create_user_service(admin_data)

    # Логин администратора для получения токена
    login_data = LoginModel(
        email=admin_email,
        password="adminpassword8"
    )
    login_response = await client.post("/users/login", json=login_data.dict())
    assert login_response.status_code == 200
    tokens = login_response.json()
    access_token = tokens["access_token"]

    # Устанавливаем токен в cookies
    client.cookies.set("access_token", access_token)

    # Создаем нескольких пользователей для тестирования с уникальными email
    users_data = [
        {
            "first_name": "User8",
            "last_name": "Test8",
            "other_name": None,
            "email": generate_unique_email("user8"),
            "phone": "1111111111",
            "birthday": "1991-01-01",
            "password": "user1password",
            "is_admin": False,
            "city": 2,
            "additional_info": None
        },
        {
            "first_name": "User9",
            "last_name": "Test9",
            "other_name": None,
            "email": generate_unique_email("user9"),
            "phone": "2222222222",
            "birthday": "1992-02-02",
            "password": "user9password",
            "is_admin": False,
            "city": 3,
            "additional_info": None
        }
    ]

    created_users = []

    try:
        for user_data in users_data:
            response = await client.post("/private/users", json=user_data)
            assert response.status_code == 201, f"Не удалось создать пользователя: {user_data['email']}"
            created_user = await User.get(email=user_data["email"])
            created_users.append(created_user)

        # Отправляем GET-запрос на получение списка пользователей
        response = await client.get("/private/users", params={"page": 1, "size": 10})
        assert response.status_code == 200, "Не удалось получить список пользователей."
        data = response.json()
        assert "data" in data
        assert "meta" in data
        assert data["meta"]["pagination"]["total"] >= len(
            users_data), "Общее количество пользователей меньше ожидаемого."
        assert len(data["data"]) >= len(users_data), "Количество пользователей в списке меньше ожидаемого."

        # Проверяем, что в списке присутствуют созданные пользователи
        emails = [user["email"] for user in data["data"]]
        for user_data in users_data:
            assert user_data["email"] in emails, f"Пользователь {user_data['email']} не найден в списке."

    finally:
        # Удаляем созданных пользователей
        for user in created_users:
            delete_result = await UserService.delete_user(user.id)
            assert delete_result, f"Не удалось удалить пользователя с ID {user.id}."

        # Удаляем администратора
        delete_result = await UserService.delete_user(admin.id)
        assert delete_result, f"Не удалось удалить администратора с ID {admin.id}."


@pytest.mark.asyncio
async def test_admin_create_user(client: AsyncClient, initialize_db):
    # Создаем администратора с уникальным email
    admin_email = generate_unique_email("admin")
    admin_data = CreateUser(
        first_name="Admin",
        last_name="User",
        other_name=None,
        email=admin_email,
        phone="5555555555",
        birthday="1980-01-01",
        password="adminpassword",
        is_admin=True,
        city=1,
        additional_info=None
    )
    admin = await UserService.create_user_service(admin_data)

    # Логин администратора для получения токена
    login_data = LoginModel(
        email=admin_email,
        password="adminpassword"
    )
    login_response = await client.post("/users/login", json=login_data.dict())
    assert login_response.status_code == 200
    tokens = login_response.json()
    access_token = tokens["access_token"]

    # Устанавливаем токен в cookies
    client.cookies.set("access_token", access_token)

    # Данные для создания нового пользователя через администратора с уникальным email
    new_user_email = generate_unique_email("charlie")
    new_user_data = {
        "first_name": "Charlie",
        "last_name": "Chaplin",
        "other_name": None,
        "email": new_user_email,
        "phone": "6666666666",
        "birthday": "1970-07-07",
        "password": "charliepassword",
        "is_admin": False,
        "city": 2,
        "additional_info": "Silent movie star"
    }

    created_user = None

    try:
        # Отправляем POST-запрос на создание пользователя
        response = await client.post("/private/users", json=new_user_data)
        assert response.status_code == 201, "Не удалось создать нового пользователя администратором."
        data = response.json()
        assert data["email"] == new_user_email, "Email созданного пользователя не совпадает."
        assert data["first_name"] == new_user_data["first_name"], "Имя созданного пользователя не совпадает."

        # Проверяем, что пользователь создан в базе данных
        user = await User.get(email=new_user_email)
        assert user is not None, "Пользователь не найден в базе данных."
        assert user.first_name == new_user_data["first_name"], "Имя пользователя в базе данных не совпадает."

        created_user = user

    finally:
        # Удаляем созданного пользователя
        if created_user:
            delete_result = await UserService.delete_user(created_user.id)
            assert delete_result, f"Не удалось удалить пользователя с ID {created_user.id}."

        # Удаляем администратора
        delete_result = await UserService.delete_user(admin.id)
        assert delete_result, f"Не удалось удалить администратора с ID {admin.id}."
