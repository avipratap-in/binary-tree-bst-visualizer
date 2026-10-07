"""Binary Tree Traversal Algorithms.

Provides both recursive and iterative implementations (using explicit stack/deque)
for preorder, inorder, postorder, and level-order traversals.

Complexity:
- Time: O(n) for all traversals (visits every node once).
- Space: O(h) for DFS call-stack/explicit stack, where h is tree height.
         O(w) for BFS level-order where w is maximum tree width.
"""
from __future__ import annotations

from collections import deque
from typing import Any, List, Optional
from bt_visualizer.core.binary_tree import TreeNode


def preorder_recursive(root: Optional[TreeNode]) -> List[Any]:
    """Preorder traversal (Root -> Left -> Right) using recursion.

    Time Complexity: O(n)
    Space Complexity: O(h) call stack
    """
    result: List[Any] = []

    def _traverse(node: Optional[TreeNode]) -> None:
        if node is None:
            return
        result.append(node.val)
        _traverse(node.left)
        _traverse(node.right)

    _traverse(root)
    return result


def preorder_iterative(root: Optional[TreeNode]) -> List[Any]:
    """Preorder traversal (Root -> Left -> Right) using an explicit stack.

    Time Complexity: O(n)
    Space Complexity: O(h) explicit stack
    """
    if root is None:
        return []

    result: List[Any] = []
    stack: List[TreeNode] = [root]

    while stack:
        node = stack.pop()
        result.append(node.val)
        # Push right first so left is popped first
        if node.right is not None:
            stack.append(node.right)
        if node.left is not None:
            stack.append(node.left)

    return result


def inorder_recursive(root: Optional[TreeNode]) -> List[Any]:
    """Inorder traversal (Left -> Root -> Right) using recursion.

    Time Complexity: O(n)
    Space Complexity: O(h) call stack
    """
    result: List[Any] = []

    def _traverse(node: Optional[TreeNode]) -> None:
        if node is None:
            return
        _traverse(node.left)
        result.append(node.val)
        _traverse(node.right)

    _traverse(root)
    return result


def inorder_iterative(root: Optional[TreeNode]) -> List[Any]:
    """Inorder traversal (Left -> Root -> Right) using an explicit stack.

    Time Complexity: O(n)
    Space Complexity: O(h) explicit stack
    """
    result: List[Any] = []
    stack: List[TreeNode] = []
    curr: Optional[TreeNode] = root

    while curr is not None or stack:
        while curr is not None:
            stack.append(curr)
            curr = curr.left

        curr = stack.pop()
        result.append(curr.val)
        curr = curr.right

    return result


def postorder_recursive(root: Optional[TreeNode]) -> List[Any]:
    """Postorder traversal (Left -> Right -> Root) using recursion.

    Time Complexity: O(n)
    Space Complexity: O(h) call stack
    """
    result: List[Any] = []

    def _traverse(node: Optional[TreeNode]) -> None:
        if node is None:
            return
        _traverse(node.left)
        _traverse(node.right)
        result.append(node.val)

    _traverse(root)
    return result


def postorder_iterative(root: Optional[TreeNode]) -> List[Any]:
    """Postorder traversal (Left -> Right -> Root) using an explicit stack.

    Time Complexity: O(n)
    Space Complexity: O(h) explicit stack
    """
    if root is None:
        return []

    result: List[Any] = []
    stack: List[TreeNode] = []
    curr: Optional[TreeNode] = root
    last_visited: Optional[TreeNode] = None

    while curr is not None or stack:
        if curr is not None:
            stack.append(curr)
            curr = curr.left
        else:
            peek_node = stack[-1]
            if peek_node.right is not None and last_visited != peek_node.right:
                curr = peek_node.right
            else:
                result.append(peek_node.val)
                last_visited = stack.pop()

    return result


def level_order(root: Optional[TreeNode]) -> List[Any]:
    """Level-order (breadth-first) traversal using collections.deque.

    Time Complexity: O(n)
    Space Complexity: O(w) queue where w is maximum width of the tree
    """
    if root is None:
        return []

    result: List[Any] = []
    queue: deque[TreeNode] = deque([root])

    while queue:
        node = queue.popleft()
        result.append(node.val)
        if node.left is not None:
            queue.append(node.left)
        if node.right is not None:
            queue.append(node.right)

    return result
