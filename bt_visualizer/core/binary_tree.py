"""Binary Tree node definitions and core binary tree abstractions.

Complexity:
- TreeNode initialization and serialization: O(1) time, O(1) space.
- BinaryTree from_level_order: O(n) time, O(n) space.
"""
from __future__ import annotations

import itertools
from typing import Any, Dict, List, Optional
from collections import deque

_ID_COUNTER = itertools.count(1)


def generate_node_id() -> str:
    """Generate a unique sequential string identifier for visualizer nodes."""
    return f"node_{next(_ID_COUNTER)}"


class TreeNode:
    """Represents a node in a binary tree.

    Attributes:
        val: Node value.
        freq: Frequency or occurrence count of the value (for BST duplicate handling).
        left: Left child reference.
        right: Right child reference.
        node_id: Unique string identifier for tracking in visualization steps.
    """

    def __init__(
        self,
        val: Any,
        left: Optional[TreeNode] = None,
        right: Optional[TreeNode] = None,
        node_id: Optional[str] = None,
        freq: int = 1,
    ) -> None:
        self.val = val
        self.freq = freq
        self.left = left
        self.right = right
        self.node_id = node_id if node_id is not None else generate_node_id()

    @property
    def value(self) -> Any:
        """Alias for val."""
        return self.val

    @value.setter
    def value(self, new_val: Any) -> None:
        self.val = new_val

    def to_dict(self) -> Dict[str, Any]:
        """Serialize tree node to dictionary conforming to visualizer step schema.

        Time Complexity: O(n) where n is size of subtree.
        Space Complexity: O(h) recursion stack.
        """
        return {
            "id": self.node_id,
            "value": self.val,
            "val": self.val,
            "freq": self.freq,
            "left": self.left.to_dict() if self.left is not None else None,
            "right": self.right.to_dict() if self.right is not None else None,
        }

    def clone(self) -> TreeNode:
        """Create a deep copy of the subtree preserving values and IDs.

        Time Complexity: O(n) where n is size of subtree.
        Space Complexity: O(h) call stack.
        """
        cloned = TreeNode(
            val=self.val,
            node_id=self.node_id,
            freq=self.freq,
        )
        if self.left is not None:
            cloned.left = self.left.clone()
        if self.right is not None:
            cloned.right = self.right.clone()
        return cloned

    def __repr__(self) -> str:
        freq_str = f" x{self.freq}" if self.freq > 1 else ""
        return f"TreeNode({self.val}{freq_str}, id={self.node_id})"


class BinaryTree:
    """General Binary Tree wrapper.

    Allows construction from level-order lists (e.g. [1, 2, 3, None, 4]).
    """

    def __init__(self, root: Optional[TreeNode] = None) -> None:
        self.root = root

    @classmethod
    def from_level_order(cls, values: List[Optional[Any]]) -> BinaryTree:
        """Build a binary tree from a level-order representation.

        None indicates an empty/missing child.

        Time Complexity: O(n) where n is len(values).
        Space Complexity: O(n) for queue and tree nodes.
        """
        if not values or values[0] is None:
            return cls(None)

        root = TreeNode(values[0])
        queue: deque[TreeNode] = deque([root])
        idx = 1
        n = len(values)

        while queue and idx < n:
            curr = queue.popleft()

            # Left child
            if idx < n:
                left_val = values[idx]
                idx += 1
                if left_val is not None:
                    curr.left = TreeNode(left_val)
                    queue.append(curr.left)

            # Right child
            if idx < n:
                right_val = values[idx]
                idx += 1
                if right_val is not None:
                    curr.right = TreeNode(right_val)
                    queue.append(curr.right)

        return cls(root)

    def to_level_order(self) -> List[Optional[Any]]:
        """Return level-order list of values with trailing Nones pruned.

        Time Complexity: O(n).
        Space Complexity: O(n).
        """
        if not self.root:
            return []

        res: List[Optional[Any]] = []
        queue: deque[Optional[TreeNode]] = deque([self.root])

        while queue:
            curr = queue.popleft()
            if curr is not None:
                res.append(curr.val)
                queue.append(curr.left)
                queue.append(curr.right)
            else:
                res.append(None)

        # Trim trailing Nones
        while res and res[-1] is None:
            res.pop()
        return res

    def size(self) -> int:
        """Return total number of nodes.

        Time Complexity: O(n).
        Space Complexity: O(h).
        """
        def _size(node: Optional[TreeNode]) -> int:
            if not node:
                return 0
            return 1 + _size(node.left) + _size(node.right)

        return _size(self.root)

    def height(self) -> int:
        """Return height of tree (0 for empty tree, 1 for single root).

        Time Complexity: O(n).
        Space Complexity: O(h).
        """
        def _height(node: Optional[TreeNode]) -> int:
            if not node:
                return 0
            return 1 + max(_height(node.left), _height(node.right))

        return _height(self.root)

    def is_empty(self) -> bool:
        """Check if tree is empty."""
        return self.root is None
