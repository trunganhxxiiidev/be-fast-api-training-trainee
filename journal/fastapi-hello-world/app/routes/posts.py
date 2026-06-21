from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.db import SessionDep
from app.deps import pagination
from app.schemas import PostCreate, PostOut, PostReplace, PostUpdate
from app.services import post_service

router = APIRouter(prefix="/posts", tags=["posts"])


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
async def get_post(post_id: int, db: SessionDep) -> PostOut:
    post = await post_service.get_post(db, post_id)
    return to_post_out(post)


@router.put("/{post_id}", response_model=PostOut)
async def replace_post(
    post_id: int,
    payload: PostReplace,
    db: SessionDep,
) -> PostOut:
    post = await post_service.replace_post(db, post_id, payload)
    return to_post_out(post)


@router.patch("/{post_id}", response_model=PostOut)
async def update_post(
    post_id: int,
    payload: PostUpdate,
    db: SessionDep,
) -> PostOut:
    post = await post_service.update_post(db, post_id, payload)
    return to_post_out(post)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: SessionDep) -> None:
    await post_service.delete_post(db, post_id)
