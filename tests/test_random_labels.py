"""Tests for GET /api/random with numbers and letters label options."""
import pytest
from bt_visualizer.api.app import create_app
from bt_visualizer.core.traversals import level_order


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_random_binary_numeric_labels(client):
    """GET /api/random?type=binary&n=8&labels=numbers returns 8 unique numbers."""
    res = client.get("/api/random?type=binary&n=8&labels=numbers")
    assert res.status_code == 200
    data = res.get_json()
    assert "Generated random binary tree with 8 numeric nodes" in data["steps"][-1]["message"]

    tree = data["steps"][-1]["tree"]
    # Collect all node values
    vals = []
    def collect(node):
        if not node:
            return
        vals.append(node["val"])
        collect(node.get("left"))
        collect(node.get("right"))
    collect(tree)

    assert len(vals) == 8
    assert len(set(vals)) == 8  # unique
    for v in vals:
        assert isinstance(v, int)
        assert 1 <= v <= 99


def test_random_binary_alphabetic_labels(client):
    """GET /api/random?type=binary&n=6&labels=letters returns 6 unique letters."""
    res = client.get("/api/random?type=binary&n=6&labels=letters")
    assert res.status_code == 200
    data = res.get_json()
    assert "Generated random binary tree with 6 alphabetic nodes" in data["steps"][-1]["message"]

    tree = data["steps"][-1]["tree"]
    vals = []
    def collect(node):
        if not node:
            return
        vals.append(node["val"])
        collect(node.get("left"))
        collect(node.get("right"))
    collect(tree)

    assert len(vals) == 6
    assert len(set(vals)) == 6
    for v in vals:
        assert isinstance(v, str)
        assert len(v) == 1
        assert "A" <= v <= "Z"


def test_random_validation_clamps_and_errors(client):
    """Test validation and error handling for /api/random."""
    # Letters max is 26
    res = client.get("/api/random?type=binary&n=27&labels=letters")
    assert res.status_code == 400
    assert "between 1 and 26" in res.get_json()["message"]

    # Numbers max is 30
    res = client.get("/api/random?type=binary&n=35&labels=numbers")
    assert res.status_code == 400
    assert "between 1 and 30" in res.get_json()["message"]

    # Minimum is 1
    res = client.get("/api/random?type=binary&n=0&labels=numbers")
    assert res.status_code == 400

    # Invalid labels
    res = client.get("/api/random?type=binary&n=5&labels=invalid")
    assert res.status_code == 400
    assert "labels" in res.get_json()["message"].lower()

    # Invalid n
    res = client.get("/api/random?type=binary&n=abc")
    assert res.status_code == 400
