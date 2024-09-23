# Логика аутентификации (JWT-токены)
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, Request, HTTPException, status
from app.core.config import settings
from app.db.models import User
from app.services.user_service import UserService

# Настройка контекста для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Константы для JWT-токенов
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Создает JWT-токен для аутентификации пользователя.

    :param data: Данные для включения в токен
    :param expires_delta: Время жизни токена
    :return: Сгенерированный JWT-токен в виде строки
    """
    to_encode = data.copy()
    if expires_delta:
        # Если передано конкретное время жизни токена
        expire = datetime.utcnow() + expires_delta
    else:
        # Используем время жизни по умолчанию из настроек
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # Добавляем время истечения токена в данные для кодирования
    to_encode.update({"exp": expire})
    # Кодируем данные в JWT-токен
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет соответствие введенного пароля и хеша из базы данных.

    :param plain_password: Введенный пользователем пароль
    :param hashed_password: Хеш пароля из базы данных
    :return: True, если пароль верен, иначе False
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Генерирует хеш для заданного пароля.

    :param password: Пароль пользователя
    :return: Хеш пароля
    """
    return pwd_context.hash(password)


async def get_current_user(request: Request) -> User:
    """
    Извлекает текущего пользователя из JWT-токена, хранящегося в cookies.

    :param request: Объект запроса FastAPI
    :return: Объект пользователя из базы данных
    """
    # Извлекаем токен из cookies
    token = request.cookies.get("access_token")
    if not token:
        # Если токен отсутствует, выбрасываем исключение о неавторизованном доступе
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не аутентифицирован",
        )
    try:
        # Декодируем JWT-токен
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Извлекаем email пользователя из payload
        email: str = payload.get("sub")
        if email is None:
            # Если email отсутствует в токене, выбрасываем исключение
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверные учетные данные",
            )
    except JWTError:
        # Если произошла ошибка при декодировании токена, выбрасываем исключение
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные",
        )

    # Получаем пользователя из базы данных по email
    user = await UserService.get_user_by_email(email)
    if user is None:
        # Если пользователь не найден, выбрасываем исключение
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
        )
    return user


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Проверяет, что текущий пользователь является администратором.

    :param current_user: Объект текущего пользователя, полученный из зависимости get_current_user
    :return: Объект пользователя, если он является администратором
    """
    if not current_user.is_admin:
        # Если пользователь не администратор, выбрасываем исключение о запрете доступа
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен: только администраторы"
        )
    # Возвращаем объект текущего пользователя
    return current_user
