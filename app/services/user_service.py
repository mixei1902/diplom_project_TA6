from typing import Optional

from passlib.hash import bcrypt
from pydantic import EmailStr
from tortoise.exceptions import DoesNotExist

from app.db.models import User
from app.schemas.user_schema import CreateUser, UpdateUser


class UserService:
    """
    Класс для управления пользователями.
    """

    @staticmethod
    async def create_user_service(user_data: CreateUser) -> User:
        """
        Создает нового пользователя на основе переданных данных.
        """
        # Хеширование пароля
        hashed_password = bcrypt.hash(user_data.password)

        # Создание записи пользователя в базе данных
        user = await User.create(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            other_name=user_data.other_name,
            email=user_data.email,
            phone=user_data.phone,
            birthday=user_data.birthday,
            is_admin=user_data.is_admin,
            password_hash=hashed_password,
            city=user_data.city,
            additional_info=user_data.additional_info
        )
        return user

    @staticmethod
    async def get_user_by_id(user_id: int) -> Optional[User]:
        """
        Получает пользователя по его ID.
        """
        try:
            return await User.get(id=user_id)
        except DoesNotExist:
            return None

    @staticmethod
    async def update_user(user_id: int, user_data: UpdateUser) -> Optional[User]:
        """
        Обновляет данные пользователя на основе переданных данных.
        """
        user = await UserService.get_user_by_id(user_id)
        if user:
            # Обновление полей, если они предоставлены
            user.first_name = user_data.first_name or user.first_name
            user.last_name = user_data.last_name or user.last_name
            user.other_name = user_data.other_name or user.other_name
            user.email = user_data.email or user.email
            user.phone = user_data.phone or user.phone
            user.birthday = user_data.birthday or user.birthday
            await user.save()
            return user
        return None

    @staticmethod
    async def delete_user(user_id: int) -> bool:
        """
        Удаляет пользователя по его ID.
        """
        user = await UserService.get_user_by_id(user_id)
        if user:
            await user.delete()
            return True
        return False

    @staticmethod
    async def authenticate_user(email: EmailStr, password: str) -> Optional[User]:
        """
        Аутентифицирует пользователя по email и паролю.
        """
        try:
            user = await User.get(email=email)
            # Проверка пароля
            if bcrypt.verify(password, user.password_hash):
                return user
        except DoesNotExist:
            return None
        return None
