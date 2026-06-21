from fastapi.testclient import TestClient
from datetime import datetime

from tests.test_users import user_payload


def post_payload(
    user_id: int = 1,
    title: str = "SQLAlchemy relationships",
) -> dict[str, object]:
    return {
        "user_id": user_id,
        "title": title,
        "summary": "Short SQLAlchemy note.",
        "body": "A post belongs to one user.",
        "published": True,
    }


def test_create_then_get_post(client: TestClient) -> None:
    client.post("/users", json=user_payload())

    create_response = client.post("/posts", json=post_payload())

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["id"] == 1
    assert created["user_id"] == 1
    assert created["title"] == "SQLAlchemy relationships"
    assert created["summary"] == "Short SQLAlchemy note."
    assert datetime.fromisoformat(created["published_at"])

    get_response = client.get("/posts/1")

    assert get_response.status_code == 200
    assert get_response.json() == created


def test_create_post_rejects_missing_user(client: TestClient) -> None:
    response = client.post("/posts", json=post_payload(user_id=999))

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "USER_NOT_FOUND"


def test_list_posts_uses_pagination(client: TestClient) -> None:
    client.post("/users", json=user_payload())
    client.post("/posts", json=post_payload(title="First post"))
    client.post("/posts", json=post_payload(title="Second post"))
    client.post("/posts", json=post_payload(title="Third post"))

    response = client.get("/posts?limit=2&offset=1")

    assert response.status_code == 200
    assert [post["title"] for post in response.json()] == [
        "Second post",
        "Third post",
    ]


def test_list_user_posts_uses_relationship_endpoint(client: TestClient) -> None:
    client.post("/users", json=user_payload("ada@example.com", "Ada Lovelace"))
    client.post("/users", json=user_payload("grace@example.com", "Grace Hopper"))
    client.post("/posts", json=post_payload(user_id=1, title="Ada post one"))
    client.post("/posts", json=post_payload(user_id=1, title="Ada post two"))
    client.post("/posts", json=post_payload(user_id=2, title="Grace post"))

    response = client.get("/users/1/posts")

    assert response.status_code == 200
    assert [post["title"] for post in response.json()] == [
        "Ada post one",
        "Ada post two",
    ]


def test_patch_post(client: TestClient) -> None:
    client.post("/users", json=user_payload())
    client.post("/posts", json=post_payload())

    response = client.patch("/posts/1", json={"title": "Updated title"})

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Updated title"
    assert body["updated_at"] is not None


def test_delete_post(client: TestClient) -> None:
    client.post("/users", json=user_payload())
    client.post("/posts", json=post_payload())

    delete_response = client.delete("/posts/1")
    get_response = client.get("/posts/1")

    assert delete_response.status_code == 204
    assert delete_response.content == b""
    assert get_response.status_code == 404
    assert get_response.json()["error"]["code"] == "POST_NOT_FOUND"
