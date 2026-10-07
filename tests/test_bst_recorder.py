"""Unit tests for BST step recorder."""
import pytest
from bt_visualizer.core.bst import BinarySearchTree
from bt_visualizer.core.traversals import inorder_recursive
from bt_visualizer.recorder.bst_recorder import (
    record_create_from_array,
    record_insert,
    record_max,
    record_min,
    record_predecessor,
    record_rank,
    record_remove,
    record_search,
    record_select,
    record_successor,
)


def extract_inorder_from_tree_dict(tree_dict):
    """Helper to extract inorder list from serialized tree dict."""
    if not tree_dict:
        return []
    res = []

    def _inorder(node):
        if not node:
            return
        _inorder(node["left"])
        res.append((node["val"], node["freq"]))
        _inorder(node["right"])

    _inorder(tree_dict)
    return res


class TestBSTRecorderContract:
    def test_step_contract_schema(self):
        bst = BinarySearchTree.create_from_array([50, 30, 70])
        result = record_search(bst.root, 30)

        assert "operation" in result
        assert result["operation"] == "search"
        assert "pseudocode" in result
        assert isinstance(result["pseudocode"], list)
        assert len(result["pseudocode"]) > 0
        assert "steps" in result
        assert isinstance(result["steps"], list)
        assert len(result["steps"]) > 0

        first_step = result["steps"][0]
        for key in ["tree", "highlight_nodes", "highlight_edges", "visited", "message", "pseudo_line", "stats"]:
            assert key in first_step
        assert "n" in first_step["stats"]
        assert "h" in first_step["stats"]


class TestBSTRemoveRecorder:
    def test_remove_pseudocode_and_message(self):
        bst = BinarySearchTree.create_from_array([50, 30, 70, 20])
        result = record_remove(bst.root, 20)

        # Check required pseudocode lines
        expected_pseudo = [
            "search for v",
            "if v's freq > 1, decrement by 1",
            "else if v is a leaf, remove leaf v",
            "else if v has 1 child, bypass v",
            "else replace v with successor",
        ]
        assert result["pseudocode"] == expected_pseudo

        # Check final message
        final_step = result["steps"][-1]
        assert "Removal of 20 is complete." in final_step["message"]

    @pytest.mark.parametrize(
        "initial_vals, val_to_remove",
        [
            ([50, 30, 70, 20], 20),           # leaf
            ([50, 30, 70, 20], 30),           # 1 child
            ([50, 30, 70, 60, 80], 70),       # 2 children
            ([50, 30, 70], 50),               # root with 2 children
            ([50, 30, 30, 70], 30),           # duplicate freq > 1
            ([50, 30, 70], 99),               # not found
        ],
    )
    def test_final_tree_matches_core_remove(self, initial_vals, val_to_remove):
        # 1. Run pure core
        core_bst = BinarySearchTree.create_from_array(initial_vals)
        core_bst.remove(val_to_remove)
        core_tree_dict = core_bst.root.to_dict() if core_bst.root else None

        # 2. Run recorded version
        init_bst = BinarySearchTree.create_from_array(initial_vals)
        rec_res = record_remove(init_bst.root, val_to_remove)
        rec_final_tree_dict = rec_res["steps"][-1]["tree"]

        # 3. Compare structure and frequencies
        assert extract_inorder_from_tree_dict(core_tree_dict) == extract_inorder_from_tree_dict(rec_final_tree_dict)


class TestBSTOtherOperationsRecorder:
    def test_insert_matches_core(self):
        bst = BinarySearchTree.create_from_array([50, 30])
        rec_res = record_insert(bst.root, 40)

        core_bst = BinarySearchTree.create_from_array([50, 30])
        core_bst.insert(40)

        core_tree_dict = core_bst.root.to_dict()
        rec_final_tree_dict = rec_res["steps"][-1]["tree"]
        assert extract_inorder_from_tree_dict(core_tree_dict) == extract_inorder_from_tree_dict(rec_final_tree_dict)

    def test_insert_duplicate_matches_core(self):
        bst = BinarySearchTree.create_from_array([50, 30])
        rec_res = record_insert(bst.root, 30)

        core_bst = BinarySearchTree.create_from_array([50, 30])
        core_bst.insert(30)

        assert extract_inorder_from_tree_dict(core_bst.root.to_dict()) == extract_inorder_from_tree_dict(rec_res["steps"][-1]["tree"])

    def test_create_from_array_matches_core(self):
        arr = [50, 20, 80, 10, 30, 70, 90]
        rec_res = record_create_from_array(arr)
        core_bst = BinarySearchTree.create_from_array(arr)

        assert extract_inorder_from_tree_dict(core_bst.root.to_dict()) == extract_inorder_from_tree_dict(rec_res["steps"][-1]["tree"])

    def test_queries_step_recording(self):
        bst = BinarySearchTree.create_from_array([50, 20, 80])
        for op_fn, args in [
            (record_min, (bst.root,)),
            (record_max, (bst.root,)),
            (record_predecessor, (bst.root, 50)),
            (record_successor, (bst.root, 50)),
            (record_rank, (bst.root, 50)),
            (record_select, (bst.root, 2)),
        ]:
            res = op_fn(*args)
            assert "steps" in res
            assert len(res["steps"]) > 0
            assert res["steps"][-1]["message"] != ""
