from app.server import app
from app.version import __version__
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    # Check key fields as routes list can be dynamic or ordered differently
    data = response.json()
    assert data["status"] == "online"
    assert data["version"] == __version__


def test_static_mount():
    # Attempt to fetch a non-existent static file -> 404
    # Just verifies the mount point exists and handles request
    response = client.get("/static/nothing.css")
    assert response.status_code == 404


def test_middleware_logging(caplog):
    # middleware logs info on request
    # caplog fixture from pytest captures logging
    import logging

    with caplog.at_level(logging.INFO):
        client.get("/")

    assert "Incoming request: GET /" in caplog.text
    assert "Request handled: GET /" in caplog.text
