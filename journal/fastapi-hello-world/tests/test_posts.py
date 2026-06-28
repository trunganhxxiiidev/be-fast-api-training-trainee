from datetime import datetime

from fastapi.testclient import TestClient

from app.routes.posts import POST_CACHE_TTL_SECONDS, post_cache_key
from app.schemas import PostOut
from tests.conftest import FakeRedis
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


def test_get_post_populates_cache_on_miss(
    client: TestClient,
    fake_redis: FakeRedis,
) -> None:
    client.post("/users", json=user_payload())
    create_response = client.post("/posts", json=post_payload())
    created = create_response.json()

    response = client.get("/posts/1")

    assert response.status_code == 200
    assert response.json() == created
    key = post_cache_key(1)
    assert fake_redis.get_calls[-1] == key
    assert key in fake_redis.data
    assert fake_redis.ttls[key] == POST_CACHE_TTL_SECONDS


def test_get_post_returns_cached_value_without_db(
    client: TestClient,
    fake_redis: FakeRedis,
) -> None:
    cached_post = PostOut(
        id=99,
        user_id=99,
        title="Cached post",
        summary="From Redis",
        body="This response did not touch the database.",
        published=True,
        published_at=datetime.fromisoformat("2026-06-28T08:00:00+00:00"),
        created_at=datetime.fromisoformat("2026-06-28T08:00:00+00:00"),
        updated_at=None,
    )
    fake_redis.data[post_cache_key(99)] = cached_post.model_dump_json()

    response = client.get("/posts/99")

    assert response.status_code == 200
    assert response.json()["title"] == "Cached post"
    assert fake_redis.set_calls == []


def test_get_post_ignores_old_cache_version(
    client: TestClient,
    fake_redis: FakeRedis,
) -> None:
    client.post("/users", json=user_payload())
    create_response = client.post("/posts", json=post_payload(title="Current post"))
    created = create_response.json()
    old_cached_post = PostOut(
        id=1,
        user_id=1,
        title="Old cached post",
        summary="Old version",
        body="This old cache entry should be ignored.",
        published=True,
        published_at=datetime.fromisoformat("2026-06-28T08:00:00+00:00"),
        created_at=datetime.fromisoformat("2026-06-28T08:00:00+00:00"),
        updated_at=None,
    )
    fake_redis.data["v0:post:1"] = old_cached_post.model_dump_json()

    response = client.get("/posts/1")

    assert response.status_code == 200
    assert response.json() == created
    assert response.json()["title"] == "Current post"
    assert fake_redis.get_calls[-1] == post_cache_key(1)
    assert "v0:post:1" in fake_redis.data
    assert post_cache_key(1) in fake_redis.data


def test_patch_post_invalidates_cache(
    client: TestClient,
    fake_redis: FakeRedis,
) -> None:
    client.post("/users", json=user_payload())
    client.post("/posts", json=post_payload())
    client.get("/posts/1")
    key = post_cache_key(1)
    assert key in fake_redis.data

    patch_response = client.patch("/posts/1", json={"title": "Updated title"})

    assert patch_response.status_code == 200
    assert key not in fake_redis.data
    assert fake_redis.delete_calls[-1] == key

    get_response = client.get("/posts/1")

    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Updated title"
    assert key in fake_redis.data


def test_put_post_invalidates_cache(
    client: TestClient,
    fake_redis: FakeRedis,
) -> None:
    client.post("/users", json=user_payload())
    client.post("/posts", json=post_payload())
    client.get("/posts/1")
    key = post_cache_key(1)
    assert key in fake_redis.data

    put_response = client.put("/posts/1", json=post_payload(title="Replaced title"))

    assert put_response.status_code == 200
    assert key not in fake_redis.data
    assert fake_redis.delete_calls[-1] == key

    get_response = client.get("/posts/1")

    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Replaced title"
    assert key in fake_redis.data


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


def test_delete_post_invalidates_cache(
    client: TestClient,
    fake_redis: FakeRedis,
) -> None:
    client.post("/users", json=user_payload())
    client.post("/posts", json=post_payload())
    client.get("/posts/1")
    key = post_cache_key(1)
    assert key in fake_redis.data

    response = client.delete("/posts/1")

    assert response.status_code == 204
    assert key not in fake_redis.data
    assert fake_redis.delete_calls[-1] == key
