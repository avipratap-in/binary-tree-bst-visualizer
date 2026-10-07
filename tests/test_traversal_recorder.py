"""Unit tests for traversal step recorder."""
import pytest
from bt_visualizer.core.binary_tree import BinaryTree
from bt_visualizer.core.traversals import (
    inorder_recursive,
    level_order,
    postorder_recursive,
    preorder_recursive,
)
from bt_visualizer.recorder.traversal_recorder import (
    record_inorder,
    record_level_order,
    record_postorder,
    record_preorder,
)


@pytest.fixture
def sample_tree():
    return BinaryTree.from_level_order([1, 2, 3, 4, 5, 6]).root


def test_empty_traversal_recorder():
    for rec_fn in [record_preorder, record_inorder, record_postorder, record_level_order]:
        res = rec_fn(None)
        assert len(res["steps"]) == 1
        assert res["steps"][0]["visited"] == []


def test_preorder_recorder_matches_core(sample_tree):
    core_result = preorder_recursive(sample_tree)
    rec_res = record_preorder(sample_tree)

    final_visited = rec_res["steps"][-1]["visited"]
    assert final_visited == core_result

    # Verify visited list grows progressively
    visited_lengths = [len(step["visited"]) for step in rec_res["steps"]]
    assert visited_lengths == sorted(visited_lengths)


def test_inorder_recorder_matches_core(sample_tree):
    core_result = inorder_recursive(sample_tree)
    rec_res = record_inorder(sample_tree)

    final_visited = rec_res["steps"][-1]["visited"]
    assert final_visited == core_result


def test_postorder_recorder_matches_core(sample_tree):
    core_result = postorder_recursive(sample_tree)
    rec_res = record_postorder(sample_tree)

    final_visited = rec_res["steps"][-1]["visited"]
    assert final_visited == core_result


def test_level_order_recorder_matches_core(sample_tree):
    core_result = level_order(sample_tree)
    rec_res = record_level_order(sample_tree)

    final_visited = rec_res["steps"][-1]["visited"]
    assert final_visited == core_result
