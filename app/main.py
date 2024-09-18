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
    # Логируем подробности ошибки
    logger.error(f"Internal Server Error: {repr(exc)}")
    # Возвращаем ответ в формате, указанном в спецификации
    return JSONResponse(
        status_code=500,
        content={"message": "что-то пошло не так, мы уже исправляем эту ошибку"},
    )


# Обработчик ошибок для ошибок валидации данных (RequestValidationError)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Логируем подробности ошибки
    logger.warning(f"Validation Error: {exc.errors()}")
    # Возвращаем ответ в формате, указанном в спецификации
    return JSONResponse(
        status_code=422,
        content={
            "code": 422,
            "message": "Ошибка валидации данных",
            "details": exc.errors()
        },
    )


# Обработчик ошибок, если запись не найдена (DoesNotExist)
@app.exception_handler(DoesNotExist)
async def does_not_exist_handler(request: Request, exc: DoesNotExist):
    # Логируем подробности ошибки
    logger.warning(f"Entity Not Found: {repr(exc)}")
    # Возвращаем ответ в формате, указанном в спецификации
    return JSONResponse(
        status_code=404,
        content={
            "code": 404,
            "message": "Объект не найден"
        },
    )


# Обработчик ошибок для JWT авторизации (JWTError)
@app.exception_handler(JWTError)
async def jwt_error_handler(request: Request, exc: JWTError):
    # Логируем подробности ошибки
    logger.warning(f"JWT Error: {repr(exc)}")
    # Возвращаем ответ в формате, указанном в спецификации
    return JSONResponse(
        status_code=401,
        content={
            "code": 401,
            "message": "Ошибка авторизации. Неверный токен."
        },
    )


# Обработчик ошибок авторизации и прав доступа (HTTPException)
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Логируем подробности ошибки
    logger.warning(f"HTTP Exception: {exc.detail}")
    # Возвращаем ответ в формате, указанном в спецификации
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail
        },
    )


# Подключение роутеров
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
