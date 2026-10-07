"""Unit tests for TreeNode and BinaryTree core implementations."""
import pytest
from bt_visualizer.core.binary_tree import TreeNode, BinaryTree


class TestTreeNode:
    def test_node_creation_defaults(self):
        node = TreeNode(42)
        assert node.val == 42
        assert node.value == 42
        assert node.freq == 1
        assert node.left is None
        assert node.right is None
        assert node.node_id.startswith("node_")

    def test_node_custom_attributes(self):
        node = TreeNode(10, node_id="custom_1", freq=3)
        assert node.val == 10
        assert node.node_id == "custom_1"
        assert node.freq == 3

    def test_node_to_dict_serialization(self):
        root = TreeNode(10, node_id="n1")
        root.left = TreeNode(5, node_id="n2")
        root.right = TreeNode(15, node_id="n3", freq=2)

        data = root.to_dict()
        assert data["id"] == "n1"
        assert data["value"] == 10
        assert data["freq"] == 1
        assert data["left"]["id"] == "n2"
        assert data["left"]["value"] == 5
        assert data["right"]["id"] == "n3"
        assert data["right"]["freq"] == 2
        assert data["left"]["left"] is None

    def test_node_clone(self):
        root = TreeNode(10, node_id="n1")
        root.left = TreeNode(5, node_id="n2")
        cloned = root.clone()

        assert cloned.val == root.val
        assert cloned.node_id == root.node_id
        assert cloned.left is not None
        assert cloned.left.val == 5
        # Modifying clone does not mutate original
        cloned.val = 99
        assert root.val == 10


class TestBinaryTree:
    def test_empty_tree(self):
        tree = BinaryTree.from_level_order([])
        assert tree.root is None
        assert tree.is_empty()
        assert tree.size() == 0
        assert tree.height() == 0
        assert tree.to_level_order() == []

    def test_single_node(self):
        tree = BinaryTree.from_level_order([10])
        assert tree.root is not None
        assert tree.root.val == 10
        assert tree.size() == 1
        assert tree.height() == 1
        assert tree.to_level_order() == [10]

    def test_balanced_level_order(self):
        # Tree:
        #      1
        #    /   \
        #   2     3
        #  / \
        # 4   5
        items = [1, 2, 3, 4, 5]
        tree = BinaryTree.from_level_order(items)
        assert tree.size() == 5
        assert tree.height() == 3
        assert tree.root.val == 1
        assert tree.root.left.val == 2
        assert tree.root.right.val == 3
        assert tree.root.left.left.val == 4
        assert tree.root.left.right.val == 5
        assert tree.to_level_order() == [1, 2, 3, 4, 5]

    def test_tree_with_none_placeholders(self):
        # Tree:
        #      1
        #     / \
        #  None  2
        #       /
        #      3
        items = [1, None, 2, 3]
        tree = BinaryTree.from_level_order(items)
        assert tree.size() == 3
        assert tree.height() == 3
        assert tree.root.left is None
        assert tree.root.right.val == 2
        assert tree.root.right.left.val == 3
        assert tree.to_level_order() == [1, None, 2, 3]

    def test_skewed_tree(self):
        # Left-skewed tree
        items = [1, 2, None, 3]
        tree = BinaryTree.from_level_order(items)
        assert tree.height() == 3
        assert tree.size() == 3
        assert tree.root.left.val == 2
        assert tree.root.left.left.val == 3
