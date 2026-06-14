import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
from app.services import user_service


@pytest.fixture(autouse=True)
def reset_user_service() -> None:
    user_service.reset()


@pytest.fixture
def client() -> TestClient:
    app = create_app(Settings(app_version="9.9.9", log_level="INFO"))
    return TestClient(app)
