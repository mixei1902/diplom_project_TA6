import pytest
from httpx import AsyncClient
from app.core.auth import get_password_hash
from app.db.models import User


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    response = await client.post("/register", json={
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "password": "password123",
        "is_admin": False
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "john@example.com"


@pytest.mark.asyncio
async def test_login_user(client: AsyncClient):
    # Предварительно создаём пользователя в базе данных
    password_hash = get_password_hash("password123")
    await User.create(
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
        password_hash=password_hash,
        is_admin=False
    )
    response = await client.post("/login", json={
        "email": "jane@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    cookies = response.cookies
    assert "access_token" in cookies


@pytest.mark.asyncio
async def test_get_current_user_data(client: AsyncClient):
    # Входим и получаем cookies
    response = await client.post("/login", json={
        "email": "jane@example.com",
        "password": "password123"
    })
    cookies = response.cookies
    # Отправляем запрос с cookies
    response = await client.get("/users/current", cookies=cookies)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "jane@example.com"
