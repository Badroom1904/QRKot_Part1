import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.core.db import Base
from app.models import CharityProject, Donation


async def init_database():
    """Создаёт все таблицы в базе данных."""
    engine = create_async_engine(settings.DATABASE_URL)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("База данных успешно создана!")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_database())