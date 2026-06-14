from fastapi.testclient import TestClient


def test_version_uses_app_settings(client: TestClient) -> None:
    response = client.get("/version")

    assert response.status_code == 200
    assert response.json() == {"version": "9.9.9"}


def test_version_rejects_post(client: TestClient) -> None:
    response = client.post("/version")

    assert response.status_code == 405
    assert response.json()["error"]["code"] == "METHOD_NOT_ALLOWED"
