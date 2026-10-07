"""Unit tests for Flask API endpoints using Flask test client."""
import pytest
from bt_visualizer.api.app import create_app
from bt_visualizer.core.bst import BinarySearchTree


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestBSTCreateAPI:
    def test_bst_create_valid(self, client):
        res = client.post("/api/bst/create", json={"values": [50, 30, 70]})
        assert res.status_code == 200
        data = res.get_json()
        assert data["operation"] == "create_from_array"
        assert len(data["steps"]) > 0

    def test_bst_create_missing_values(self, client):
        res = client.post("/api/bst/create", json={})
        assert res.status_code == 400
        data = res.get_json()
        assert "message" in data

    def test_bst_create_invalid_values_type(self, client):
        res = client.post("/api/bst/create", json={"values": "not a list"})
        assert res.status_code == 400
        data = res.get_json()
        assert "message" in data


class TestBSTOperationAPI:
    @pytest.fixture
    def sample_tree_dict(self):
        bst = BinarySearchTree.create_from_array([50, 30, 70])
        return bst.root.to_dict()

    def test_bst_insert(self, client, sample_tree_dict):
        res = client.post(
            "/api/bst/operation",
            json={"tree": sample_tree_dict, "op": "insert", "value": 40},
        )
        assert res.status_code == 200
        data = res.get_json()
        assert data["operation"] == "insert"
        assert len(data["steps"]) > 0

    def test_bst_remove(self, client, sample_tree_dict):
        res = client.post(
            "/api/bst/operation",
            json={"tree": sample_tree_dict, "op": "remove", "value": 30},
        )
        assert res.status_code == 200
        data = res.get_json()
        assert data["operation"] == "remove"
        assert "Removal of 30 is complete." in data["steps"][-1]["message"]

    def test_bst_search(self, client, sample_tree_dict):
        res = client.post(
            "/api/bst/operation",
            json={"tree": sample_tree_dict, "op": "search", "value": 70},
        )
        assert res.status_code == 200
        data = res.get_json()
        assert data["operation"] == "search"

    def test_bst_min_max(self, client, sample_tree_dict):
        res_min = client.post(
            "/api/bst/operation",
            json={"tree": sample_tree_dict, "op": "min"},
        )
        assert res_min.status_code == 200

        res_max = client.post(
            "/api/bst/operation",
            json={"tree": sample_tree_dict, "op": "max"},
        )
        assert res_max.status_code == 200

    def test_bst_pred_succ(self, client, sample_tree_dict):
        res_pred = client.post(
            "/api/bst/operation",
            json={"tree": sample_tree_dict, "op": "pred", "value": 50},
        )
        assert res_pred.status_code == 200

        res_succ = client.post(
            "/api/bst/operation",
            json={"tree": sample_tree_dict, "op": "succ", "value": 50},
        )
        assert res_succ.status_code == 200

    def test_bst_rank_select(self, client, sample_tree_dict):
        res_rank = client.post(
            "/api/bst/operation",
            json={"tree": sample_tree_dict, "op": "rank", "value": 50},
        )
        assert res_rank.status_code == 200

        res_select = client.post(
            "/api/bst/operation",
            json={"tree": sample_tree_dict, "op": "select", "value": 2},
        )
        assert res_select.status_code == 200

    def test_bst_missing_required_value(self, client, sample_tree_dict):
        res = client.post(
            "/api/bst/operation",
            json={"tree": sample_tree_dict, "op": "insert"},
        )
        assert res.status_code == 400
        data = res.get_json()
        assert "message" in data

    def test_bst_invalid_op(self, client, sample_tree_dict):
        res = client.post(
            "/api/bst/operation",
            json={"tree": sample_tree_dict, "op": "invalid_op", "value": 10},
        )
        assert res.status_code == 400
        data = res.get_json()
        assert "message" in data

    def test_bst_malformed_tree(self, client):
        res = client.post(
            "/api/bst/operation",
            json={"tree": "corrupted string instead of dict", "op": "insert", "value": 10},
        )
        assert res.status_code == 400
        data = res.get_json()
        assert "message" in data


class TestTraverseAPI:
    @pytest.fixture
    def sample_tree_dict(self):
        bst = BinarySearchTree.create_from_array([50, 30, 70])
        return bst.root.to_dict()

    @pytest.mark.parametrize("order", ["pre", "in", "post", "level"])
    def test_traverse_valid(self, client, sample_tree_dict, order):
        res = client.post(
            "/api/traverse",
            json={"tree": sample_tree_dict, "order": order},
        )
        assert res.status_code == 200
        data = res.get_json()
        assert len(data["steps"]) > 0

    def test_traverse_invalid_order(self, client, sample_tree_dict):
        res = client.post(
            "/api/traverse",
            json={"tree": sample_tree_dict, "order": "diagonal"},
        )
        assert res.status_code == 400
        data = res.get_json()
        assert "message" in data


class TestBuildAPI:
    def test_build_inorder_preorder_success(self, client):
        res = client.post(
            "/api/build",
            json={
                "mode": "in+pre",
                "seq1": [4, 2, 5, 1, 3],
                "seq2": [1, 2, 4, 5, 3],
            },
        )
        assert res.status_code == 200
        data = res.get_json()
        assert data["operation"] == "build_inorder_preorder"
        assert len(data["steps"]) > 0

    def test_build_preorder_postorder_ambiguous(self, client):
        # Non-full tree -> should return 400 with message
        res = client.post(
            "/api/build",
            json={
                "mode": "pre+post",
                "seq1": [1, 2],
                "seq2": [2, 1],
            },
        )
        assert res.status_code == 400
        data = res.get_json()
        assert "message" in data
        assert "ambiguous" in data["message"].lower()

    def test_build_bst_from_preorder(self, client):
        res = client.post(
            "/api/build",
            json={
                "mode": "bst-pre",
                "seq1": [50, 25, 10, 30, 75],
            },
        )
        assert res.status_code == 200
        data = res.get_json()
        assert data["operation"] == "build_bst_from_preorder"

    def test_build_validation_length_mismatch(self, client):
        res = client.post(
            "/api/build",
            json={
                "mode": "in+pre",
                "seq1": [1, 2],
                "seq2": [1],
            },
        )
        assert res.status_code == 400
        data = res.get_json()
        assert "Length mismatch" in data["message"]


class TestRandomAndExamplesAPI:
    def test_random_bst(self, client):
        res = client.get("/api/random?type=bst&n=5")
        assert res.status_code == 200
        data = res.get_json()
        assert data["operation"] == "create_from_array"

    def test_random_binary(self, client):
        res = client.get("/api/random?type=binary&n=6")
        assert res.status_code == 200
        data = res.get_json()
        assert data["operation"] == "random_binary"

    def test_random_invalid_n(self, client):
        res = client.get("/api/random?type=bst&n=100")
        assert res.status_code == 400
        data = res.get_json()
        assert "message" in data

    def test_examples(self, client):
        res = client.get("/api/examples")
        assert res.status_code == 200
        data = res.get_json()
        assert "examples" in data
        assert len(data["examples"]) >= 3


class TestPropertiesAPI:
    def test_tree_properties_valid(self, client):
        bst = BinarySearchTree.create_from_array([50, 25, 75])
        res = client.post("/api/properties", json={"tree": bst.root.to_dict()})
        assert res.status_code == 200
        data = res.get_json()
        assert "properties" in data
        props = data["properties"]
        assert props["size"] == 3
        assert props["height"] == 2
        assert props["leaf_count"] == 2
        assert props["internal_node_count"] == 1
        assert props["is_full"] is True
        assert props["is_complete"] is True
        assert props["is_balanced"] is True

    def test_tree_properties_empty(self, client):
        res = client.post("/api/properties", json={"tree": None})
        assert res.status_code == 200
        data = res.get_json()
        assert data["properties"]["size"] == 0

    def test_tree_properties_invalid(self, client):
        res = client.post("/api/properties", json="bad string")
        assert res.status_code == 400
        data = res.get_json()
        assert "message" in data

