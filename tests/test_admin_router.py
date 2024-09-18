import pytest
from httpx import AsyncClient

from app.core.auth import get_password_hash
from app.db.models import User
from app.services.user_service import UserService


@pytest.mark.asyncio
async def test_admin_get_users(client: AsyncClient):
    # Создаём администратора
    password_hash = get_password_hash("adminpass")
    admin_user = await User.create(
        first_name="Admin",
        last_name="User",
        email="admin@example.com",
        password_hash=password_hash,
        is_admin=True
    )
    # Входим под администратором
    response = await client.post("/login", json={
        "email": "admin@example.com",
        "password": "adminpass"
    })
    cookies = response.cookies
    # Запрашиваем список пользователей
    response = await client.get("/private/users?page=1&size=10", cookies=cookies)
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "meta" in data


@pytest.mark.asyncio
async def test_non_admin_cannot_access_admin_endpoints(client: AsyncClient):
    # Входим под обычным пользователем
    response = await client.post("/login", json={
        "email": "jane@example.com",
        "password": "password123"
    })
    cookies = response.cookies
    # Пытаемся получить доступ к административному эндпоинту
    response = await client.get("/private/users?page=1&size=10", cookies=cookies)
    assert response.status_code == 403


# async def test_admin_create_user(authenticated_admin_client: AsyncClient):
#     Тестирование cоздания пользователя администратором
#     new_user_data = {
#         "first_name": "New",
#         "last_name": "User",
#         "email": "newuser@example.com",
#         "password": "newpassword",
#         "is_admin": False
#     }
#     response = await authenticated_admin_client.post("/private/users", json=new_user_data)
#     assert response.status_code == 201
#     data = response.json()
#     assert data["email"] == "newuser@example.com"
#     # Удаление созданного пользователя
#     await UserService.delete_user(data["id"])
