"""Tree Property Analyzers and Validators.

Provides calculations for:
- Leaf count
- Internal node count
- Tree height
- is_full (every node has 0 or 2 children)
- is_complete (all levels filled except possibly last, filled left-to-right)
- is_perfect (all leaves at same level, internal nodes have 2 children: n = 2^h - 1)
- is_balanced (AVL balance: |height(left) - height(right)| <= 1 for all nodes)

Complexity:
- Time: O(n) for all property checks.
- Space: O(h) recursion stack / O(w) queue.
"""
from __future__ import annotations

from collections import deque
from typing import Any, Dict, Optional, Tuple
from bt_visualizer.core.binary_tree import TreeNode


def height(root: Optional[TreeNode]) -> int:
    """Calculate height of binary tree (0 for empty tree, 1 for single node).

    Time Complexity: O(n)
    Space Complexity: O(h)
    """
    if root is None:
        return 0
    return 1 + max(height(root.left), height(root.right))


def size(root: Optional[TreeNode]) -> int:
    """Count total number of nodes in binary tree.

    Time Complexity: O(n)
    Space Complexity: O(h)
    """
    if root is None:
        return 0
    return 1 + size(root.left) + size(root.right)


def leaf_count(root: Optional[TreeNode]) -> int:
    """Count number of leaf nodes (nodes with 0 children).

    Time Complexity: O(n)
    Space Complexity: O(h)
    """
    if root is None:
        return 0
    if root.left is None and root.right is None:
        return 1
    return leaf_count(root.left) + leaf_count(root.right)


def internal_node_count(root: Optional[TreeNode]) -> int:
    """Count number of internal nodes (nodes with at least one child).

    Time Complexity: O(n)
    Space Complexity: O(h)
    """
    if root is None or (root.left is None and root.right is None):
        return 0
    return 1 + internal_node_count(root.left) + internal_node_count(root.right)


def is_full(root: Optional[TreeNode]) -> bool:
    """Check if tree is a full binary tree (every node has 0 or 2 children).

    An empty tree or single node tree is full.

    Time Complexity: O(n)
    Space Complexity: O(h)
    """
    if root is None:
        return True

    # If leaf
    if root.left is None and root.right is None:
        return True

    # If both children exist
    if root.left is not None and root.right is not None:
        return is_full(root.left) and is_full(root.right)

    # Has exactly one child
    return False


def is_complete(root: Optional[TreeNode]) -> bool:
    """Check if tree is complete (all levels filled except possibly the last, packed left).

    Time Complexity: O(n)
    Space Complexity: O(w)
    """
    if root is None:
        return True

    queue: deque[Optional[TreeNode]] = deque([root])
    seen_null = False

    while queue:
        curr = queue.popleft()
        if curr is None:
            seen_null = True
        else:
            if seen_null:
                # Encountered a non-null node after a null node
                return False
            queue.append(curr.left)
            queue.append(curr.right)

    return True


def is_perfect(root: Optional[TreeNode]) -> bool:
    """Check if tree is perfect (all internal nodes have 2 children, all leaves at same depth).

    Equivalently, size == (2 ** height) - 1.

    Time Complexity: O(n)
    Space Complexity: O(h)
    """
    if root is None:
        return True

    h = height(root)
    n = size(root)
    return n == (1 << h) - 1


def is_balanced(root: Optional[TreeNode]) -> bool:
    """Check if tree is height-balanced (AVL criterion: |left_h - right_h| <= 1 for all nodes).

    Time Complexity: O(n) bottom-up
    Space Complexity: O(h)
    """
    def _check_balance(node: Optional[TreeNode]) -> Tuple[bool, int]:
        if node is None:
            return True, 0

        left_bal, left_h = _check_balance(node.left)
        if not left_bal:
            return False, 0

        right_bal, right_h = _check_balance(node.right)
        if not right_bal:
            return False, 0

        if abs(left_h - right_h) > 1:
            return False, 0

        return True, 1 + max(left_h, right_h)

    balanced, _ = _check_balance(root)
    return balanced


def get_all_properties(root: Optional[TreeNode]) -> Dict[str, Any]:
    """Compute all tree structural properties in a single summary dictionary."""
    return {
        "size": size(root),
        "height": height(root),
        "leaf_count": leaf_count(root),
        "internal_node_count": internal_node_count(root),
        "is_full": is_full(root),
        "is_complete": is_complete(root),
        "is_perfect": is_perfect(root),
        "is_balanced": is_balanced(root),
    }
