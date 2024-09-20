import pytest
from httpx import AsyncClient

from app.db.models import User
from app.schemas.user_schema import LoginModel, CreateUser
from app.services.user_service import UserService



@pytest.mark.asyncio
async def test_admin_get_users(client: AsyncClient, initialize_db):
    # Создаем администратора
    admin_data = CreateUser(
        first_name="Admin8",
        last_name="User8",
        other_name=None,
        email="admin8@example.com",
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
        email="admin8@example.com",
        password="adminpassword8"
    )
    login_response = await client.post("/users/login", json=login_data.dict())
    assert login_response.status_code == 200
    tokens = login_response.json()
    access_token = tokens["access_token"]

    # Устанавливаем токен в cookies
    client.cookies.set("access_token", access_token)

    # Создаем нескольких пользователей для тестирования
    users_data = [
        {
            "first_name": "User8",
            "last_name": "Test8",
            "other_name": None,
            "email": "user8@example.com",
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
            "email": "user9@example.com",
            "phone": "2222222222",
            "birthday": "1992-02-02",
            "password": "user9password",
            "is_admin": False,
            "city": 3,
            "additional_info": None
        }
    ]

    for user_data in users_data:
        response = await client.post("/private/users", json=user_data)
        assert response.status_code == 201

    # Отправляем GET-запрос на получение списка пользователей
    response = await client.get("/private/users", params={"page": 1, "size": 10})
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "meta" in data
    assert data["meta"]["pagination"]["total"] >= 2
    assert len(data["data"]) >= 2

    # Проверяем, что в списке присутствуют созданные пользователи
    emails = [user["email"] for user in data["data"]]
    for user_data in users_data:
        assert user_data["email"] in emails



@pytest.mark.asyncio
async def test_admin_create_user(client: AsyncClient, initialize_db):
    # Создаем администратора
    admin_data = CreateUser(
        first_name="Admin",
        last_name="User",
        other_name=None,
        email="admin@example.com",
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
        email="admin@example.com",
        password="adminpassword"
    )
    login_response = await client.post("/users/login", json=login_data.dict())
    assert login_response.status_code == 200
    tokens = login_response.json()
    access_token = tokens["access_token"]

    # Устанавливаем токен в cookies
    client.cookies.set("access_token", access_token)

    # Данные для создания нового пользователя через администратора
    new_user_data = {
        "first_name": "Charlie",
        "last_name": "Chaplin",
        "other_name": None,
        "email": "charlie@example.com",
        "phone": "6666666666",
        "birthday": "1970-07-07",
        "password": "charliepassword",
        "is_admin": False,
        "city": 2,
        "additional_info": "Silent movie star"
    }

    # Отправляем POST-запрос на создание пользователя
    response = await client.post("/private/users", json=new_user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == new_user_data["email"]
    assert data["first_name"] == new_user_data["first_name"]

    # Проверяем, что пользователь создан в базе данных
    user = await User.get(email=new_user_data["email"])
    assert user is not None
    assert user.first_name == new_user_data["first_name"]



# @pytest.mark.asyncio
# async def test_non_admin_cannot_access_admin_endpoints(client: AsyncClient):
#     # Входим под обычным пользователем
#     response = await client.post("/login", json={
#         "email": "jane@example.com",
#         "password": "password123"
#     })
#     cookies = response.cookies
#     # Пытаемся получить доступ к административному эндпоинту
#     response = await client.get("/private/users?page=1&size=10", cookies=cookies)
#     assert response.status_code == 403