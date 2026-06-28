from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.exceptions import DuplicateEmailError, UserNotFoundError
from app.models import User
from app.schemas import UserCreate, UserReplace, UserUpdate
from app.security import hash_password


async def list_users(db: AsyncSession, limit: int, offset: int) -> list[User]:
    result = await db.execute(select(User).order_by(User.id).limit(limit).offset(offset))
    return list(result.scalars().all())


async def get_user(db: AsyncSession, user_id: int) -> User:
    user = await db.get(User, user_id)
    if user is None:
        raise UserNotFoundError()
    return user


async def get_user_with_posts(db: AsyncSession, user_id: int) -> User:
    result = await db.execute(
        select(User).options(selectinload(User.posts)).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise UserNotFoundError()
    return user


async def create_user(
    db: AsyncSession,
    payload: UserCreate | None = None,
    *,
    email: str | None = None,
    name: str | None = None,
    password: str | None = None,
    is_active: bool = True,
    role: str = "member",
) -> User:
    if payload is not None:
        email = str(payload.email)
        name = payload.name
        password = payload.password
        is_active = payload.is_active

    if email is None or name is None or password is None:
        raise ValueError("email, name, and password are required")

    normalized_email = _normalize_email(email)
    await _ensure_email_available(db, normalized_email)

    user = User(
        email=normalized_email,
        name=name,
        password_hash=hash_password(password),
        role=role,
        is_active=is_active,
    )
    db.add(user)
    await db.flush()
    return user


async def replace_user(
    db: AsyncSession,
    user_id: int,
    payload: UserReplace,
) -> User:
    user = await get_user(db, user_id)
    email = _normalize_email(payload.email)
    await _ensure_email_available(db, email, ignore_user_id=user.id)

    user.email = email
    user.name = payload.name
    user.password_hash = hash_password(payload.password)
    user.is_active = payload.is_active
    user.updated_at = datetime.now(UTC)
    await db.flush()
    return user


async def update_user(db: AsyncSession, user_id: int, payload: UserUpdate) -> User:
    user = await get_user(db, user_id)
    updates = payload.model_dump(exclude_unset=True)

    if "email" in updates:
        email = _normalize_email(updates["email"])
        await _ensure_email_available(db, email, ignore_user_id=user.id)
        user.email = email
    if "name" in updates:
        user.name = updates["name"]
    if "password" in updates:
        user.password_hash = hash_password(updates["password"])
    if "is_active" in updates:
        user.is_active = updates["is_active"]
    if updates:
        user.updated_at = datetime.now(UTC)
        await db.flush()
    return user


async def delete_user(db: AsyncSession, user_id: int) -> None:
    user = await get_user(db, user_id)
    await db.delete(user)
    await db.flush()


async def _ensure_email_available(
    db: AsyncSession,
    email: str,
    ignore_user_id: int | None = None,
) -> None:
    query = select(User).where(func.lower(User.email) == email)
    if ignore_user_id is not None:
        query = query.where(User.id != ignore_user_id)

    result = await db.execute(query)
    if result.scalar_one_or_none() is not None:
        raise DuplicateEmailError()


def _normalize_email(email: str) -> str:
    return str(email).lower()
