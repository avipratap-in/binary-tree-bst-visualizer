"""Unit tests for build step recorder."""
import pytest
from bt_visualizer.core.builders import (
    AmbiguousTreeError,
    build_bst_from_postorder,
    build_bst_from_preorder,
    build_from_inorder_level_order,
    build_from_inorder_postorder,
    build_from_inorder_preorder,
    build_from_preorder_postorder,
)
from bt_visualizer.recorder.build_recorder import (
    record_build_bst_from_postorder,
    record_build_bst_from_preorder,
    record_build_inorder_level_order,
    record_build_inorder_postorder,
    record_build_inorder_preorder,
    record_build_preorder_postorder,
)
from tests.test_bst_recorder import extract_inorder_from_tree_dict


def test_build_inorder_preorder_matches_core():
    inorder = [4, 2, 5, 1, 6, 3, 7]
    preorder = [1, 2, 4, 5, 3, 6, 7]

    core_root = build_from_inorder_preorder(inorder, preorder)
    core_dict = core_root.to_dict()

    rec_res = record_build_inorder_preorder(inorder, preorder)
    rec_dict = rec_res["steps"][-1]["tree"]

    assert extract_inorder_from_tree_dict(core_dict) == extract_inorder_from_tree_dict(rec_dict)


def test_build_inorder_postorder_matches_core():
    inorder = [4, 2, 5, 1, 6, 3, 7]
    postorder = [4, 5, 2, 6, 7, 3, 1]

    core_root = build_from_inorder_postorder(inorder, postorder)
    core_dict = core_root.to_dict()

    rec_res = record_build_inorder_postorder(inorder, postorder)
    rec_dict = rec_res["steps"][-1]["tree"]

    assert extract_inorder_from_tree_dict(core_dict) == extract_inorder_from_tree_dict(rec_dict)


def test_build_inorder_level_order_matches_core():
    inorder = [4, 2, 5, 1, 6, 3, 7]
    lvl = [1, 2, 3, 4, 5, 6, 7]

    core_root = build_from_inorder_level_order(inorder, lvl)
    core_dict = core_root.to_dict()

    rec_res = record_build_inorder_level_order(inorder, lvl)
    rec_dict = rec_res["steps"][-1]["tree"]

    assert extract_inorder_from_tree_dict(core_dict) == extract_inorder_from_tree_dict(rec_dict)


def test_build_preorder_postorder_matches_core():
    preorder = [1, 2, 4, 5, 3, 6, 7]
    postorder = [4, 5, 2, 6, 7, 3, 1]

    core_root = build_from_preorder_postorder(preorder, postorder)
    core_dict = core_root.to_dict()

    rec_res = record_build_preorder_postorder(preorder, postorder)
    rec_dict = rec_res["steps"][-1]["tree"]

    assert extract_inorder_from_tree_dict(core_dict) == extract_inorder_from_tree_dict(rec_dict)


def test_build_preorder_postorder_ambiguous_error():
    preorder = [1, 2]
    postorder = [2, 1]
    with pytest.raises(AmbiguousTreeError):
        record_build_preorder_postorder(preorder, postorder)


def test_build_bst_from_preorder_matches_core():
    preorder = [10, 5, 1, 7, 15, 12, 20]

    core_root = build_bst_from_preorder(preorder)
    core_dict = core_root.to_dict()

    rec_res = record_build_bst_from_preorder(preorder)
    rec_dict = rec_res["steps"][-1]["tree"]

    assert extract_inorder_from_tree_dict(core_dict) == extract_inorder_from_tree_dict(rec_dict)


def test_build_bst_from_postorder_matches_core():
    postorder = [1, 7, 5, 12, 20, 15, 10]

    core_root = build_bst_from_postorder(postorder)
    core_dict = core_root.to_dict()

    rec_res = record_build_bst_from_postorder(postorder)
    rec_dict = rec_res["steps"][-1]["tree"]

    assert extract_inorder_from_tree_dict(core_dict) == extract_inorder_from_tree_dict(rec_dict)
