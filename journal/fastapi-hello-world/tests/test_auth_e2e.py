import pytest
from httpx import AsyncClient

from tests.test_auth import auth_header, login_form, register_payload
from tests.test_posts import post_payload


@pytest.mark.asyncio
async def test_register_login_create_fetch_and_delete_post(
    async_client: AsyncClient,
) -> None:
    register_response = await async_client.post(
        "/auth/register",
        json=register_payload(),
    )
    assert register_response.status_code == 201
    user_id = register_response.json()["id"]

    login_response = await async_client.post("/auth/login", data=login_form())
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    me_response = await async_client.get("/users/me", headers=auth_header(token))
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "ada@example.com"

    create_post_response = await async_client.post(
        "/posts",
        json=post_payload(user_id=user_id, title="E2E testing pyramid"),
        headers=auth_header(token),
    )
    assert create_post_response.status_code == 201
    post_id = create_post_response.json()["id"]

    get_post_response = await async_client.get(f"/posts/{post_id}")
    assert get_post_response.status_code == 200
    assert get_post_response.json()["title"] == "E2E testing pyramid"

    delete_post_response = await async_client.delete(f"/posts/{post_id}")
    get_deleted_response = await async_client.get(f"/posts/{post_id}")

    assert delete_post_response.status_code == 204
    assert get_deleted_response.status_code == 404
