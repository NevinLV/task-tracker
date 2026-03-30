from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.task import TaskStatus


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    content_json: Optional[str] = None
    status: TaskStatus = TaskStatus.familiarization


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content_json: Optional[str] = None
    status: Optional[TaskStatus] = None


class TimeEntryOut(BaseModel):
    id: str
    started_at: datetime
    ended_at: Optional[datetime]
    duration_seconds: Optional[int]

    model_config = {"from_attributes": True}


class ManualTimeCreate(BaseModel):
    minutes: int = Field(ge=1, le=24 * 60)


class TaskOut(BaseModel):
    id: str
    title: str
    content_json: Optional[str]
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    total_tracked_seconds: int = 0
    active_timer_entry_id: Optional[str] = None
    time_entries: List[TimeEntryOut] = []

    model_config = {"from_attributes": True}
