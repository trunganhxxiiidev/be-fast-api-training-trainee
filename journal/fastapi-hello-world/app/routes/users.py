from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.deps import pagination
from app.schemas import UserCreate, UserOut, UserReplace, UserUpdate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])


def to_user_out(user: object) -> UserOut:
    return UserOut.model_validate(user)


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate) -> UserOut:
    user = user_service.create_user(payload)
    return to_user_out(user)


@router.get("", response_model=list[UserOut])
def list_users(
    page: Annotated[tuple[int, int], Depends(pagination)],
) -> list[UserOut]:
    limit, offset = page
    users = user_service.list_users(limit=limit, offset=offset)
    return [to_user_out(user) for user in users]


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int) -> UserOut:
    user = user_service.get_user(user_id)
    return to_user_out(user)


@router.put("/{user_id}", response_model=UserOut)
def replace_user(user_id: int, payload: UserReplace) -> UserOut:
    user = user_service.replace_user(user_id, payload)
    return to_user_out(user)


@router.patch("/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserUpdate) -> UserOut:
    user = user_service.update_user(user_id, payload)
    return to_user_out(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int) -> None:
    user_service.delete_user(user_id)
