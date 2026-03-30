from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=120)
    last_name: Optional[str] = Field(None, max_length=120)
    hourly_rate: Optional[Decimal] = Field(None, ge=Decimal("0"))


class PasswordChange(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class TaskIdsBody(BaseModel):
    task_ids: List[UUID] = Field(min_length=1)


class TimeMoneySummary(BaseModel):
    total_seconds: int
    hourly_rate: str
    total_amount: str
