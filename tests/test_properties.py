"""Unit tests for binary tree structural properties."""
import pytest
from bt_visualizer.core.binary_tree import TreeNode, BinaryTree
from bt_visualizer.core.properties import (
    leaf_count,
    internal_node_count,
    height,
    size,
    is_full,
    is_complete,
    is_perfect,
    is_balanced,
    get_all_properties,
)


def test_empty_tree_properties():
    assert leaf_count(None) == 0
    assert internal_node_count(None) == 0
    assert height(None) == 0
    assert size(None) == 0
    assert is_full(None) is True
    assert is_complete(None) is True
    assert is_perfect(None) is True
    assert is_balanced(None) is True

    props = get_all_properties(None)
    assert props["size"] == 0
    assert props["height"] == 0
    assert props["leaf_count"] == 0


def test_single_node_properties():
    root = TreeNode(1)
    assert leaf_count(root) == 1
    assert internal_node_count(root) == 0
    assert height(root) == 1
    assert size(root) == 1
    assert is_full(root) is True
    assert is_complete(root) is True
    assert is_perfect(root) is True
    assert is_balanced(root) is True


def test_full_vs_non_full():
    # Full tree:
    #     1
    #    / \
    #   2   3
    full_tree = BinaryTree.from_level_order([1, 2, 3]).root
    assert is_full(full_tree) is True
    assert leaf_count(full_tree) == 2
    assert internal_node_count(full_tree) == 1

    # Non-full tree (2 has only left child 4):
    #     1
    #    / \
    #   2   3
    #  /
    # 4
    non_full_tree = BinaryTree.from_level_order([1, 2, 3, 4]).root
    assert is_full(non_full_tree) is False


def test_complete_vs_non_complete():
    # Complete: [1, 2, 3, 4, 5, 6]
    complete_tree = BinaryTree.from_level_order([1, 2, 3, 4, 5, 6]).root
    assert is_complete(complete_tree) is True

    # Non-complete (level order has gap: left missing, right present):
    #     1
    #    / \
    #   2   3
    #    \
    #     4
    non_complete_tree = BinaryTree.from_level_order([1, 2, 3, None, 4]).root
    assert is_complete(non_complete_tree) is False


def test_perfect_vs_non_perfect():
    # Perfect (size = 2^2 - 1 = 3)
    p3 = BinaryTree.from_level_order([1, 2, 3]).root
    assert is_perfect(p3) is True

    # Perfect (size = 2^3 - 1 = 7)
    p7 = BinaryTree.from_level_order([1, 2, 3, 4, 5, 6, 7]).root
    assert is_perfect(p7) is True

    # Not perfect (size = 6)
    p6 = BinaryTree.from_level_order([1, 2, 3, 4, 5, 6]).root
    assert is_perfect(p6) is False


def test_balanced_vs_unbalanced():
    # Balanced (height diff <= 1)
    balanced_tree = BinaryTree.from_level_order([1, 2, 3, 4, 5]).root
    assert is_balanced(balanced_tree) is True

    # Unbalanced: 1 -> 2 -> 3
    unbalanced_tree = BinaryTree.from_level_order([1, 2, None, 3]).root
    assert is_balanced(unbalanced_tree) is False
