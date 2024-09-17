from typing import Optional, List, Tuple

from fastapi import HTTPException, Request
from jose import JWTError, jwt
from passlib.hash import bcrypt
from tortoise.exceptions import DoesNotExist

from app.core.config import settings
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
            update_data = user_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(user, field, value)
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
    async def get_current_user(request: Request) -> User:
        """
        Извлекает текущего пользователя из JWT-токена, хранящегося в cookies.
        """
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(
                status_code=401,
                detail="Not authenticated",
            )
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            email: str = payload.get("sub")
            if email is None:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid authentication credentials",
                )
        except JWTError:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
            )

        user = await User.get(email=email)
        if user is None:
            raise HTTPException(
                status_code=401,
                detail="User not found",
            )
        return user

    @staticmethod
    async def authenticate_user(email: str, password: str) -> Optional[User]:
        """
        Аутентифицирует пользователя по email и паролю.
        """
        try:
            user = await User.get(email=email)
            if not bcrypt.verify(password, user.password_hash):
                return None
            return user
        except DoesNotExist:
            return None

    @staticmethod
    async def get_users(page: int, size: int) -> Tuple[List[User], int]:
        """
        Получает список пользователей с пагинацией.
        """
        total = await User.all().count()
        users = await User.all().offset((page - 1) * size).limit(size)
        return users, total

    async def get_user_by_email(email: str) -> Optional[User]:
        """
        Получает пользователя по его email.

        :param email: Электронная почта пользователя
        :return: Объект пользователя или None, если пользователь не найден
        """
        try:
            return await User.get(email=email)
        except DoesNotExist:
            return None

    @staticmethod
    async def is_admin(user: User) -> bool:
        """
        Проверяет, является ли пользователь администратором.
        """
        return user.is_admin
