from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.db import SessionDep
from app.deps import pagination
from app.schemas import PostOut, UserCreate, UserOut, UserReplace, UserUpdate
from app.services import post_service, user_service

router = APIRouter(prefix="/users", tags=["users"])


def to_user_out(user: object) -> UserOut:
    return UserOut.model_validate(user)


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, db: SessionDep) -> UserOut:
    user = await user_service.create_user(db, payload)
    return to_user_out(user)


@router.get("", response_model=list[UserOut])
async def list_users(
    page: Annotated[tuple[int, int], Depends(pagination)],
    db: SessionDep,
) -> list[UserOut]:
    limit, offset = page
    users = await user_service.list_users(db, limit=limit, offset=offset)
    return [to_user_out(user) for user in users]


@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: int, db: SessionDep) -> UserOut:
    user = await user_service.get_user(db, user_id)
    return to_user_out(user)


@router.get("/{user_id}/posts", response_model=list[PostOut])
async def list_user_posts(
    user_id: int,
    page: Annotated[tuple[int, int], Depends(pagination)],
    db: SessionDep,
) -> list[PostOut]:
    limit, offset = page
    posts = await post_service.list_user_posts(db, user_id)
    return [PostOut.model_validate(post) for post in posts[offset : offset + limit]]


@router.put("/{user_id}", response_model=UserOut)
async def replace_user(user_id: int, payload: UserReplace, db: SessionDep) -> UserOut:
    user = await user_service.replace_user(db, user_id, payload)
    return to_user_out(user)


@router.patch("/{user_id}", response_model=UserOut)
async def update_user(user_id: int, payload: UserUpdate, db: SessionDep) -> UserOut:
    user = await user_service.update_user(db, user_id, payload)
    return to_user_out(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: SessionDep) -> None:
    await user_service.delete_user(db, user_id)
