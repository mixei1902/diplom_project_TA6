# Pydantic-модели для валидации данных пользователей
from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    first_name: str
    last_name: str
    other_name: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    birthday: Optional[date] = None


class CreateUser(UserBase):
    password: str
    city: Optional[int] = None
    additional_info: Optional[str] = None


class UpdateUser(UserBase):
    city: Optional[int] = None
    additional_info: Optional[str] = None


class UserResponse(UserBase):
    id: int
    is_admin: bool

    class Config:
        orm_mode = True
