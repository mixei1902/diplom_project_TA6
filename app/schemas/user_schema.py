from datetime import date
from typing import Optional, List, Any

from pydantic import BaseModel, EmailStr


# Модель для информации о пользователе
class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    other_name: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    birthday: Optional[date] = None
    is_admin: bool

    class Config:
        orm_mode = True


# Модель для создания пользователя
class CreateUser(BaseModel):
    first_name: str
    last_name: str
    other_name: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    birthday: Optional[date] = None
    password: str
    is_admin: bool
    city: Optional[int] = None
    additional_info: Optional[str] = None

# Модель для обновления пользователя
class UpdateUser(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    other_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    birthday: Optional[date] = None
    city: Optional[int] = None
    additional_info: Optional[str] = None

    class Config:
        orm_mode = True

# Модель для авторизации пользователя
class LoginModel(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


# Модель для краткой информации о пользователе в списке
class UsersListElementModel(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr

    class Config:
        orm_mode = True


# Модель для метаданных пагинации
class PaginatedMetaDataModel(BaseModel):
    total: int
    page: int
    size: int


# Модель для ответа со списком пользователей
class UsersListResponseModel(BaseModel):
    data: List[UsersListElementModel]
    meta: dict


# Модель для создания пользователя (администратор)
class PrivateCreateUser(BaseModel):
    first_name: str
    last_name: str
    other_name: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    birthday: Optional[date] = None
    city: Optional[int] = None
    additional_info: Optional[str] = None
    is_admin: bool
    password: str


# Модель для обновления пользователя (администратор)
class PrivateUpdateUser(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    other_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    birthday: Optional[date] = None
    city: Optional[int] = None
    additional_info: Optional[str] = None
    is_admin: Optional[bool] = None
    password: Optional[str] = None

    class Config:
        orm_mode = True


# Модель для детального ответа о пользователе (администратор)
class PrivateUserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    other_name: Optional[str]
    email: EmailStr
    phone: Optional[str]
    birthday: Optional[date]
    city: Optional[int]
    additional_info: Optional[str]
    is_admin: bool

    class Config:
        orm_mode = True


class ErrorResponseModel(BaseModel):
    code: int
    message: str


class ValidationErrorResponseModel(BaseModel):
    code: int
    message: str
    details: List[Any]
