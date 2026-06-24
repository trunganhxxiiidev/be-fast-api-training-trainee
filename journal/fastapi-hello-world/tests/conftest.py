import asyncio
from collections.abc import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.config import Settings
from app.db import get_session
from app.main import create_app
from app.models import Base


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_local = async_sessionmaker(engine, expire_on_commit=False)

    async def create_tables() -> None:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    async def dispose_engine() -> None:
        await engine.dispose()

    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        async with session_local() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    asyncio.run(create_tables())
    app = create_app(
        Settings(
            app_version="9.9.9",
            log_level="INFO",
            database_url="sqlite+aiosqlite://",
            database_echo=False,
            jwt_secret="test-secret-key-with-at-least-32-bytes",
        )
    )
    app.dependency_overrides[get_session] = override_get_session
    app.state.test_session_local = session_local

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    asyncio.run(dispose_engine())
