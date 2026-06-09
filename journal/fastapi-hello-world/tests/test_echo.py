from datetime import datetime

from fastapi.testclient import TestClient


def test_echo_returns_message_and_timestamp(client: TestClient) -> None:
    response = client.post("/echo", json={"message": "hello FastAPI"})

    assert response.status_code == 200
    body = response.json()
    assert body["echo"] == "hello FastAPI"
    assert datetime.fromisoformat(body["received_at"])


def test_echo_rejects_missing_message(client: TestClient) -> None:
    response = client.post("/echo", json={})

    assert response.status_code == 422
    body = response.json()
    assert "detail" in body
    assert body["detail"][0]["loc"] == ["body", "message"]

