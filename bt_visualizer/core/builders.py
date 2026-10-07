"""Tree reconstruction algorithms from traversal orders.

Reconstructs Binary Trees from:
- Inorder + Preorder
- Inorder + Postorder
- Inorder + Level order
- Preorder + Postorder (raises AmbiguousTreeError if non-full / ambiguous)
- BST from Preorder only
- BST from Postorder only

Complexity:
- Inorder + Preorder: O(n) time, O(n) space.
- Inorder + Postorder: O(n) time, O(n) space.
- Inorder + Level order: O(n^2) time, O(n) space.
- Preorder + Postorder: O(n) time, O(n) space.
- BST from Preorder / Postorder: O(n) time, O(n) space.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Set
from bt_visualizer.core.binary_tree import TreeNode


class TreeBuildError(ValueError):
    """Raised when traversal inputs are invalid or inconsistent."""
    pass


class AmbiguousTreeError(TreeBuildError):
    """Raised when traversals cannot uniquely define a tree (e.g. non-full pre+post)."""
    pass


def _validate_sequences(
    seq1: List[Any],
    seq2: List[Any],
    name1: str,
    name2: str,
    require_unique: bool = True,
) -> None:
    """Validate two traversal sequences for length, duplicates, and multiset equality."""
    if len(seq1) != len(seq2):
        raise TreeBuildError(
            f"Length mismatch: {name1} has {len(seq1)} elements, but {name2} has {len(seq2)}."
        )

    if require_unique:
        if len(set(seq1)) != len(seq1):
            raise TreeBuildError(
                f"Duplicate elements detected in {name1}: {seq1}. Reconstruction requires unique values."
            )
        if len(set(seq2)) != len(seq2):
            raise TreeBuildError(
                f"Duplicate elements detected in {name2}: {seq2}. Reconstruction requires unique values."
            )

    if set(seq1) != set(seq2):
        diff1 = set(seq1) - set(seq2)
        diff2 = set(seq2) - set(seq1)
        raise TreeBuildError(
            f"Inconsistent sequences: {name1} and {name2} contain different elements. "
            f"Missing in {name2}: {list(diff1)}; Missing in {name1}: {list(diff2)}."
        )


def build_from_inorder_preorder(
    inorder: List[Any],
    preorder: List[Any],
) -> Optional[TreeNode]:
    """Reconstruct binary tree from inorder and preorder traversals.

    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    _validate_sequences(inorder, preorder, "inorder", "preorder", require_unique=True)
    if not inorder:
        return None

    in_map: Dict[Any, int] = {val: idx for idx, val in enumerate(inorder)}
    pre_iter = iter(preorder)

    def _build(left_idx: int, right_idx: int) -> Optional[TreeNode]:
        if left_idx > right_idx:
            return None

        val = next(pre_iter)
        mid_idx = in_map[val]

        if mid_idx < left_idx or mid_idx > right_idx:
            raise TreeBuildError(
                f"Inconsistent traversal order: value '{val}' is outside current subtree range [{left_idx}, {right_idx}]."
            )

        root = TreeNode(val)
        root.left = _build(left_idx, mid_idx - 1)
        root.right = _build(mid_idx + 1, right_idx)
        return root

    return _build(0, len(inorder) - 1)


def build_from_inorder_postorder(
    inorder: List[Any],
    postorder: List[Any],
) -> Optional[TreeNode]:
    """Reconstruct binary tree from inorder and postorder traversals.

    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    _validate_sequences(inorder, postorder, "inorder", "postorder", require_unique=True)
    if not inorder:
        return None

    in_map: Dict[Any, int] = {val: idx for idx, val in enumerate(inorder)}
    post_iter = reversed(postorder)

    def _build(left_idx: int, right_idx: int) -> Optional[TreeNode]:
        if left_idx > right_idx:
            return None

        val = next(post_iter)
        mid_idx = in_map[val]

        if mid_idx < left_idx or mid_idx > right_idx:
            raise TreeBuildError(
                f"Inconsistent traversal order: value '{val}' is outside current subtree range [{left_idx}, {right_idx}]."
            )

        root = TreeNode(val)
        # Note: In postorder reversed, root is followed by right subtree, then left
        root.right = _build(mid_idx + 1, right_idx)
        root.left = _build(left_idx, mid_idx - 1)
        return root

    return _build(0, len(inorder) - 1)


def build_from_inorder_level_order(
    inorder: List[Any],
    level_order: List[Any],
) -> Optional[TreeNode]:
    """Reconstruct binary tree from inorder and level-order traversals.

    Time Complexity: O(n^2)
    Space Complexity: O(n)
    """
    _validate_sequences(inorder, level_order, "inorder", "level_order", require_unique=True)
    if not inorder:
        return None

    def _build(in_list: List[Any], level_list: List[Any]) -> Optional[TreeNode]:
        if not in_list:
            return None

        root_val = level_list[0]
        root = TreeNode(root_val)
        root_idx = in_list.index(root_val)

        left_in = in_list[:root_idx]
        right_in = in_list[root_idx + 1:]

        left_set: Set[Any] = set(left_in)
        left_level: List[Any] = []
        right_level: List[Any] = []

        for item in level_list[1:]:
            if item in left_set:
                left_level.append(item)
            else:
                right_level.append(item)

        root.left = _build(left_in, left_level)
        root.right = _build(right_in, right_level)
        return root

    return _build(inorder, level_order)


def build_from_preorder_postorder(
    preorder: List[Any],
    postorder: List[Any],
) -> Optional[TreeNode]:
    """Reconstruct binary tree from preorder and postorder traversals.

    Raises AmbiguousTreeError if any internal node has only one child,
    as preorder + postorder uniquely identifies only full binary trees.

    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    _validate_sequences(preorder, postorder, "preorder", "postorder", require_unique=True)
    if not preorder:
        return None

    post_map: Dict[Any, int] = {val: idx for idx, val in enumerate(postorder)}

    def _build(
        pre_start: int,
        pre_end: int,
        post_start: int,
        post_end: int,
    ) -> TreeNode:
        root_val = preorder[pre_start]
        root = TreeNode(root_val)

        if pre_start == pre_end:
            return root

        # Next value in preorder is the root of the left subtree
        left_val = preorder[pre_start + 1]
        # Preceding value in postorder is the root of the right subtree
        last_post_val = postorder[post_end - 1]

        # If left_val == last_post_val, this node has only ONE child!
        # It is ambiguous whether this single child is a left or right child.
        if left_val == last_post_val:
            raise AmbiguousTreeError(
                f"Reconstruction from preorder and postorder is ambiguous: node '{root_val}' "
                f"has a single child '{left_val}', which could be either a left or right child. "
                f"Preorder + Postorder requires a full binary tree."
            )

        left_post_idx = post_map[left_val]
        left_size = left_post_idx - post_start + 1

        root.left = _build(
            pre_start + 1,
            pre_start + left_size,
            post_start,
            left_post_idx,
        )
        root.right = _build(
            pre_start + left_size + 1,
            pre_end,
            left_post_idx + 1,
            post_end - 1,
        )
        return root

    return _build(0, len(preorder) - 1, 0, len(postorder) - 1)


def build_bst_from_preorder(preorder: List[Any]) -> Optional[TreeNode]:
    """Reconstruct BST from preorder traversal only.

    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    if not preorder:
        return None

    if len(set(preorder)) != len(preorder):
        raise TreeBuildError(
            f"Duplicate elements in preorder traversal: {preorder}. BST construction requires distinct keys."
        )

    idx = 0
    n = len(preorder)

    def _build(min_val: Any, max_val: Any) -> Optional[TreeNode]:
        nonlocal idx
        if idx >= n:
            return None

        val = preorder[idx]
        if (min_val is not None and val <= min_val) or (max_val is not None and val >= max_val):
            return None

        idx += 1
        root = TreeNode(val)
        root.left = _build(min_val, val)
        root.right = _build(val, max_val)
        return root

    root = _build(None, None)
    if idx < n:
        raise TreeBuildError(
            f"Invalid BST preorder sequence: element '{preorder[idx]}' violates BST ordering."
        )
    return root


def build_bst_from_postorder(postorder: List[Any]) -> Optional[TreeNode]:
    """Reconstruct BST from postorder traversal only.

    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    if not postorder:
        return None

    if len(set(postorder)) != len(postorder):
        raise TreeBuildError(
            f"Duplicate elements in postorder traversal: {postorder}. BST construction requires distinct keys."
        )

    idx = len(postorder) - 1

    def _build(min_val: Any, max_val: Any) -> Optional[TreeNode]:
        nonlocal idx
        if idx < 0:
            return None

        val = postorder[idx]
        if (min_val is not None and val <= min_val) or (max_val is not None and val >= max_val):
            return None

        idx -= 1
        root = TreeNode(val)
        # In postorder reversed, right subtree comes before left
        root.right = _build(val, max_val)
        root.left = _build(min_val, val)
        return root

    root = _build(None, None)
    if idx >= 0:
        raise TreeBuildError(
            f"Invalid BST postorder sequence: element '{postorder[idx]}' violates BST ordering."
        )
    return root
