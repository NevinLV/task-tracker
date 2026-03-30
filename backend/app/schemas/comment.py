from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    body: str = Field(min_length=1, max_length=10000)


class CommentAuthor(BaseModel):
    id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    display_name: str


class CommentOut(BaseModel):
    id: str
    user_id: str
    body: str
    created_at: datetime
    author: CommentAuthor

    model_config = {"from_attributes": True}
