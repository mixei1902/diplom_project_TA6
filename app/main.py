from fastapi import FastAPI

from app.db.database import init_db, close_db
from app.routers import user_router

app = FastAPI(
    title="Сервис для хранения данных о пользователях",
    description="API для управления пользователями и их данными",
    version="1.0.0"
)


@app.on_event("startup")
async def startup():
    await init_db()


@app.on_event("shutdown")
async def shutdown():
    await close_db()


@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(user_router.router)