"""Добавляет колонки/таблицы в уже существующую БД (create_all их не трогает)."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection


async def apply_schema_patches(conn: AsyncConnection) -> None:
    await conn.execute(
        text("ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_filename VARCHAR(255)")
    )
    await conn.execute(
        text(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS hourly_rate NUMERIC(12, 2) NOT NULL DEFAULT 0"
        )
    )
    await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS first_name VARCHAR(120)"))
    await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_name VARCHAR(120)"))
    await conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS task_comments (
                id UUID PRIMARY KEY,
                task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                body TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
    )
    await conn.execute(
        text(
            "CREATE INDEX IF NOT EXISTS ix_task_comments_task_id ON task_comments (task_id)"
        )
    )
    await conn.execute(
        text(
            "CREATE INDEX IF NOT EXISTS ix_task_comments_user_id ON task_comments (user_id)"
        )
    )
