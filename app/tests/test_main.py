from unittest.mock import MagicMock
import main


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root_status(client):
    response = client.get("/")
    assert response.status_code == 200


def test_root_json_fields(client):
    response = client.get("/")
    data = response.json()
    assert "status" in data
    assert "total_api_requests" in data
    assert "database_connected" in data


def test_root_without_redis(client):
    original = main.redis_client.incr
    main.redis_client.incr = MagicMock(side_effect=Exception("Redis caído"))
    try:
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["total_api_requests"] == 0
    finally:
        main.redis_client.incr = original


def test_root_without_db(client):
    original = main.get_db_connection
    main.get_db_connection = MagicMock(side_effect=Exception("PostgreSQL caído"))
    try:
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["database_connected"] == "unavailable"
    finally:
        main.get_db_connection = original
