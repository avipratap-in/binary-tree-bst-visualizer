"""Random tree generators for traversal reconstruction and visualizer presets.

Generates random binary trees (general, full binary trees, and BSTs)
with either alphabetical labels (A-Z) or numeric labels (1-99).
"""
from __future__ import annotations

import random
from typing import Any, List, Optional, Tuple
from bt_visualizer.core.binary_tree import TreeNode
from bt_visualizer.core.bst import BinarySearchTree
from bt_visualizer.core.traversals import (
    inorder_recursive,
    level_order,
    postorder_recursive,
    preorder_recursive,
)


def get_random_labels(n: int, label_type: str = "letters") -> List[Any]:
    """Generate n unique labels: either letters (A-Z) or numbers (1-99)."""
    if label_type == "numbers":
        pool = list(range(1, 100))
        return random.sample(pool, min(n, len(pool)))
    else:
        # Letters A-Z (or extended if n > 26)
        alphabet = [chr(c) for c in range(ord("A"), ord("Z") + 1)]
        if n <= 26:
            return random.sample(alphabet, n)
        else:
            extended = list(alphabet)
            for c1 in alphabet:
                for c2 in alphabet:
                    extended.append(f"{c1}{c2}")
                    if len(extended) >= n:
                        break
                if len(extended) >= n:
                    break
            return random.sample(extended, min(n, len(extended)))


def generate_random_binary_tree(n: int, label_type: str = "letters") -> TreeNode:
    """Generate a random connected binary tree with n nodes."""
    if n <= 0:
        raise ValueError("Node count n must be positive.")

    labels = get_random_labels(n, label_type)
    root = TreeNode(labels[0])
    nodes = [root]

    for label in labels[1:]:
        new_node = TreeNode(label)
        # Pick a node with an available child slot
        candidates = [node for node in nodes if node.left is None or node.right is None]
        parent = random.choice(candidates)
        if parent.left is None and parent.right is None:
            if random.random() < 0.5:
                parent.left = new_node
            else:
                parent.right = new_node
        elif parent.left is None:
            parent.left = new_node
        else:
            parent.right = new_node
        nodes.append(new_node)

    return root


def generate_random_full_binary_tree(n: int, label_type: str = "letters") -> TreeNode:
    """Generate a random Full Binary Tree (every node has 0 or 2 children).

    A full binary tree must have an odd number of nodes (n = 2k + 1).
    """
    if n % 2 == 0:
        n += 1  # ensure odd node count

    labels = get_random_labels(n, label_type)
    root = TreeNode(labels[0])
    leaves = [root]
    idx = 1

    while idx < n and leaves:
        leaf = random.choice(leaves)
        leaves.remove(leaf)

        leaf.left = TreeNode(labels[idx])
        leaf.right = TreeNode(labels[idx + 1])
        idx += 2

        leaves.append(leaf.left)
        leaves.append(leaf.right)

    return root


def generate_random_bst(n: int, label_type: str = "letters") -> TreeNode:
    """Generate a random Binary Search Tree with n nodes."""
    if n <= 0:
        raise ValueError("Node count n must be positive.")

    labels = get_random_labels(n, label_type)
    bst = BinarySearchTree()
    for label in labels:
        bst.insert(label)
    return bst.root


def generate_traversal_pair(
    mode: str,
    n: int = 7,
    labels: str = "letters",
) -> Tuple[List[Any], Optional[List[Any]]]:
    """Generate valid traversal sequences for a given reconstruction mode."""
    if mode in {"in+pre", "in+post", "in+level"}:
        root = generate_random_binary_tree(n, labels)
        in_seq = inorder_recursive(root)
        if mode == "in+pre":
            return in_seq, preorder_recursive(root)
        elif mode == "in+post":
            return in_seq, postorder_recursive(root)
        else:
            return in_seq, level_order(root)

    elif mode == "pre+post":
        # Must be full binary tree to guarantee unambiguous reconstruction
        full_n = n if n % 2 == 1 else n + 1
        root = generate_random_full_binary_tree(full_n, labels)
        return preorder_recursive(root), postorder_recursive(root)

    elif mode == "bst-pre":
        root = generate_random_bst(n, labels)
        return preorder_recursive(root), None

    elif mode == "bst-post":
        root = generate_random_bst(n, labels)
        return postorder_recursive(root), None

    else:
        raise ValueError(f"Unknown mode: {mode}")
