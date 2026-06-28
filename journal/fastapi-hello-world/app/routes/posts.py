from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.db import SessionDep
from app.deps import pagination
from app.redis import RedisDep
from app.schemas import PostCreate, PostOut, PostReplace, PostUpdate
from app.services import post_service

router = APIRouter(prefix="/posts", tags=["posts"])
POST_CACHE_TTL_SECONDS = 300
POST_CACHE_VERSION = "v1"


def post_cache_key(post_id: int) -> str:
    return f"{POST_CACHE_VERSION}:post:{post_id}"


def to_post_out(post: object) -> PostOut:
    return PostOut.model_validate(post)


@router.post("", response_model=PostOut, status_code=status.HTTP_201_CREATED)
async def create_post(payload: PostCreate, db: SessionDep) -> PostOut:
    post = await post_service.create_post(db, payload)
    return to_post_out(post)


@router.get("", response_model=list[PostOut])
async def list_posts(
    page: Annotated[tuple[int, int], Depends(pagination)],
    db: SessionDep,
) -> list[PostOut]:
    limit, offset = page
    posts = await post_service.list_posts(db, limit=limit, offset=offset)
    return [to_post_out(post) for post in posts]


@router.get("/{post_id}", response_model=PostOut)
async def get_post(post_id: int, db: SessionDep, redis: RedisDep) -> PostOut:
    cached = await redis.get(post_cache_key(post_id))
    if cached is not None:
        return PostOut.model_validate_json(cached)

    post = await post_service.get_post(db, post_id)
    post_out = to_post_out(post)
    await redis.set(
        post_cache_key(post_id),
        post_out.model_dump_json(),
        ex=POST_CACHE_TTL_SECONDS,
    )
    return post_out


@router.put("/{post_id}", response_model=PostOut)
async def replace_post(
    post_id: int,
    payload: PostReplace,
    db: SessionDep,
    redis: RedisDep,
) -> PostOut:
    post = await post_service.replace_post(db, post_id, payload)
    await redis.delete(post_cache_key(post_id))
    return to_post_out(post)


@router.patch("/{post_id}", response_model=PostOut)
async def update_post(
    post_id: int,
    payload: PostUpdate,
    db: SessionDep,
    redis: RedisDep,
) -> PostOut:
    post = await post_service.update_post(db, post_id, payload)
    await redis.delete(post_cache_key(post_id))
    return to_post_out(post)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: SessionDep, redis: RedisDep) -> None:
    await post_service.delete_post(db, post_id)
    await redis.delete(post_cache_key(post_id))
