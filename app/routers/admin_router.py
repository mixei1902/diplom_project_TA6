from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import get_current_admin
from app.schemas.user_schema import (
    PrivateUserResponse,
    PrivateCreateUser,
    PrivateUpdateUser,
    UsersListResponseModel,
)
from app.services.user_service import UserService

router = APIRouter(tags=["admin"])


# Эндпоинт для получения списка пользователей с пагинацией
@router.get("", response_model=UsersListResponseModel)
async def get_users(
        page: int,
        size: int,
        current_user=Depends(get_current_admin)
):
    users, total = await UserService.get_users(page=page, size=size)
    return {
        "data": users,
        "meta": {
            "pagination": {
                "total": total,
                "page": page,
                "size": size
            }
        }
    }


# Эндпоинт для создания пользователя
@router.post("", response_model=PrivateUserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: PrivateCreateUser,
    current_user=Depends(get_current_admin)
):
    existing_user = await UserService.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    user = await UserService.create_user_service(user_data)
    return user


# Эндпоинт для получения информации о пользователе по ID
@router.get("/{pk}", response_model=PrivateUserResponse)
async def get_user(
        pk: int,
        current_user=Depends(get_current_admin)
):
    user = await UserService.get_user_by_id(pk)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


# Эндпоинт для обновления информации о пользователе
@router.patch("/{pk}", response_model=PrivateUserResponse)
async def update_user(
        pk: int,
        user_data: PrivateUpdateUser,
        current_user=Depends(get_current_admin)
):
    updated_user = await UserService.update_user(pk, user_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return updated_user


# Эндпоинт для удаления пользователя
@router.delete("/{pk}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        pk: int,
        current_user=Depends(get_current_admin)
):
    deleted = await UserService.delete_user(pk)
    if not deleted:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return
