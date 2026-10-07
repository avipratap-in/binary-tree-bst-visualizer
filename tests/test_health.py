"""Tests for application health and static asset serving."""
import pytest
from bt_visualizer.api.app import create_app


@pytest.fixture
def client():
    """Test client fixture for the Flask app."""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    """GET /api/health returns 200 and json status ok."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data == {"status": "ok", "service": "bt_visualizer"}


def test_index_page(client):
    """GET / returns 200 and serves html containing Visualizer header."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Binary Tree &amp; BST Visualizer" in response.data or b"Binary Tree & BST Visualizer" in response.data


def test_dev_step_page(client):
    """GET /dev_step.html returns 200 and serves test page."""
    response = client.get("/dev_step.html")
    assert response.status_code == 200
    assert b"Dev Step" in response.data

