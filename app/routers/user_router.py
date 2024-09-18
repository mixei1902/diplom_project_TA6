from fastapi import APIRouter, Depends, HTTPException, status, Response

from app.core.auth import create_access_token, get_current_user
from app.schemas.user_schema import UserResponse, CreateUser, UpdateUser, LoginModel, UsersListResponseModel
from app.services.user_service import UserService

router = APIRouter()


# Эндпоинт для регистрации пользователя
@router.post("/register", response_model=UserResponse)
async def register_user(user: CreateUser):
    return await UserService.create_user_service(user)


# Эндпоинт для входа пользователя
@router.post("/login")
async def login_user(login_data: LoginModel, response: Response):
    user = await UserService.authenticate_user(login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверные учетные данные"
        )
    access_token = create_access_token(data={"sub": user.email})
    # Устанавливаем JWT-токен в cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite='lax'
    )
    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer"
    }


# Эндпоинт для выхода пользователя
@router.get("/logout")
async def logout_user(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}


# Получение данных текущего пользователя
@router.get("/current", response_model=UserResponse)
async def get_current_user_data(current_user=Depends(get_current_user)):
    return current_user


# Обновление данных текущего пользователя
@router.patch("/current", response_model=UserResponse)
async def update_current_user(
        user_data: UpdateUser,
        current_user=Depends(get_current_user)
):
    updated_user = await UserService.update_user(current_user.id, user_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


# Получение списка пользователей с пагинацией (для всех пользователей)
@router.get("/users", response_model=UsersListResponseModel)
async def get_users(
        page: int,
        size: int,
        current_user=Depends(get_current_user)
):
    users, total = await UserService.get_users(page=page, size=size)
    # Формируем список с ограниченной информацией
    users_data = [
        {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email
        }
        for user in users
    ]
    return {
        "data": users_data,
        "meta": {
            "pagination": {
                "total": total,
                "page": page,
                "size": size
            }
        }
    }
