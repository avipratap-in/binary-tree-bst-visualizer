"""Unit tests for tree reconstruction builders and cross-check validation."""
import pytest
from bt_visualizer.core.binary_tree import TreeNode, BinaryTree
from bt_visualizer.core.bst import BinarySearchTree
from bt_visualizer.core.traversals import (
    inorder_recursive,
    preorder_recursive,
    postorder_recursive,
    level_order,
)
from bt_visualizer.core.builders import (
    TreeBuildError,
    AmbiguousTreeError,
    build_from_inorder_preorder,
    build_from_inorder_postorder,
    build_from_inorder_level_order,
    build_from_preorder_postorder,
    build_bst_from_preorder,
    build_bst_from_postorder,
)


class TestValidationErrors:
    def test_length_mismatch(self):
        with pytest.raises(TreeBuildError, match="Length mismatch"):
            build_from_inorder_preorder([1, 2], [1])

    def test_duplicate_elements(self):
        with pytest.raises(TreeBuildError, match="Duplicate elements"):
            build_from_inorder_preorder([1, 1], [1, 1])

    def test_inconsistent_elements(self):
        with pytest.raises(TreeBuildError, match="Inconsistent sequences"):
            build_from_inorder_preorder([1, 2, 3], [1, 2, 4])


class TestInorderPreorderBuilder:
    def test_empty(self):
        assert build_from_inorder_preorder([], []) is None

    def test_single_node(self):
        root = build_from_inorder_preorder([10], [10])
        assert root is not None
        assert root.val == 10

    def test_reconstruction_and_verification(self):
        # Original tree:
        #        1
        #      /   \
        #     2     3
        #    / \   / \
        #   4   5 6   7
        inorder = [4, 2, 5, 1, 6, 3, 7]
        preorder = [1, 2, 4, 5, 3, 6, 7]

        root = build_from_inorder_preorder(inorder, preorder)
        assert root is not None
        assert inorder_recursive(root) == inorder
        assert preorder_recursive(root) == preorder
        assert postorder_recursive(root) == [4, 5, 2, 6, 7, 3, 1]


class TestInorderPostorderBuilder:
    def test_empty(self):
        assert build_from_inorder_postorder([], []) is None

    def test_reconstruction_and_verification(self):
        inorder = [4, 2, 5, 1, 6, 3, 7]
        postorder = [4, 5, 2, 6, 7, 3, 1]

        root = build_from_inorder_postorder(inorder, postorder)
        assert root is not None
        assert inorder_recursive(root) == inorder
        assert postorder_recursive(root) == postorder
        assert preorder_recursive(root) == [1, 2, 4, 5, 3, 6, 7]


class TestInorderLevelOrderBuilder:
    def test_empty(self):
        assert build_from_inorder_level_order([], []) is None

    def test_reconstruction_and_verification(self):
        inorder = [4, 2, 5, 1, 6, 3, 7]
        lvl = [1, 2, 3, 4, 5, 6, 7]

        root = build_from_inorder_level_order(inorder, lvl)
        assert root is not None
        assert inorder_recursive(root) == inorder
        assert level_order(root) == lvl


class TestPreorderPostorderBuilder:
    def test_empty(self):
        assert build_from_preorder_postorder([], []) is None

    def test_full_binary_tree_succeeds(self):
        # Full tree:
        #      1
        #    /   \
        #   2     3
        #  / \   / \
        # 4   5 6   7
        preorder = [1, 2, 4, 5, 3, 6, 7]
        postorder = [4, 5, 2, 6, 7, 3, 1]

        root = build_from_preorder_postorder(preorder, postorder)
        assert root is not None
        assert preorder_recursive(root) == preorder
        assert postorder_recursive(root) == postorder

    def test_ambiguous_tree_raises_ambiguous_tree_error(self):
        # Tree with single child:
        #    1
        #   /
        #  2
        # (Could also be 1 -> right: 2 with identical pre/post: [1, 2] and [2, 1])
        preorder = [1, 2]
        postorder = [2, 1]

        with pytest.raises(AmbiguousTreeError, match="ambiguous"):
            build_from_preorder_postorder(preorder, postorder)


class TestBSTBuilders:
    def test_bst_from_preorder(self):
        preorder = [10, 5, 1, 7, 15, 12, 20]
        root = build_bst_from_preorder(preorder)
        assert root is not None
        assert preorder_recursive(root) == preorder
        assert inorder_recursive(root) == sorted(preorder)

    def test_bst_from_preorder_duplicates_rejected(self):
        with pytest.raises(TreeBuildError, match="Duplicate elements"):
            build_bst_from_preorder([10, 5, 5])

    def test_bst_from_postorder(self):
        postorder = [1, 7, 5, 12, 20, 15, 10]
        root = build_bst_from_postorder(postorder)
        assert root is not None
        assert postorder_recursive(root) == postorder
        assert inorder_recursive(root) == sorted(postorder)

    def test_bst_from_postorder_duplicates_rejected(self):
        with pytest.raises(TreeBuildError, match="Duplicate elements"):
            build_bst_from_postorder([5, 5, 10])


class TestCrossCheckRoundTrip:
    @pytest.mark.parametrize(
        "level_order_input",
        [
            [1],
            [1, 2, 3],
            [10, 5, 15, 2, 7, 12, 20],
            [1, None, 2, None, 3],  # Right-skewed
            [1, 2, None, 3],        # Left-skewed
        ],
    )
    def test_round_trip_reconstruction(self, level_order_input):
        original_tree = BinaryTree.from_level_order(level_order_input).root

        in_seq = inorder_recursive(original_tree)
        pre_seq = preorder_recursive(original_tree)
        post_seq = postorder_recursive(original_tree)
        lvl_seq = level_order(original_tree)

        # 1. Rebuild from Inorder + Preorder
        tree_from_in_pre = build_from_inorder_preorder(in_seq, pre_seq)
        assert inorder_recursive(tree_from_in_pre) == in_seq
        assert preorder_recursive(tree_from_in_pre) == pre_seq
        assert postorder_recursive(tree_from_in_pre) == post_seq
        assert level_order(tree_from_in_pre) == lvl_seq

        # 2. Rebuild from Inorder + Postorder
        tree_from_in_post = build_from_inorder_postorder(in_seq, post_seq)
        assert inorder_recursive(tree_from_in_post) == in_seq
        assert preorder_recursive(tree_from_in_post) == pre_seq
        assert postorder_recursive(tree_from_in_post) == post_seq
        assert level_order(tree_from_in_post) == lvl_seq

        # 3. Rebuild from Inorder + Level order
        tree_from_in_lvl = build_from_inorder_level_order(in_seq, lvl_seq)
        assert inorder_recursive(tree_from_in_lvl) == in_seq
        assert preorder_recursive(tree_from_in_lvl) == pre_seq
        assert postorder_recursive(tree_from_in_lvl) == post_seq
        assert level_order(tree_from_in_lvl) == lvl_seq
