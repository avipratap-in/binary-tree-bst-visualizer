"""Comprehensive edge-case audit tests for all 6 tree reconstruction modes.

Covers:
- Empty input and whitespace only
- Single-node trees
- One empty field in two-sequence modes
- Unequal length sequences
- Duplicate labels
- Mixed numbers and letters
- Long input (> 50 nodes limit with friendly message)
- Lowercase vs uppercase distinctions
- Unicode characters
- API validation and random generator endpoints
"""
import pytest
from bt_visualizer.api.app import create_app
from bt_visualizer.core.parsing import parse_sequence
from bt_visualizer.core.validator import validate_build_input


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


MODES_TWO_SEQ = ["in+pre", "in+post", "in+level", "pre+post"]
MODES_BST = ["bst-pre", "bst-post"]
ALL_MODES = MODES_TWO_SEQ + MODES_BST


def test_empty_and_whitespace_validation():
    """Empty or whitespace-only inputs should return neutral or graceful empty states."""
    for mode in ALL_MODES:
        res1 = validate_build_input(mode, "", "")
        assert res1["status"] == "neutral"

        res2 = validate_build_input(mode, "   ", "   \t\n  ")
        assert res2["status"] == "neutral"


def test_single_node_all_modes(client):
    """Single node inputs ('A' or 42) should build successfully in all 6 modes."""
    for mode in ALL_MODES:
        # Letters
        res = client.post(
            "/api/build",
            json={"mode": mode, "seq1": "A", "seq2": "A" if mode in MODES_TWO_SEQ else None},
        )
        assert res.status_code == 200, f"Single letter node failed for mode {mode}: {res.get_json()}"
        data = res.get_json()
        assert data["steps"][-1]["tree"]["val"] == "A"

        # Numbers
        res_num = client.post(
            "/api/build",
            json={"mode": mode, "seq1": "42", "seq2": "42" if mode in MODES_TWO_SEQ else None},
        )
        assert res_num.status_code == 200, f"Single numeric node failed for mode {mode}"
        assert res_num.get_json()["steps"][-1]["tree"]["val"] == 42


def test_one_empty_field_two_seq(client):
    """Providing only one field for a two-sequence mode should return an informative 400 error."""
    for mode in MODES_TWO_SEQ:
        res = client.post("/api/build", json={"mode": mode, "seq1": "A, B, C", "seq2": ""})
        assert res.status_code == 400

        diag = validate_build_input(mode, "A, B, C", "")
        assert diag["valid"] is False


def test_unequal_lengths(client):
    """Unequal lengths in two-sequence modes should return a clear length mismatch error."""
    for mode in MODES_TWO_SEQ:
        res = client.post(
            "/api/build",
            json={"mode": mode, "seq1": "A, B, C", "seq2": "A, B"},
        )
        assert res.status_code == 400
        assert "Length mismatch" in res.get_json()["message"] or "length" in res.get_json()["message"].lower()

        diag = validate_build_input(mode, "A, B, C", "A, B")
        assert diag["status"] == "error"
        assert "Length mismatch" in diag["message"]


def test_duplicate_labels_detection(client):
    """Duplicates in general binary tree modes should return error with renaming suggestions."""
    for mode in MODES_TWO_SEQ:
        res = client.post(
            "/api/build",
            json={"mode": mode, "seq1": "A, B, A", "seq2": "A, B, A"},
        )
        assert res.status_code == 400
        assert "duplicate" in res.get_json()["message"].lower()

        diag = validate_build_input(mode, "A, B, A", "A, B, A")
        assert diag["status"] == "error"
        assert any(s["type"] == "replace" for s in diag["suggestions"])


def test_mixed_letters_and_numbers_in_bst(client):
    """BST modes reject mixed numbers and letters with a clear message."""
    for mode in MODES_BST:
        res = client.post(
            "/api/build",
            json={"mode": mode, "seq1": "10, B, 30, A"},
        )
        assert res.status_code == 400
        assert "mixed" in res.get_json()["message"].lower()

        diag = validate_build_input(mode, "10, B, 30, A")
        assert diag["status"] == "error"
        assert "mixed" in diag["message"].lower()


def test_over_50_nodes_limit(client):
    """Input with more than 50 nodes should show a friendly limit message."""
    tokens = [f"N{i}" for i in range(55)]
    seq_str = ", ".join(tokens)

    for mode in ALL_MODES:
        res = client.post(
            "/api/build",
            json={"mode": mode, "seq1": seq_str, "seq2": seq_str if mode in MODES_TWO_SEQ else None},
        )
        assert res.status_code == 400
        data = res.get_json()
        assert "50 nodes" in data["message"]

        diag = validate_build_input(mode, seq_str, seq_str if mode in MODES_TWO_SEQ else None)
        assert diag["status"] == "error"
        assert "50 nodes" in diag["message"]


def test_case_sensitivity_letters(client):
    """'a' and 'A' are distinct labels and should be preserved case-sensitively."""
    # Inorder: a, A, b ; Preorder: A, a, b
    res = client.post(
        "/api/build",
        json={"mode": "in+pre", "seq1": "a, A, b", "seq2": "A, a, b"},
    )
    assert res.status_code == 200
    root = res.get_json()["steps"][-1]["tree"]
    assert root["val"] == "A"
    assert root["left"]["val"] == "a"
    assert root["right"]["val"] == "b"


def test_unicode_node_labels(client):
    """Unicode labels (Greek letters, emojis, accents) should be handled seamlessly."""
    # α, β, γ
    res = client.post(
        "/api/build",
        json={"mode": "in+pre", "seq1": "β, α, γ", "seq2": "α, β, γ"},
    )
    assert res.status_code == 200
    root = res.get_json()["steps"][-1]["tree"]
    assert root["val"] == "α"
    assert root["left"]["val"] == "β"
    assert root["right"]["val"] == "γ"


def test_api_random_endpoint(client):
    """Test GET /api/build/random endpoint across all modes with letters and numbers."""
    for mode in ALL_MODES:
        for labels in ["letters", "numbers"]:
            res = client.get(f"/api/build/random?mode={mode}&n=5&labels={labels}")
            assert res.status_code == 200
            data = res.get_json()
            assert "seq1" in data
            if mode in MODES_TWO_SEQ:
                assert "seq2" in data

            # Verify that building with the random pair returns 200
            build_res = client.post(
                "/api/build",
                json={"mode": mode, "seq1": data["seq1"], "seq2": data.get("seq2")},
            )
            assert build_res.status_code == 200, f"Random build failed for {mode} ({labels}): {build_res.get_json()}"
