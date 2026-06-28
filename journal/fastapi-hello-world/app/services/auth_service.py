from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.schemas import RegisterRequest
from app.security import create_access_token, verify_password
from app.services import user_service


async def register_user(db: AsyncSession, payload: RegisterRequest) -> User:
    return await user_service.create_user(
        db,
        email=str(payload.email),
        name=payload.name,
        password=payload.password,
    )


async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str,
) -> User | None:
    result = await db.execute(select(User).where(func.lower(User.email) == email.lower()))
    user = result.scalar_one_or_none()
    if user is None:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def issue_access_token(user: User) -> str:
    return create_access_token(user_id=user.id, role=user.role)
