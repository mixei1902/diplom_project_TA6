# Логика работы с пользователями (CRUD операции, бизнес-логика)
from tortoise.exceptions import DoesNotExist

from app.db.models import User
from app.schemas.user_schema import CreateUser, UpdateUser


async def get_user_by_id(user_id: int):
    """
    Получить пользователя по id
    """
    try:
        return await User.get(id=user_id)
    except DoesNotExist:
        return None


async def create_user(user_data: CreateUser):
    """
    Создать нового пользователя
    """
    user = await User.create(**user_data.dict()) #ghtобразовываем объект в словарь
    return user


async def update_user(user_id: int, user_data: UpdateUser):
    """
    Обновление данных существующего пользователя
    """
    user = await get_user_by_id(user_id)
    if not user:
        return None
    await user.update_from_dict(user_data.dict(exclude_unset=True))
    await user.save()
    return user


async def delete_user(user_id: int):
    """
    Удалить пользователя по id
    """
    user = await get_user_by_id(user_id)
    if user:
        await user.delete()
        return True
    return False
