"""Unit tests for binary tree traversals (recursive, iterative, level-order)."""
import pytest
from bt_visualizer.core.binary_tree import TreeNode, BinaryTree
from bt_visualizer.core.traversals import (
    preorder_recursive,
    preorder_iterative,
    inorder_recursive,
    inorder_iterative,
    postorder_recursive,
    postorder_iterative,
    level_order,
)


@pytest.fixture
def sample_tree():
    # Tree:
    #        1
    #      /   \
    #     2     3
    #    / \   /
    #   4   5 6
    return BinaryTree.from_level_order([1, 2, 3, 4, 5, 6]).root


def test_empty_tree():
    assert preorder_recursive(None) == []
    assert preorder_iterative(None) == []
    assert inorder_recursive(None) == []
    assert inorder_iterative(None) == []
    assert postorder_recursive(None) == []
    assert postorder_iterative(None) == []
    assert level_order(None) == []


def test_single_node():
    root = TreeNode(42)
    assert preorder_recursive(root) == [42]
    assert preorder_iterative(root) == [42]
    assert inorder_recursive(root) == [42]
    assert inorder_iterative(root) == [42]
    assert postorder_recursive(root) == [42]
    assert postorder_iterative(root) == [42]
    assert level_order(root) == [42]


def test_traversal_values(sample_tree):
    # Preorder: 1, 2, 4, 5, 3, 6
    assert preorder_recursive(sample_tree) == [1, 2, 4, 5, 3, 6]
    assert preorder_iterative(sample_tree) == [1, 2, 4, 5, 3, 6]

    # Inorder: 4, 2, 5, 1, 6, 3
    assert inorder_recursive(sample_tree) == [4, 2, 5, 1, 6, 3]
    assert inorder_iterative(sample_tree) == [4, 2, 5, 1, 6, 3]

    # Postorder: 4, 5, 2, 6, 3, 1
    assert postorder_recursive(sample_tree) == [4, 5, 2, 6, 3, 1]
    assert postorder_iterative(sample_tree) == [4, 5, 2, 6, 3, 1]

    # Level order: 1, 2, 3, 4, 5, 6
    assert level_order(sample_tree) == [1, 2, 3, 4, 5, 6]


def test_skewed_trees_parity():
    # Left-skewed: 1 -> 2 -> 3
    left_root = TreeNode(1, left=TreeNode(2, left=TreeNode(3)))
    assert preorder_recursive(left_root) == preorder_iterative(left_root) == [1, 2, 3]
    assert inorder_recursive(left_root) == inorder_iterative(left_root) == [3, 2, 1]
    assert postorder_recursive(left_root) == postorder_iterative(left_root) == [3, 2, 1]
    assert level_order(left_root) == [1, 2, 3]

    # Right-skewed: 1 -> 2 -> 3
    right_root = TreeNode(1, right=TreeNode(2, right=TreeNode(3)))
    assert preorder_recursive(right_root) == preorder_iterative(right_root) == [1, 2, 3]
    assert inorder_recursive(right_root) == inorder_iterative(right_root) == [1, 2, 3]
    assert postorder_recursive(right_root) == postorder_iterative(right_root) == [3, 2, 1]
    assert level_order(right_root) == [1, 2, 3]
