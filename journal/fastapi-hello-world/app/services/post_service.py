from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import PostNotFoundError
from app.models import Post
from app.schemas import PostCreate, PostReplace, PostUpdate
from app.services import user_service


async def list_posts(db: AsyncSession, limit: int, offset: int) -> list[Post]:
    result = await db.execute(select(Post).order_by(Post.id).limit(limit).offset(offset))
    return list(result.scalars().all())


async def list_user_posts(db: AsyncSession, user_id: int) -> list[Post]:
    user = await user_service.get_user_with_posts(db, user_id)
    return list(user.posts)


async def get_post(db: AsyncSession, post_id: int) -> Post:
    post = await db.get(Post, post_id)
    if post is None:
        raise PostNotFoundError()
    return post


async def create_post(db: AsyncSession, payload: PostCreate) -> Post:
    await user_service.get_user(db, payload.user_id)

    post = Post(
        user_id=payload.user_id,
        title=payload.title,
        body=payload.body,
        published=payload.published,
    )
    db.add(post)
    await db.flush()
    return post


async def replace_post(
    db: AsyncSession,
    post_id: int,
    payload: PostReplace,
) -> Post:
    post = await get_post(db, post_id)
    await user_service.get_user(db, payload.user_id)

    post.user_id = payload.user_id
    post.title = payload.title
    post.body = payload.body
    post.published = payload.published
    post.updated_at = datetime.now(UTC)
    await db.flush()
    return post


async def update_post(db: AsyncSession, post_id: int, payload: PostUpdate) -> Post:
    post = await get_post(db, post_id)
    updates = payload.model_dump(exclude_unset=True)

    if "user_id" in updates:
        await user_service.get_user(db, updates["user_id"])
        post.user_id = updates["user_id"]
    if "title" in updates:
        post.title = updates["title"]
    if "body" in updates:
        post.body = updates["body"]
    if "published" in updates:
        post.published = updates["published"]
    if updates:
        post.updated_at = datetime.now(UTC)
        await db.flush()
    return post


async def delete_post(db: AsyncSession, post_id: int) -> None:
    post = await get_post(db, post_id)
    await db.delete(post)
    await db.flush()
