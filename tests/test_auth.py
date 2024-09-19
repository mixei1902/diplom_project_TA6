from datetime import datetime, timedelta

from jose import jwt

from app.core.auth import create_access_token
from app.core.auth import get_password_hash, verify_password
from app.core.config import settings


def test_create_access_token():
    data = {"sub": "test@example.com"}
    token = create_access_token(data)

    # Декодируем токен для проверки содержимого
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    assert payload["sub"] == "test@example.com"
    assert "exp" in payload

    # Проверяем время истечения токена
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    token_exp = datetime.fromtimestamp(payload["exp"])
    assert token_exp > datetime.utcnow()


def test_password_hashing_and_verification():
    password = "securepassword"
    hashed_password = get_password_hash(password)

    # Проверяем, что хешированный пароль отличается от исходного
    assert hashed_password != password

    # Проверяем, что функция verify_password возвращает True для правильного пароля
    assert verify_password(password, hashed_password) == True

    # Проверяем, что функция verify_password возвращает False для неправильного пароля
    assert verify_password("wrongpassword", hashed_password) == False
