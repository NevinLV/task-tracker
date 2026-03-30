from __future__ import annotations

from typing import Any, AsyncGenerator, Dict

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

def _asyncpg_connect_args(url: str) -> Dict[str, Any]:
    """Локальный Postgres часто без SSL; на Windows asyncpg может обрывать рукопожатие без ssl=False."""
    args: Dict[str, Any] = {"timeout": 60}
    if any(h in url for h in ("localhost", "127.0.0.1", "::1")):
        args["ssl"] = False
    return args


engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
    connect_args=_asyncpg_connect_args(settings.database_url),
)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
