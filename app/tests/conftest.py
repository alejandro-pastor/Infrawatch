from unittest.mock import patch, MagicMock
import pytest


@pytest.fixture(autouse=True)
def mock_redis():
    with patch("redis.Redis") as mock:
        mock_instance = MagicMock()
        mock_instance.incr.return_value = 42
        mock.return_value = mock_instance
        yield


@pytest.fixture(autouse=True)
def mock_db():
    with patch("psycopg2.connect") as mock:
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ["PostgreSQL 16 (Debian)"]
        mock.return_value.cursor.return_value = mock_cursor
        yield


@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    from main import app
    return TestClient(app)
