from types import SimpleNamespace

import jwt
import pytest

from app.config import get_settings
from app.security import hash_password
from app.services import auth_service


class FakeResult:
    def __init__(self, user: object | None) -> None:
        self.user = user

    def scalar_one_or_none(self) -> object | None:
        return self.user


class FakeSession:
    def __init__(self, user: object | None) -> None:
        self.user = user
        self.queries: list[object] = []

    async def execute(self, query: object) -> FakeResult:
        self.queries.append(query)
        return FakeResult(self.user)


@pytest.mark.asyncio
async def test_authenticate_user_accepts_valid_password_without_http_or_db() -> None:
    user = SimpleNamespace(
        id=7,
        email="ada@example.com",
        role="member",
        password_hash=hash_password("correct-horse-battery"),
    )
    session = FakeSession(user)

    authenticated = await auth_service.authenticate_user(
        session,
        email="ADA@example.com",
        password="correct-horse-battery",
    )

    assert authenticated is user
    assert len(session.queries) == 1


@pytest.mark.asyncio
async def test_authenticate_user_rejects_wrong_password_without_http_or_db() -> None:
    user = SimpleNamespace(
        id=7,
        email="ada@example.com",
        role="member",
        password_hash=hash_password("correct-horse-battery"),
    )

    authenticated = await auth_service.authenticate_user(
        FakeSession(user),
        email="ada@example.com",
        password="wrong-password",
    )

    assert authenticated is None


def test_issue_access_token_uses_user_identity_and_role() -> None:
    token = auth_service.issue_access_token(SimpleNamespace(id=42, role="admin"))

    payload = jwt.decode(
        token,
        get_settings().jwt_secret,
        algorithms=["HS256"],
    )

    assert payload["sub"] == "42"
    assert payload["role"] == "admin"
