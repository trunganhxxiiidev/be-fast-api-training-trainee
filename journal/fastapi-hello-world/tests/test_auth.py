import asyncio
from datetime import timedelta

from fastapi.testclient import TestClient

from app.security import create_access_token
from app.services import user_service


def register_payload(
    email: str = "ada@example.com",
    name: str = "Ada Lovelace",
    password: str = "correct-horse-battery",
) -> dict[str, str]:
    return {
        "email": email,
        "name": name,
        "password": password,
    }


def login_form(
    email: str = "ada@example.com",
    password: str = "correct-horse-battery",
) -> dict[str, str]:
    return {
        "username": email,
        "password": password,
    }


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def create_admin_user(client: TestClient) -> None:
    async def create_admin() -> None:
        async with client.app.state.test_session_local() as session:
            await user_service.create_user(
                session,
                email="admin@example.com",
                name="Admin User",
                password="admin-correct-horse",
                role="admin",
            )
            await session.commit()

    asyncio.run(create_admin())


def test_register_login_and_get_me(client: TestClient) -> None:
    register_response = client.post("/auth/register", json=register_payload())

    assert register_response.status_code == 201
    registered = register_response.json()
    assert registered["email"] == "ada@example.com"
    assert registered["role"] == "member"
    assert "password" not in registered
    assert "password_hash" not in registered

    login_response = client.post("/auth/login", data=login_form())

    assert login_response.status_code == 200
    token_body = login_response.json()
    assert token_body["token_type"] == "bearer"
    assert token_body["access_token"]

    me_response = client.get(
        "/users/me",
        headers=auth_header(token_body["access_token"]),
    )

    assert me_response.status_code == 200
    assert me_response.json()["email"] == "ada@example.com"


def test_login_wrong_password_uses_generic_error(client: TestClient) -> None:
    client.post("/auth/register", json=register_payload())

    response = client.post("/auth/login", data=login_form(password="wrong-password"))

    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "UNAUTHORIZED",
            "message": "Incorrect email or password",
        }
    }


def test_get_me_without_token_returns_401(client: TestClient) -> None:
    response = client.get("/users/me")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_get_me_with_expired_token_returns_401(client: TestClient) -> None:
    client.post("/auth/register", json=register_payload())
    expired_token = create_access_token(
        user_id=1,
        role="member",
        expires_delta=timedelta(minutes=-1),
    )

    response = client.get("/users/me", headers=auth_header(expired_token))

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_member_cannot_delete_user(client: TestClient) -> None:
    client.post("/auth/register", json=register_payload())
    client.post(
        "/auth/register",
        json=register_payload("grace@example.com", "Grace Hopper"),
    )
    login_response = client.post("/auth/login", data=login_form())
    member_token = login_response.json()["access_token"]

    response = client.delete("/users/2", headers=auth_header(member_token))

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"


def test_admin_can_delete_user(client: TestClient) -> None:
    create_admin_user(client)
    client.post("/auth/register", json=register_payload("grace@example.com", "Grace"))
    login_response = client.post(
        "/auth/login",
        data=login_form("admin@example.com", "admin-correct-horse"),
    )
    admin_token = login_response.json()["access_token"]

    delete_response = client.delete("/users/2", headers=auth_header(admin_token))
    get_response = client.get("/users/2")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404
