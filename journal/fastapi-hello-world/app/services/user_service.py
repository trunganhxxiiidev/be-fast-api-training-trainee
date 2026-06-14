from dataclasses import dataclass
from datetime import UTC, datetime

from app.exceptions import DuplicateEmailError, UserNotFoundError
from app.schemas import UserCreate, UserReplace, UserUpdate


@dataclass
class UserRecord:
    id: int
    email: str
    name: str
    password: str
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None


class InMemoryUserService:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self._users: dict[int, UserRecord] = {}
        self._next_id = 1

    def list_users(self, limit: int, offset: int) -> list[UserRecord]:
        users = sorted(self._users.values(), key=lambda user: user.id)
        return users[offset : offset + limit]

    def get_user(self, user_id: int) -> UserRecord:
        user = self._users.get(user_id)
        if user is None:
            raise UserNotFoundError()
        return user

    def create_user(self, payload: UserCreate) -> UserRecord:
        email = self._normalize_email(payload.email)
        self._ensure_email_available(email)

        user = UserRecord(
            id=self._next_id,
            email=email,
            name=payload.name,
            password=payload.password,
            is_active=payload.is_active,
            created_at=datetime.now(UTC),
        )
        self._users[user.id] = user
        self._next_id += 1
        return user

    def replace_user(self, user_id: int, payload: UserReplace) -> UserRecord:
        user = self.get_user(user_id)
        email = self._normalize_email(payload.email)
        self._ensure_email_available(email, ignore_user_id=user.id)

        user.email = email
        user.name = payload.name
        user.password = payload.password
        user.is_active = payload.is_active
        user.updated_at = datetime.now(UTC)
        return user

    def update_user(self, user_id: int, payload: UserUpdate) -> UserRecord:
        user = self.get_user(user_id)
        updates = payload.model_dump(exclude_unset=True)

        if "email" in updates:
            email = self._normalize_email(updates["email"])
            self._ensure_email_available(email, ignore_user_id=user.id)
            user.email = email
        if "name" in updates:
            user.name = updates["name"]
        if "password" in updates:
            user.password = updates["password"]
        if "is_active" in updates:
            user.is_active = updates["is_active"]
        if updates:
            user.updated_at = datetime.now(UTC)
        return user

    def delete_user(self, user_id: int) -> None:
        self.get_user(user_id)
        del self._users[user_id]

    def _ensure_email_available(
        self,
        email: str,
        ignore_user_id: int | None = None,
    ) -> None:
        for user in self._users.values():
            if user.id != ignore_user_id and user.email == email:
                raise DuplicateEmailError()

    @staticmethod
    def _normalize_email(email: str) -> str:
        return str(email).lower()


user_service = InMemoryUserService()
