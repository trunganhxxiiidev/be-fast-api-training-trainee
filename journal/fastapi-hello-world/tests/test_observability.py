from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def build_observability_app() -> FastAPI:
    app = create_app(
        Settings(
            environment="prod",
            log_level="INFO",
            database_url="sqlite+aiosqlite://",
            database_echo=False,
            jwt_secret="test-secret-key-with-at-least-32-bytes",
        ),
    )

    @app.get("/boom")
    async def boom() -> None:
        raise RuntimeError("forced observability failure")

    return app


def test_correlation_id_is_generated_when_missing() -> None:
    app = build_observability_app()

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.headers["X-Request-ID"]


def test_correlation_id_reuses_request_header() -> None:
    app = build_observability_app()

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/health", headers={"X-Request-ID": "my-id-123"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "my-id-123"


def test_unhandled_exception_logs_correlation_id(capsys) -> None:
    app = build_observability_app()

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/boom", headers={"X-Request-ID": "err-id-123"})

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "INTERNAL_ERROR",
            "message": "Something went wrong",
        },
    }
    assert response.headers["X-Request-ID"] == "err-id-123"

    captured = capsys.readouterr().out
    assert "unhandled_exception" in captured
    assert "err-id-123" in captured
    assert "RuntimeError" in captured
