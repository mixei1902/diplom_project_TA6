from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.auth import create_access_token
from app.schemas.user_schema import UserResponse, CreateUser, UpdateUser, Token
from app.services.user_service import UserService
router = APIRouter()


# Эндпоинт для регистрации пользователя
@router.post("/register", response_model=UserResponse)
async def register_user(user: CreateUser):
    return await UserService.create_user_service(user)


# Эндпоинт для логина пользователя
@router.post("/login", response_model=Token)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await UserService.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


# Получение данных текущего пользователя
@router.get("/users/current", response_model=UserResponse)
async def get_current_user_data(current_user: UserResponse = Depends(UserService.get_current_user)):
    return current_user


# Получение данных пользователя по ID (доступ для администратора)
@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, current_user: UserResponse = Depends(UserService.get_current_user)):
    user = await UserService.get_user_by_id_service(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


# Обновление данных пользователя
@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user: UpdateUser, current_user: UserResponse = Depends(UserService.get_current_user)):
    updated_user = await UserService.update_user_service(user_id, user)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated_user


# Удаление пользователя
@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, current_user: UserResponse = Depends(UserService.get_current_user)):
    deleted = await UserService.delete_user_service(user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
