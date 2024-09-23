import uuid

import pytest

from app.schemas.user_schema import CreateUser, UpdateUser
from app.services.user_service import UserService


@pytest.mark.asyncio
async def test_authenticate_user_success(initialize_db):
    # Генерация уникального email для пользователя
    user_email = f"auth_success_{uuid.uuid4()}@example.com"

    # Данные пользователя
    user_data = CreateUser(
        first_name="Auth",
        last_name="Success",
        other_name=None,
        email=user_email,
        phone="1111111111",
        birthday="1990-01-01",
        password="authpassword",
        is_admin=False,
        city=1,
        additional_info=None
    )

    # Создаем пользователя через сервис
    user = await UserService.create_user_service(user_data)

    try:
        # Аутентификация пользователя
        authenticated_user = await UserService.authenticate_user(user_email, "authpassword")
        assert authenticated_user is not None
        assert authenticated_user.email == user_email
    finally:
        # Удаляем пользователя
        await UserService.delete_user(user.id)


@pytest.mark.asyncio
async def test_update_user_success(initialize_db):
    # Генерация уникального email для пользователя
    user_email = f"update_success_{uuid.uuid4()}@example.com"

    # Данные пользователя
    user_data = CreateUser(
        first_name="Update",
        last_name="Success",
        other_name=None,
        email=user_email,
        phone="3333333333",
        birthday="1992-03-03",
        password="updatepassword",
        is_admin=False,
        city=3,
        additional_info=None
    )

    # Создаем пользователя через сервис
    user = await UserService.create_user_service(user_data)

    try:
        # Данные для обновления
        update_data = UpdateUser(
            first_name="Updated",
            phone="4444444444"
        )

        # Обновляем пользователя
        updated_user = await UserService.update_user(user.id, update_data)
        assert updated_user is not None
        assert updated_user.first_name == "Updated"
        assert updated_user.phone == "4444444444"
    finally:
        # Удаляем пользователя
        await UserService.delete_user(user.id)


@pytest.mark.asyncio
async def test_update_user_nonexistent(initialize_db):
    # Попытка обновления несуществующего пользователя
    update_data = UpdateUser(
        first_name="Nonexistent",
        phone="5555555555"
    )
    updated_user = await UserService.update_user(9999, update_data)  # Предполагаемый несуществующий ID
    assert updated_user is None


@pytest.mark.asyncio
async def test_delete_user_nonexistent(initialize_db):
    # Попытка удаления несуществующего пользователя
    result = await UserService.delete_user(9999)  # Предполагаемый несуществующий ID
    assert result == False
