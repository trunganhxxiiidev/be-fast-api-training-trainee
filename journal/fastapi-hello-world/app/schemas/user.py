from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=100, examples=["Ada Lovelace"])
    password: str = Field(min_length=12, examples=["correct-horse-battery"])
    is_active: bool = True


class UserReplace(UserCreate):
    pass


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    name: str | None = Field(default=None, min_length=1, max_length=100)
    password: str | None = Field(default=None, min_length=12)
    is_active: bool | None = None

    @field_validator("email", "name", "password", "is_active", mode="before")
    @classmethod
    def reject_explicit_null(cls, value: Any) -> Any:
        if value is None:
            raise ValueError("Field cannot be null")
        return value


class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
