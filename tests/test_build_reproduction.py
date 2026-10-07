"""Tests reproducing the Build from Traversal bug with alphabetical labels and raw strings."""
import pytest
from bt_visualizer.api.app import create_app
from bt_visualizer.core.builders import build_from_inorder_postorder


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_core_build_inorder_postorder_letters():
    """Core builder must support string/alphabetical node values."""
    inorder = ["D", "B", "E", "A", "C"]
    postorder = ["D", "E", "B", "C", "A"]
    root = build_from_inorder_postorder(inorder, postorder)
    assert root is not None
    assert root.val == "A"
    assert root.left is not None
    assert root.left.val == "B"
    assert root.left.left.val == "D"
    assert root.left.right.val == "E"
    assert root.right.val == "C"


def test_api_build_with_raw_string_sequences(client):
    """API /api/build should accept raw string sequences as requested in Part 1 & 3."""
    payload = {
        "mode": "in+post",
        "seq1": "D,B,E,A,C",
        "seq2": "D,E,B,C,A",
    }
    res = client.post("/api/build", json=payload)
    assert res.status_code == 200, f"Failed with {res.status_code}: {res.get_json()}"
    data = res.get_json()
    assert data["operation"] == "build_inorder_postorder"
    assert len(data["steps"]) > 0
    final_tree = data["steps"][-1]["tree"]
    assert final_tree["val"] == "A"
