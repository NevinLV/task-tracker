import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import List, Optional
from typing_extensions import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.database import get_db
from app.models.task import Task, TaskComment, TaskStatus, TimeEntry
from app.models.user import User
from app.schemas.comment import CommentAuthor, CommentCreate, CommentOut
from app.schemas.task import ManualTimeCreate, TaskCreate, TaskOut, TaskUpdate, TimeEntryOut
from app.schemas.user_profile import TaskIdsBody, TimeMoneySummary

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _author_public(u: User) -> CommentAuthor:
    parts: List[str] = []
    if u.first_name:
        parts.append(u.first_name.strip())
    if u.last_name:
        parts.append(u.last_name.strip())
    display = " ".join(parts) if parts else u.email
    avatar_url = f"/static/uploads/avatars/{u.avatar_filename}" if u.avatar_filename else None
    return CommentAuthor(
        id=str(u.id),
        first_name=u.first_name,
        last_name=u.last_name,
        avatar_url=avatar_url,
        display_name=display,
    )


def _comment_out(c: TaskComment, author: User) -> CommentOut:
    return CommentOut(
        id=str(c.id),
        user_id=str(c.user_id),
        body=c.body,
        created_at=c.created_at,
        author=_author_public(author),
    )


def _entry_duration(entry: TimeEntry) -> Optional[int]:
    if entry.ended_at is None:
        return None
    delta = entry.ended_at - entry.started_at
    return int(delta.total_seconds())


def _utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _compute_task_seconds(task: Task) -> int:
    total = 0
    now = datetime.now(timezone.utc)
    for e in task.time_entries:
        if e.ended_at is None:
            total += int((now - _utc(e.started_at)).total_seconds())
        else:
            total += _entry_duration(e) or 0
    return total


def _serialize_task(task: Task) -> TaskOut:
    total = 0
    now = datetime.now(timezone.utc)
    entries_out: List[TimeEntryOut] = []
    active_id: Optional[str] = None
    for e in task.time_entries:
        if e.ended_at is None:
            active_id = str(e.id)
            secs = int((now - _utc(e.started_at)).total_seconds())
            total += secs
            entries_out.append(
                TimeEntryOut(
                    id=str(e.id),
                    started_at=e.started_at,
                    ended_at=None,
                    duration_seconds=secs,
                )
            )
        else:
            d = _entry_duration(e) or 0
            total += d
            entries_out.append(
                TimeEntryOut(
                    id=str(e.id),
                    started_at=e.started_at,
                    ended_at=e.ended_at,
                    duration_seconds=d,
                )
            )
    return TaskOut(
        id=str(task.id),
        title=task.title,
        content_json=task.content_json,
        status=task.status,
        created_at=task.created_at,
        updated_at=task.updated_at,
        total_tracked_seconds=total,
        active_timer_entry_id=active_id,
        time_entries=entries_out,
    )


@router.get("", response_model=List[TaskOut])
async def list_tasks(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    date_from: Annotated[Optional[date], Query(description="Фильтр: created_at >= начало дня (UTC)")] = None,
    date_to: Annotated[Optional[date], Query(description="Фильтр: created_at < начало следующего дня (UTC)")] = None,
    status: Annotated[Optional[TaskStatus], Query(description="Фильтр по статусу")] = None,
) -> List[TaskOut]:
    q = select(Task).where(Task.user_id == user.id).options(selectinload(Task.time_entries))
    if status is not None:
        q = q.where(Task.status == status)
    if date_from is not None:
        start = datetime.combine(date_from, datetime.min.time(), tzinfo=timezone.utc)
        q = q.where(Task.created_at >= start)
    if date_to is not None:
        end = datetime.combine(date_to + timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc)
        q = q.where(Task.created_at < end)
    q = q.order_by(Task.updated_at.desc())
    result = await db.execute(q)
    tasks = result.scalars().unique().all()
    return [_serialize_task(t) for t in tasks]


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(
    body: TaskCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskOut:
    task = Task(
        user_id=user.id,
        title=body.title,
        content_json=body.content_json,
        status=body.status,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    await db.refresh(task, attribute_names=["time_entries"])
    return _serialize_task(task)


@router.post("/aggregate-time", response_model=TimeMoneySummary)
async def aggregate_time(
    body: TaskIdsBody,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TimeMoneySummary:
    await db.refresh(user, attribute_names=["hourly_rate"])
    unique_ids = list(dict.fromkeys(body.task_ids))
    result = await db.execute(
        select(Task)
        .where(Task.user_id == user.id, Task.id.in_(unique_ids))
        .options(selectinload(Task.time_entries))
    )
    rows = list(result.scalars().unique().all())
    if len(rows) != len(unique_ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Некоторые задачи не найдены")
    total_sec = 0
    for t in rows:
        total_sec += _compute_task_seconds(t)
    rate = user.hourly_rate if user.hourly_rate is not None else Decimal("0")
    amount = (Decimal(total_sec) / Decimal(3600)) * rate
    q = Decimal("0.01")
    amount = amount.quantize(q)
    return TimeMoneySummary(
        total_seconds=total_sec,
        hourly_rate=str(rate),
        total_amount=str(amount),
    )


@router.get("/{task_id}/comments", response_model=List[CommentOut])
async def list_comments(
    task_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> List[CommentOut]:
    tr = await db.execute(select(Task).where(Task.id == task_id, Task.user_id == user.id))
    if tr.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    r = await db.execute(
        select(TaskComment).where(TaskComment.task_id == task_id).order_by(desc(TaskComment.created_at))
    )
    comments = r.scalars().all()
    if not comments:
        return []
    user_ids = list({c.user_id for c in comments})
    ur = await db.execute(select(User).where(User.id.in_(user_ids)))
    users_map = {u.id: u for u in ur.scalars().all()}
    return [_comment_out(c, users_map[c.user_id]) for c in comments]


@router.post("/{task_id}/comments", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
async def add_comment(
    task_id: uuid.UUID,
    body: CommentCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CommentOut:
    tr = await db.execute(select(Task).where(Task.id == task_id, Task.user_id == user.id))
    task = tr.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    c = TaskComment(task_id=task.id, user_id=user.id, body=body.body)
    db.add(c)
    await db.commit()
    await db.refresh(c)
    return _comment_out(c, user)


@router.get("/{task_id}", response_model=TaskOut)
async def get_task(
    task_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskOut:
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == user.id).options(selectinload(Task.time_entries))
    )
    task = result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return _serialize_task(task)


@router.patch("/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: uuid.UUID,
    body: TaskUpdate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskOut:
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == user.id).options(selectinload(Task.time_entries))
    )
    task = result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if body.title is not None:
        task.title = body.title
    if body.content_json is not None:
        task.content_json = body.content_json
    if body.status is not None:
        task.status = body.status
    task.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(task)
    await db.refresh(task, attribute_names=["time_entries"])
    return _serialize_task(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    result = await db.execute(select(Task).where(Task.id == task_id, Task.user_id == user.id))
    task = result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    await db.delete(task)
    await db.commit()


@router.post("/{task_id}/time/start", response_model=TaskOut)
async def start_timer(
    task_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskOut:
    result = await db.execute(select(Task).where(Task.id == task_id, Task.user_id == user.id))
    task = result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    running = await db.execute(
        select(TimeEntry).where(TimeEntry.user_id == user.id, TimeEntry.ended_at.is_(None))
    )
    active = running.scalars().first()
    if active is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Stop the current timer before starting another",
        )

    entry = TimeEntry(task_id=task.id, user_id=user.id, started_at=datetime.now(timezone.utc))
    db.add(entry)
    await db.commit()
    result = await db.execute(
        select(Task).where(Task.id == task_id).options(selectinload(Task.time_entries))
    )
    task = result.scalar_one()
    return _serialize_task(task)


@router.post("/{task_id}/time/stop", response_model=TaskOut)
async def stop_timer(
    task_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskOut:
    result = await db.execute(
        select(TimeEntry).where(
            TimeEntry.task_id == task_id,
            TimeEntry.user_id == user.id,
            TimeEntry.ended_at.is_(None),
        )
    )
    entry = result.scalar_one_or_none()
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active timer for this task")

    entry.ended_at = datetime.now(timezone.utc)
    await db.commit()
    result = await db.execute(
        select(Task).where(Task.id == task_id).options(selectinload(Task.time_entries))
    )
    task = result.scalar_one()
    return _serialize_task(task)


@router.post("/{task_id}/time/manual", response_model=TaskOut)
async def add_manual_time(
    task_id: uuid.UUID,
    body: ManualTimeCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskOut:
    result = await db.execute(select(Task).where(Task.id == task_id, Task.user_id == user.id))
    task = result.scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    running = await db.execute(
        select(TimeEntry).where(TimeEntry.user_id == user.id, TimeEntry.ended_at.is_(None))
    )
    if running.scalars().first() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Stop the current timer before adding manual time",
        )

    ended_at = datetime.now(timezone.utc)
    started_at = ended_at - timedelta(minutes=body.minutes)
    entry = TimeEntry(task_id=task.id, user_id=user.id, started_at=started_at, ended_at=ended_at)
    db.add(entry)
    await db.commit()
    result = await db.execute(
        select(Task).where(Task.id == task_id).options(selectinload(Task.time_entries))
    )
    task = result.scalar_one()
    return _serialize_task(task)
