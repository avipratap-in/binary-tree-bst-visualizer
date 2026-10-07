"""Unit tests for BinarySearchTree core implementation."""
import pytest
from bt_visualizer.core.binary_tree import TreeNode
from bt_visualizer.core.bst import BinarySearchTree


class TestBSTBasics:
    def test_empty_bst(self):
        bst = BinarySearchTree()
        assert bst.root is None
        assert bst.size() == 0
        assert bst.height() == 0
        assert bst.min() is None
        assert bst.max() is None
        assert bst.search(10) is None
        assert bst.remove(10) is False
        assert bst.rank(10) == 0
        assert bst.select(1) is None
        assert bst.is_valid_bst() is True

    def test_single_node(self):
        bst = BinarySearchTree()
        bst.insert(50)
        assert bst.size() == 1
        assert bst.height() == 1
        assert bst.min() == 50
        assert bst.max() == 50
        assert bst.search(50) is not None
        assert bst.search(50).val == 50
        assert bst.predecessor(50) is None
        assert bst.successor(50) is None
        assert bst.rank(50) == 0
        assert bst.rank(60) == 1
        assert bst.select(1) == 50
        assert bst.select(2) is None
        assert bst.is_valid_bst() is True


class TestBSTDuplicates:
    def test_duplicate_insertion_increments_freq(self):
        bst = BinarySearchTree()
        bst.insert(20)
        bst.insert(10)
        bst.insert(20)  # duplicate
        bst.insert(20)  # duplicate

        node = bst.search(20)
        assert node is not None
        assert node.freq == 3
        # Distinct nodes = 2, total size = 4
        assert bst.size(include_duplicates=False) == 2
        assert bst.size(include_duplicates=True) == 4

    def test_remove_duplicate_decrements_freq(self):
        bst = BinarySearchTree()
        bst.insert(20)
        bst.insert(20)
        bst.insert(10)

        assert bst.search(20).freq == 2
        removed = bst.remove(20)
        assert removed is True
        # Node still exists with freq 1
        assert bst.search(20) is not None
        assert bst.search(20).freq == 1

        # Second remove structurally deletes the node
        removed_again = bst.remove(20)
        assert removed_again is True
        assert bst.search(20) is None


class TestBSTStructuralRemoval:
    def test_remove_leaf(self):
        bst = BinarySearchTree.create_from_array([50, 30, 70, 20])
        # 20 is a leaf
        assert bst.remove(20) is True
        assert bst.search(20) is None
        assert bst.search(30).left is None

    def test_remove_node_with_left_child_only(self):
        bst = BinarySearchTree.create_from_array([50, 30, 20])
        # 30 has only left child (20)
        assert bst.remove(30) is True
        assert bst.search(30) is None
        assert bst.root.left.val == 20

    def test_remove_node_with_right_child_only(self):
        bst = BinarySearchTree.create_from_array([50, 30, 40])
        # 30 has only right child (40)
        assert bst.remove(30) is True
        assert bst.search(30) is None
        assert bst.root.left.val == 40

    def test_remove_node_with_two_children_immediate_successor(self):
        # Tree:
        #      50
        #    /    \
        #   30    70
        #  /  \
        # 20  40
        bst = BinarySearchTree.create_from_array([50, 30, 70, 20, 40])
        assert bst.remove(30) is True
        assert bst.search(30) is None
        # Successor of 30 was 40, now replaces 30
        assert bst.root.left.val == 40
        assert bst.root.left.left.val == 20
        assert bst.root.left.right is None
        assert bst.is_valid_bst() is True

    def test_remove_node_with_two_children_deep_successor(self):
        # 30's right subtree has 40 -> 35
        # Successor of 30 is 35
        bst = BinarySearchTree.create_from_array([50, 30, 70, 20, 40, 35])
        assert bst.remove(30) is True
        assert bst.search(30) is None
        assert bst.root.left.val == 35
        assert bst.root.left.right.val == 40
        assert bst.root.left.right.left is None
        assert bst.is_valid_bst() is True

    def test_remove_root_with_two_children(self):
        bst = BinarySearchTree.create_from_array([50, 30, 70, 60, 80])
        assert bst.remove(50) is True
        assert bst.search(50) is None
        # Successor of 50 is 60, which should become new root
        assert bst.root.val == 60
        assert bst.root.right.val == 70
        assert bst.root.right.left is None
        assert bst.is_valid_bst() is True


class TestBSTQueries:
    @pytest.fixture
    def sample_bst(self):
        # Elements: 15, 6, 18, 3, 7, 17, 20, 2, 4, 13, 9
        # Sorted: 2, 3, 4, 6, 7, 9, 13, 15, 17, 18, 20
        return BinarySearchTree.create_from_array([15, 6, 18, 3, 7, 17, 20, 2, 4, 13, 9])

    def test_min_and_max(self, sample_bst):
        assert sample_bst.min() == 2
        assert sample_bst.max() == 20

    def test_predecessor(self, sample_bst):
        assert sample_bst.predecessor(15) == 13
        assert sample_bst.predecessor(6) == 4
        assert sample_bst.predecessor(2) is None  # min has no pred
        assert sample_bst.predecessor(10) == 9    # value not in tree

    def test_successor(self, sample_bst):
        assert sample_bst.successor(15) == 17
        assert sample_bst.successor(13) == 15
        assert sample_bst.successor(20) is None  # max has no succ
        assert sample_bst.successor(10) == 13    # value not in tree

    def test_rank(self, sample_bst):
        # Sorted: 2, 3, 4, 6, 7, 9, 13, 15, 17, 18, 20
        assert sample_bst.rank(2) == 0
        assert sample_bst.rank(3) == 1
        assert sample_bst.rank(6) == 3
        assert sample_bst.rank(15) == 7
        assert sample_bst.rank(25) == 11
        assert sample_bst.rank(0) == 0

    def test_rank_with_duplicates(self):
        bst = BinarySearchTree.create_from_array([10, 5, 5, 20, 20, 20])
        # Elements: 5(x2), 10(x1), 20(x3)
        assert bst.rank(5) == 0
        assert bst.rank(10) == 2
        assert bst.rank(20) == 3
        assert bst.rank(30) == 6

    def test_select(self, sample_bst):
        # 1-indexed select:
        # 1st smallest -> 2, 2nd -> 3, ..., 11th -> 20
        sorted_vals = [2, 3, 4, 6, 7, 9, 13, 15, 17, 18, 20]
        for idx, val in enumerate(sorted_vals, start=1):
            assert sample_bst.select(idx) == val

        assert sample_bst.select(0) is None
        assert sample_bst.select(12) is None

    def test_select_with_duplicates(self):
        bst = BinarySearchTree.create_from_array([10, 10, 5, 20])
        # Sorted multi-set: 5, 10, 10, 20
        assert bst.select(1) == 5
        assert bst.select(2) == 10
        assert bst.select(3) == 10
        assert bst.select(4) == 20
        assert bst.select(5) is None


class TestBSTValidationAndSkewed:
    def test_is_valid_bst(self):
        bst = BinarySearchTree.create_from_array([50, 25, 75])
        assert bst.is_valid_bst() is True

        # Manually violate BST invariant
        bst.root.left.val = 100
        assert bst.is_valid_bst() is False

    def test_skewed_bst(self):
        # Right-skewed tree
        bst = BinarySearchTree.create_from_array([1, 2, 3, 4, 5])
        assert bst.height() == 5
        assert bst.size() == 5
        assert bst.min() == 1
        assert bst.max() == 5
        assert bst.search(4) is not None
        assert bst.remove(3) is True
        assert bst.size() == 4
        assert bst.search(3) is None
