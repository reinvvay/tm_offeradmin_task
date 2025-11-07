from typing import AsyncGenerator

from resources.settings import settings
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


engine = create_async_engine(settings.DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def provide_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


async def on_startup() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))


async def on_shutdown() -> None:
    await engine.dispose()
