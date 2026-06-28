from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.db import get_session


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_rejects_post(client: TestClient) -> None:
    response = client.post("/health")

    assert response.status_code == 405
    assert response.json()["error"]["code"] == "METHOD_NOT_ALLOWED"


def test_ready_returns_ok_when_db_responds(client: TestClient) -> None:
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_returns_503_when_db_is_unavailable(client: TestClient) -> None:
    class BrokenSession:
        async def execute(self, _statement):
            raise SQLAlchemyError("database unavailable")

    async def override_get_session():
        yield BrokenSession()

    client.app.dependency_overrides[get_session] = override_get_session
    try:
        response = client.get("/ready")
    finally:
        client.app.dependency_overrides.pop(get_session, None)

    assert response.status_code == 503
    assert response.json() == {"status": "error"}
