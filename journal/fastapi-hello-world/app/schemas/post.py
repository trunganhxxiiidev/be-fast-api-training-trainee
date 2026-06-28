from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PostCreate(BaseModel):
    user_id: int = Field(gt=0)
    title: str = Field(min_length=1, max_length=200)
    summary: str | None = Field(default=None, min_length=1, max_length=280)
    body: str = Field(min_length=1)
    published: bool = False


class PostReplace(PostCreate):
    pass


class PostUpdate(BaseModel):
    user_id: int | None = Field(default=None, gt=0)
    title: str | None = Field(default=None, min_length=1, max_length=200)
    summary: str | None = Field(default=None, min_length=1, max_length=280)
    body: str | None = Field(default=None, min_length=1)
    published: bool | None = None

    @field_validator("user_id", "title", "summary", "body", "published", mode="before")
    @classmethod
    def reject_explicit_null(cls, value: Any) -> Any:
        if value is None:
            raise ValueError("Field cannot be null")
        return value


class PostOut(BaseModel):
    id: int
    user_id: int
    title: str
    summary: str | None = None
    body: str
    published: bool
    published_at: datetime
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
