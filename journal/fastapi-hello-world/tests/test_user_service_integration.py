import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import DuplicateEmailError, UserNotFoundError
from app.models import Post
from app.schemas import PostCreate, UserCreate, UserReplace, UserUpdate
from app.services import post_service, user_service


@pytest.mark.asyncio
async def test_create_then_get_user_through_service(db_session: AsyncSession) -> None:
    created = await user_service.create_user(
        db_session,
        UserCreate(
            email="Ada@Example.com",
            name="Ada Lovelace",
            password="correct-horse-battery",
        ),
    )
    await db_session.commit()

    fetched = await user_service.get_user(db_session, created.id)

    assert fetched.email == "ada@example.com"
    assert fetched.name == "Ada Lovelace"
    assert fetched.password_hash != "correct-horse-battery"


@pytest.mark.asyncio
async def test_create_user_rejects_duplicate_email_case_insensitive(
    db_session: AsyncSession,
) -> None:
    await user_service.create_user(
        db_session,
        email="ada@example.com",
        name="Ada",
        password="correct-horse-battery",
    )

    with pytest.raises(DuplicateEmailError):
        await user_service.create_user(
            db_session,
            email="ADA@example.com",
            name="Other Ada",
            password="correct-horse-battery",
        )


@pytest.mark.asyncio
async def test_replace_user_updates_all_mutable_fields(
    db_session: AsyncSession,
) -> None:
    user = await user_service.create_user(
        db_session,
        email="ada@example.com",
        name="Ada",
        password="correct-horse-battery",
    )

    replaced = await user_service.replace_user(
        db_session,
        user.id,
        UserReplace(
            email="grace@example.com",
            name="Grace Hopper",
            password="another-correct-horse",
            is_active=False,
        ),
    )

    assert replaced.email == "grace@example.com"
    assert replaced.name == "Grace Hopper"
    assert replaced.is_active is False
    assert replaced.updated_at is not None


@pytest.mark.asyncio
async def test_update_user_ignores_empty_patch(db_session: AsyncSession) -> None:
    user = await user_service.create_user(
        db_session,
        email="ada@example.com",
        name="Ada",
        password="correct-horse-battery",
    )

    updated = await user_service.update_user(db_session, user.id, UserUpdate())

    assert updated.email == "ada@example.com"
    assert updated.updated_at is None


@pytest.mark.asyncio
async def test_delete_user_cascades_to_posts(db_session: AsyncSession) -> None:
    user = await user_service.create_user(
        db_session,
        email="ada@example.com",
        name="Ada",
        password="correct-horse-battery",
    )
    post = await post_service.create_post(
        db_session,
        PostCreate(
            user_id=user.id,
            title="Cascade check",
            summary="Delete the parent user.",
            body="The child post should be removed too.",
        ),
    )

    await user_service.delete_user(db_session, user.id)
    await db_session.commit()
    posts = await db_session.scalars(select(Post).where(Post.id == post.id))

    assert posts.one_or_none() is None


@pytest.mark.asyncio
async def test_get_user_missing_id_raises_not_found(db_session: AsyncSession) -> None:
    with pytest.raises(UserNotFoundError):
        await user_service.get_user(db_session, 404)
