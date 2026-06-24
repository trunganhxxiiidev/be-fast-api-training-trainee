import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import PostNotFoundError, UserNotFoundError
from app.schemas import PostCreate, PostReplace, PostUpdate
from app.services import post_service, user_service


async def create_user(db_session: AsyncSession) -> int:
    user = await user_service.create_user(
        db_session,
        email="ada@example.com",
        name="Ada Lovelace",
        password="correct-horse-battery",
    )
    return user.id


def make_post_payload(user_id: int, title: str = "SQLAlchemy relationships") -> PostCreate:
    return PostCreate(
        user_id=user_id,
        title=title,
        summary="Short SQLAlchemy note.",
        body="A post belongs to one user.",
        published=True,
    )


@pytest.mark.asyncio
async def test_create_then_get_post_through_service(db_session: AsyncSession) -> None:
    user_id = await create_user(db_session)

    created = await post_service.create_post(db_session, make_post_payload(user_id))
    fetched = await post_service.get_post(db_session, created.id)

    assert fetched.id == created.id
    assert fetched.user_id == user_id
    assert fetched.title == "SQLAlchemy relationships"


@pytest.mark.asyncio
async def test_create_post_rejects_missing_user(db_session: AsyncSession) -> None:
    with pytest.raises(UserNotFoundError):
        await post_service.create_post(db_session, make_post_payload(999))


@pytest.mark.asyncio
async def test_list_posts_uses_limit_and_offset(db_session: AsyncSession) -> None:
    user_id = await create_user(db_session)
    await post_service.create_post(db_session, make_post_payload(user_id, "First"))
    await post_service.create_post(db_session, make_post_payload(user_id, "Second"))
    await post_service.create_post(db_session, make_post_payload(user_id, "Third"))

    posts = await post_service.list_posts(db_session, limit=2, offset=1)

    assert [post.title for post in posts] == ["Second", "Third"]


@pytest.mark.asyncio
async def test_replace_post_can_move_to_another_existing_user(
    db_session: AsyncSession,
) -> None:
    first_user_id = await create_user(db_session)
    second_user = await user_service.create_user(
        db_session,
        email="grace@example.com",
        name="Grace Hopper",
        password="correct-horse-battery",
    )
    post = await post_service.create_post(db_session, make_post_payload(first_user_id))

    replaced = await post_service.replace_post(
        db_session,
        post.id,
        PostReplace(
            user_id=second_user.id,
            title="Moved post",
            summary="Moved summary.",
            body="The post has a different author.",
            published=False,
        ),
    )

    assert replaced.user_id == second_user.id
    assert replaced.title == "Moved post"
    assert replaced.published is False
    assert replaced.updated_at is not None


@pytest.mark.asyncio
async def test_update_post_rejects_missing_new_user(db_session: AsyncSession) -> None:
    user_id = await create_user(db_session)
    post = await post_service.create_post(db_session, make_post_payload(user_id))

    with pytest.raises(UserNotFoundError):
        await post_service.update_post(db_session, post.id, PostUpdate(user_id=999))


@pytest.mark.asyncio
async def test_update_post_changes_supplied_fields(db_session: AsyncSession) -> None:
    user_id = await create_user(db_session)
    post = await post_service.create_post(db_session, make_post_payload(user_id))

    updated = await post_service.update_post(
        db_session,
        post.id,
        PostUpdate(
            title="Updated title",
            summary="Updated summary.",
            body="Updated body.",
            published=False,
        ),
    )

    assert updated.title == "Updated title"
    assert updated.summary == "Updated summary."
    assert updated.body == "Updated body."
    assert updated.published is False
    assert updated.updated_at is not None


@pytest.mark.asyncio
async def test_delete_post_removes_row(db_session: AsyncSession) -> None:
    user_id = await create_user(db_session)
    post = await post_service.create_post(db_session, make_post_payload(user_id))

    await post_service.delete_post(db_session, post.id)

    with pytest.raises(PostNotFoundError):
        await post_service.get_post(db_session, post.id)
