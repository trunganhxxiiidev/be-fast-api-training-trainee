from datetime import datetime

from fastapi.testclient import TestClient


def user_payload(
    email: str = "ada@example.com",
    name: str = "Ada Lovelace",
) -> dict[str, object]:
    return {
        "email": email,
        "name": name,
        "password": "correct-horse-battery",
        "is_active": True,
    }


def test_create_then_get_user(client: TestClient) -> None:
    create_response = client.post("/users", json=user_payload())

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["id"] == 1
    assert created["email"] == "ada@example.com"
    assert created["name"] == "Ada Lovelace"
    assert created["role"] == "member"
    assert created["is_active"] is True
    assert "password" not in created
    assert "password_hash" not in created
    assert datetime.fromisoformat(created["created_at"])

    get_response = client.get("/users/1")

    assert get_response.status_code == 200
    assert get_response.json() == created


def test_list_users_uses_pagination(client: TestClient) -> None:
    client.post("/users", json=user_payload("ada@example.com", "Ada Lovelace"))
    client.post("/users", json=user_payload("grace@example.com", "Grace Hopper"))
    client.post("/users", json=user_payload("katherine@example.com", "Katherine Johnson"))

    response = client.get("/users?limit=2&offset=1")

    assert response.status_code == 200
    body = response.json()
    assert [user["email"] for user in body] == [
        "grace@example.com",
        "katherine@example.com",
    ]


def test_create_user_rejects_duplicate_email(client: TestClient) -> None:
    client.post("/users", json=user_payload("ada@example.com"))

    response = client.post("/users", json=user_payload("ADA@example.com"))

    assert response.status_code == 409
    assert response.json() == {
        "error": {
            "code": "DUPLICATE_EMAIL",
            "message": "Email already exists",
        }
    }


def test_replace_user(client: TestClient) -> None:
    client.post("/users", json=user_payload())

    response = client.put(
        "/users/1",
        json=user_payload("grace@example.com", "Grace Hopper"),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == 1
    assert body["email"] == "grace@example.com"
    assert body["name"] == "Grace Hopper"
    assert body["updated_at"] is not None
    assert "password" not in body


def test_patch_user(client: TestClient) -> None:
    client.post("/users", json=user_payload())

    response = client.patch("/users/1", json={"name": "Countess Ada"})

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "ada@example.com"
    assert body["name"] == "Countess Ada"
    assert body["updated_at"] is not None


def test_get_user_returns_not_found(client: TestClient) -> None:
    response = client.get("/users/999")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "USER_NOT_FOUND",
            "message": "User not found",
        }
    }


def test_user_validation_uses_error_envelope(client: TestClient) -> None:
    response = client.post("/users", json={"email": "not-an-email"})

    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["error"]["details"][0]["loc"] == ["body", "email"]
