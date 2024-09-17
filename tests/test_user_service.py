import asyncio
import sys

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
import pytest
from tortoise.contrib.test import finalizer, initializer


@pytest.fixture(scope="module", autouse=True)
def initialize_db():
    # Инициализируем Tortoise ORM
    initializer(
        ["app.db.models"],
        db_url="sqlite://:memory:",
        app_label="models",
    )
    yield
    finalizer()


from tortoise.exceptions import DoesNotExist

from app.services.user_service import UserService
from app.schemas.user_schema import CreateUser, UpdateUser


@pytest.mark.asyncio
async def test_create_user_service():
    user_data = CreateUser(
        first_name="Alice",
        last_name="Smith",
        email="alice@example.com",
        password="password123",
        is_admin=False,
        city="Wonderland",
        additional_info="test user",
    )
    user = await UserService.create_user_service(user_data)
    assert user.id is not None
    assert user.first_name == user_data.first_name
    assert user.email == user_data.email


@pytest.mark.asyncio
async def test_get_user_by_id():
    user_data = CreateUser(
        first_name="Bob",
        last_name="Brown",
        email="bob@example.com",
        password="password123",
        is_admin=False,
        city="Nowhere",
        additional_info="test user",
    )
    user = await UserService.create_user_service(user_data)

    fetched_user = await UserService.get_user_by_id(user.id)
    assert fetched_user is not None
    assert fetched_user.id == user.id
    assert fetched_user.email == user.email


@pytest.mark.asyncio
async def test_update_user():
    user_data = CreateUser(
        first_name="Charlie",
        last_name="Clark",
        email="charlie@example.com",
        password="password123",
        is_admin=False,
        city="Metropolis",
        additional_info="Testing updates",
    )
    user = await UserService.create_user_service(user_data)
    # Обновляем данные пользователя
    update_data = UpdateUser(
        first_name="Charles",
        email="charles@example.com",
    )
    updated_user = await UserService.update_user(user.id, update_data)
    assert updated_user.first_name == "Charles"
    assert updated_user.email == "charles@example.com"


@pytest.mark.asyncio
async def test_authenticate_user():
    user_data = CreateUser(
        first_name="Diana",
        last_name="Prince",
        email="diana@example.com",
        password="wonderwoman",
        is_admin=True,
        city="Themyscira",
        additional_info="Amazon warrior",
    )
    user = await UserService.create_user_service(user_data)
    # Аутентифицируем пользователя
    authenticated_user = await UserService.authenticate_user(
        email="diana@example.com", password="wonderwoman"
    )
    assert authenticated_user is not None
    assert authenticated_user.id == user.id
    # Попытка аутентификации с неверным паролем
    wrong_password_user = await UserService.authenticate_user(
        email="diana@example.com", password="wrongpassword"
    )
    assert wrong_password_user is None


@pytest.mark.asyncio
async def test_delete_user():
    user_data = CreateUser(
        first_name="Eve",
        last_name="Evans",
        email="eve@example.com",
        password="password123",
        is_admin=False,
        city="Unknown",
        additional_info="To be deleted",
    )
    user = await UserService.create_user_service(user_data)
    # Удаляем пользователя
    delete_result = await UserService.delete_user(user.id)
    assert delete_result is True
    # Проверяем, что пользователя больше нет
    with pytest.raises(DoesNotExist):
        await UserService.get_user_by_id(user.id)
