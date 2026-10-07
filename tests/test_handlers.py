"""Unit tests for the plain Python handle() dispatcher and handlers."""
import json
import pytest
from bt_visualizer.api.handlers import handle
from bt_visualizer.core.bst import BinarySearchTree


def call_handle(route: str, payload=None) -> tuple[int, dict]:
    payload_str = json.dumps(payload) if payload is not None else "{}"
    raw = handle(route, payload_str)
    res = json.loads(raw)
    return res["status"], res["body"]


class TestHandleDispatcher:
    def test_handle_health(self):
        status, body = call_handle("api/health")
        assert status == 200
        assert body["status"] == "ok"
        assert body["service"] == "bt_visualizer"

    def test_handle_with_leading_slash(self):
        status, body = call_handle("/api/health")
        assert status == 200
        assert body["status"] == "ok"

    def test_handle_invalid_json_payload(self):
        raw = handle("api/health", "invalid json {{{")
        res = json.loads(raw)
        assert res["status"] == 400
        assert "Invalid JSON" in res["body"]["message"]

    def test_handle_unknown_route(self):
        status, body = call_handle("api/unknown_route")
        assert status == 404
        assert "Unknown route" in body["message"]

    def test_handle_bst_create(self):
        status, body = call_handle("api/bst/create", {"values": [40, 20, 60]})
        assert status == 200
        assert body["operation"] == "create_from_array"
        assert len(body["steps"]) > 0

    def test_handle_bst_create_invalid(self):
        status, body = call_handle("api/bst/create", {"values": "invalid"})
        assert status == 400
        assert "message" in body

    def test_handle_bst_operation_insert_and_search(self):
        bst = BinarySearchTree.create_from_array([50, 30, 70])
        tree_dict = bst.root.to_dict()

        # Insert
        status, body = call_handle("api/bst/operation", {"tree": tree_dict, "op": "insert", "value": 25})
        assert status == 200
        assert body["operation"] == "insert"

        # Search
        status, body = call_handle("api/bst/operation", {"tree": tree_dict, "op": "search", "value": 30})
        assert status == 200
        assert body["operation"] == "search"

        # Invalid op
        status, body = call_handle("api/bst/operation", {"tree": tree_dict, "op": "foo"})
        assert status == 400
        assert "Unsupported operation" in body["message"]

    def test_handle_traverse(self):
        bst = BinarySearchTree.create_from_array([10, 5, 15])
        tree_dict = bst.root.to_dict()

        status, body = call_handle("api/traverse", {"tree": tree_dict, "order": "in"})
        assert status == 200
        assert body["operation"] == "inorder"

    def test_handle_properties(self):
        bst = BinarySearchTree.create_from_array([10, 5, 15])
        tree_dict = bst.root.to_dict()

        status, body = call_handle("api/properties", {"tree": tree_dict})
        assert status == 200
        assert body["properties"]["size"] == 3

    def test_handle_build(self):
        status, body = call_handle("api/build", {
            "mode": "in+pre",
            "seq1": [2, 1, 3],
            "seq2": [1, 2, 3],
        })
        assert status == 200
        assert body["operation"] == "build_inorder_preorder"

    def test_handle_build_validate(self):
        status, body = call_handle("api/build/validate", {
            "mode": "in+pre",
            "seq1": "1, 2",
            "seq2": "1, 2",
        })
        assert status == 200
        assert "valid" in body

    def test_handle_random_build_with_query_string(self):
        status, body = call_handle("api/build/random?mode=in%2Bpre&n=5&labels=letters")
        assert status == 200
        assert body["mode"] == "in+pre"
        assert len(body["tokens1"]) == 5

    def test_handle_random_with_query_string(self):
        status, body = call_handle("api/random?type=bst&n=6&labels=numbers")
        assert status == 200
        assert body["operation"] == "create_from_array"

    def test_handle_examples(self):
        status, body = call_handle("api/examples")
        assert status == 200
        assert len(body["examples"]) >= 3
