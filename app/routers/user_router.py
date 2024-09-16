from fastapi import APIRouter, HTTPException
from tortoise.contrib.pydantic import pydantic_model_creator

from app.db.models import User
from app.schemas.user_schema import CreateUser, UpdateUser, UserResponse
from app.services.user_service import create_user, update_user, get_user_by_id, delete_user

router = APIRouter()

User_Pydantic = pydantic_model_creator(User)  # создание модели из Tortoise ORM


@router.post("/users", response_model=UserResponse)
async def create_user_route(user: CreateUser):
    """
    Создать нового пользователя
    """
    created_user = await create_user(user)
    return created_user


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """
    Получить данные пользователя
    """
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user_route(user_id: int, user: UpdateUser):
    """
    Оновить данные пользователя
    """
    updated_user = await update_user(user_id, user)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@router.delete("/users/{user_id}")
async def delete_user_route(user_id: int):
    """
    Удалить пользователя
    """
    success = await delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}
