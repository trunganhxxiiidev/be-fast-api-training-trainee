import hashlib
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.db import SessionDep
from app.schemas import RegisterRequest, TokenResponse, UserOut
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])
logger = structlog.get_logger("auth")


def login_identifier_fields(identifier: str) -> dict[str, str]:
    normalized = identifier.strip().lower()
    email_domain = normalized.rsplit("@", maxsplit=1)[-1] if "@" in normalized else "unknown"
    return {
        "email_hash": hashlib.sha256(normalized.encode("utf-8")).hexdigest(),
        "email_domain": email_domain,
    }


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
async def register(payload: RegisterRequest, db: SessionDep) -> UserOut:
    user = await auth_service.register_user(db, payload)
    return UserOut.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: SessionDep,
) -> TokenResponse:
    user = await auth_service.authenticate_user(
        db,
        email=form.username,
        password=form.password,
    )
    if user is None:
        logger.warning(
            "login_failed",
            **login_identifier_fields(form.username),
            reason="invalid_credentials",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info("login_succeeded", user_id=user.id)
    return TokenResponse(access_token=auth_service.issue_access_token(user))
