from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import charity_project_router, donation_router

app = FastAPI(
    title="QRKot - Благотворительный фонд поддержки котиков",
    description=(
        "API для управления целевыми проектами и пожертвованиями "
        "в фонде QRKot. Автоматическое инвестирование пожертвований "
        "в открытые проекты."
    ),
    version="1.0.0",
)

app.include_router(
    charity_project_router,
    prefix="/charity_project",
    tags=["Целевые проекты"],
)

app.include_router(
    donation_router,
    prefix="/donation",
    tags=["Пожертвования"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Корневой эндпоинт для проверки работоспособности."""
    return {
        "message": "Добро пожаловать в QRKot API!",
        "docs": "/docs",
        "status": "active"
    }


@app.get("/health")
async def health_check():
    """Эндпоинт для проверки состояния сервиса."""
    return {"status": "healthy"}
