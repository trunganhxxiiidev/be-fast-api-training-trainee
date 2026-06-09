import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


@pytest.fixture
def client() -> TestClient:
    app = create_app(Settings(app_version="9.9.9", log_level="INFO"))
    return TestClient(app)

