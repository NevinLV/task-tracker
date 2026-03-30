import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Dict, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.auth import router as auth_router
from app.api.tasks import router as tasks_router
from app.api.upload import router as upload_router
from app.api.users import router as users_router
from app.config import settings
from app.database import Base, engine
from app.schema_patch import apply_schema_patches

logger = logging.getLogger(__name__)

Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)


async def _init_db_with_retries() -> None:
    """Несколько попыток: Postgres в Docker иногда принимает соединение через 1–5 с после `compose up`."""
    last: Optional[Exception] = None
    for attempt in range(1, 9):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                await apply_schema_patches(conn)
            return
        except Exception as e:
            last = e
            logger.warning(
                "Подключение к БД не удалось (попытка %s/8): %s",
                attempt,
                e,
            )
            await asyncio.sleep(1.5)
    assert last is not None
    logger.exception("Не удалось подключиться к базе данных после повторных попыток")
    raise RuntimeError(
        "PostgreSQL недоступен. Убедитесь, что контейнер запущен: в корне проекта выполните "
        "`docker compose up -d`, проверьте `DATABASE_URL` в `backend/.env` (user/password/db как в "
        "`docker-compose.yml`) и что порт 5432 не занят другой службой."
    ) from last


@asynccontextmanager
async def lifespan(_: FastAPI):
    await _init_db_with_retries()
    yield


app = FastAPI(title="Task Tracker API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(tasks_router, prefix="/api")
app.include_router(upload_router, prefix="/api")

app.mount("/static/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}
