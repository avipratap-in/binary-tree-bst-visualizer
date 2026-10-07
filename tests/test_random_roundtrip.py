"""Randomized round-trip testing for binary tree and BST reconstructions.

Generates 300 random trees (sizes 1 to 12, with both letter and number labels),
extracts their traversals, reconstructs them across all 6 supported modes,
and asserts that the reconstructed tree is structurally and value-wise identical.
"""
import random
import pytest
from bt_visualizer.core.binary_tree import TreeNode
from bt_visualizer.core.bst import BinarySearchTree
from bt_visualizer.core.builders import (
    build_from_inorder_preorder,
    build_from_inorder_postorder,
    build_from_inorder_level_order,
    build_from_preorder_postorder,
    build_bst_from_preorder,
    build_bst_from_postorder,
)
from bt_visualizer.core.traversals import (
    inorder_recursive,
    preorder_recursive,
    postorder_recursive,
    level_order,
)
from bt_visualizer.core.generators import (
    generate_random_binary_tree,
    generate_random_full_binary_tree,
    generate_random_bst,
)


def trees_are_identical(t1: TreeNode, t2: TreeNode) -> bool:
    """Check structural and value identity of two binary trees."""
    if t1 is None and t2 is None:
        return True
    if t1 is None or t2 is None:
        return False
    if t1.val != t2.val:
        return False
    return trees_are_identical(t1.left, t2.left) and trees_are_identical(t1.right, t2.right)


def test_300_random_trees_roundtrip():
    """Test 300 random trees across all modes for exact round-trip reconstruction."""
    random.seed(42)

    modes = ["in+pre", "in+post", "in+level", "pre+post", "bst-pre", "bst-post"]

    for i in range(300):
        mode = modes[i % len(modes)]
        size = random.randint(1, 12)
        label_type = "letters" if (i % 2 == 0) else "numbers"

        if mode in {"in+pre", "in+post", "in+level"}:
            orig_tree = generate_random_binary_tree(n=size, label_type=label_type)
            in_seq = inorder_recursive(orig_tree)
            pre_seq = preorder_recursive(orig_tree)
            post_seq = postorder_recursive(orig_tree)
            lvl_seq = level_order(orig_tree)

            if mode == "in+pre":
                rebuilt = build_from_inorder_preorder(in_seq, pre_seq)
            elif mode == "in+post":
                rebuilt = build_from_inorder_postorder(in_seq, post_seq)
            else:
                rebuilt = build_from_inorder_level_order(in_seq, lvl_seq)

            assert trees_are_identical(orig_tree, rebuilt), (
                f"Iteration {i} ({mode}, size {size}, {label_type}) failed round-trip!"
            )

        elif mode == "pre+post":
            # Must be a FULL binary tree (odd node count)
            full_n = size if (size % 2 == 1) else (size + 1 if size < 12 else size - 1)
            orig_tree = generate_random_full_binary_tree(n=full_n, label_type=label_type)
            pre_seq = preorder_recursive(orig_tree)
            post_seq = postorder_recursive(orig_tree)

            rebuilt = build_from_preorder_postorder(pre_seq, post_seq)
            assert trees_are_identical(orig_tree, rebuilt), (
                f"Iteration {i} (pre+post, size {full_n}, {label_type}) failed round-trip!"
            )

        elif mode in {"bst-pre", "bst-post"}:
            orig_tree = generate_random_bst(n=size, label_type=label_type)
            pre_seq = preorder_recursive(orig_tree)
            post_seq = postorder_recursive(orig_tree)

            if mode == "bst-pre":
                rebuilt = build_bst_from_preorder(pre_seq)
            else:
                rebuilt = build_bst_from_postorder(post_seq)

            assert trees_are_identical(orig_tree, rebuilt), (
                f"Iteration {i} ({mode}, size {size}, {label_type}) failed round-trip!"
            )
