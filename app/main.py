import logging

from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from jose import JWTError
from tortoise.exceptions import DoesNotExist

from app.db.database import init_db, close_db
from app.routers import user_router, admin_router

app = FastAPI(
    title="Сервис для хранения данных о пользователях",
    description="API для управления пользователями и их данными",
    version="1.0.0"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Обработчик ошибок для внутренних серверных ошибок
@app.exception_handler(Exception)
async def internal_server_error_handler(request: Request, exc: Exception):
    logger.error(f"Internal Server Error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "что-то пошло не так, мы уже исправляем эту ошибку"},
    )


# Обработчик ошибок для валидации данных (Pydantic)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation Error: {exc}")
    return JSONResponse(
        status_code=422,
        content={
            "message": "Ошибка валидации данных",
            "errors": exc.errors(),
        },
    )


# Обработчик ошибок, если запись не найдена (например, пользователь)
@app.exception_handler(DoesNotExist)
async def does_not_exist_handler(request: Request, exc: DoesNotExist):
    logger.warning(f"Entity Not Found: {exc}")
    return JSONResponse(
        status_code=404,
        content={"message": "Объект не найден"},
    )


# Обработчик ошибок для JWT авторизации
@app.exception_handler(JWTError)
async def jwt_error_handler(request: Request, exc: JWTError):
    logger.warning(f"JWT Error: {exc}")
    return JSONResponse(
        status_code=401,
        content={"message": "Ошибка авторизации. Неверный токен."},
    )


# Обработчик ошибок авторизации и прав доступа (HTTPException)
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"Authorization Error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )


app.include_router(user_router.router)
app.include_router(admin_router.router)


@app.on_event("startup")
async def startup():
    logger.info("Приложение запущено")
    await init_db()


@app.on_event("shutdown")
async def shutdown():
    logger.info("Приложение завершило работу")
    await close_db()
