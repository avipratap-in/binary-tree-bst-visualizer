"""Binary Search Tree (BST) operations and data structure.

Includes duplicate handling via frequency counters on TreeNode.
Complexity:
- Balanced BST: O(log n) time for search, insert, remove, min, max, pred, succ, rank, select.
- Skewed BST: O(n) time for all operations.
- Space complexity: O(h) recursion stack (or O(1) iterative).
"""
from __future__ import annotations

from typing import Any, List, Optional
from bt_visualizer.core.binary_tree import TreeNode


class BinarySearchTree:
    """Pure Binary Search Tree implementation with frequency-based duplicate handling."""

    def __init__(self, root: Optional[TreeNode] = None) -> None:
        self.root = root

    def insert(self, val: Any) -> TreeNode:
        """Insert a value into the BST.

        If the value already exists, increments its frequency counter.
        Returns the inserted or updated TreeNode.

        Time Complexity: O(h) where h is tree height.
        Space Complexity: O(h) recursion stack.
        """
        if self.root is None:
            self.root = TreeNode(val)
            return self.root

        def _insert(node: TreeNode) -> TreeNode:
            if val == node.val:
                node.freq += 1
                return node
            elif val < node.val:
                if node.left is None:
                    node.left = TreeNode(val)
                    return node.left
                return _insert(node.left)
            else:
                if node.right is None:
                    node.right = TreeNode(val)
                    return node.right
                return _insert(node.right)

        return _insert(self.root)

    def search(self, val: Any) -> Optional[TreeNode]:
        """Search for a value in the BST.

        Returns matching TreeNode if found, else None.

        Time Complexity: O(h).
        Space Complexity: O(1) iterative.
        """
        curr = self.root
        while curr is not None:
            if val == curr.val:
                return curr
            elif val < curr.val:
                curr = curr.left
            else:
                curr = curr.right
        return None

    def remove(self, val: Any) -> bool:
        """Remove a value from the BST.

        Cases:
        - Value not found: returns False.
        - freq > 1: decrements freq by 1, returns True.
        - freq == 1:
          - Leaf: removes node.
          - One child: replaces node with its single child.
          - Two children: replaces node with inorder successor and deletes successor.
        Returns True if removed/decremented, False if not found.

        Time Complexity: O(h).
        Space Complexity: O(h) recursion stack.
        """
        target_node = self.search(val)
        if target_node is None:
            return False

        if target_node.freq > 1:
            target_node.freq -= 1
            return True

        # Structurally remove node with freq == 1
        self.root = self._delete_node(self.root, val)
        return True

    def _delete_node(self, node: Optional[TreeNode], val: Any) -> Optional[TreeNode]:
        """Helper to physically delete the node containing val."""
        if node is None:
            return None

        if val < node.val:
            node.left = self._delete_node(node.left, val)
            return node
        elif val > node.val:
            node.right = self._delete_node(node.right, val)
            return node
        else:
            # Case 1: Leaf
            if node.left is None and node.right is None:
                return None

            # Case 2: Single child
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left

            # Case 3: Two children -> find inorder successor
            succ = self._min_node(node.right)
            # Copy successor data
            node.val = succ.val
            node.freq = succ.freq
            # Delete successor from right subtree completely
            node.right = self._delete_node_completely(node.right, succ.val)
            return node

    def _delete_node_completely(self, node: Optional[TreeNode], val: Any) -> Optional[TreeNode]:
        """Helper to remove a node regardless of frequency (used for successor deletion)."""
        if node is None:
            return None

        if val < node.val:
            node.left = self._delete_node_completely(node.left, val)
            return node
        elif val > node.val:
            node.right = self._delete_node_completely(node.right, val)
            return node
        else:
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left
            succ = self._min_node(node.right)
            node.val = succ.val
            node.freq = succ.freq
            node.right = self._delete_node_completely(node.right, succ.val)
            return node

    def min(self) -> Optional[Any]:
        """Return minimum value in BST, or None if empty."""
        min_n = self._min_node(self.root)
        return min_n.val if min_n else None

    def _min_node(self, node: Optional[TreeNode]) -> Optional[TreeNode]:
        if node is None:
            return None
        curr = node
        while curr.left is not None:
            curr = curr.left
        return curr

    def max(self) -> Optional[Any]:
        """Return maximum value in BST, or None if empty."""
        max_n = self._max_node(self.root)
        return max_n.val if max_n else None

    def _max_node(self, node: Optional[TreeNode]) -> Optional[TreeNode]:
        if node is None:
            return None
        curr = node
        while curr.right is not None:
            curr = curr.right
        return curr

    def predecessor(self, val: Any) -> Optional[Any]:
        """Find inorder predecessor (largest value strictly less than val).

        Time Complexity: O(h).
        Space Complexity: O(1).
        """
        curr = self.root
        pred: Optional[TreeNode] = None

        while curr is not None:
            if val <= curr.val:
                curr = curr.left
            else:
                pred = curr
                curr = curr.right

        return pred.val if pred else None

    def successor(self, val: Any) -> Optional[Any]:
        """Find inorder successor (smallest value strictly greater than val).

        Time Complexity: O(h).
        Space Complexity: O(1).
        """
        curr = self.root
        succ: Optional[TreeNode] = None

        while curr is not None:
            if val >= curr.val:
                curr = curr.right
            else:
                succ = curr
                curr = curr.left

        return succ.val if succ else None

    def _total_count(self, node: Optional[TreeNode]) -> int:
        """Count total items in subtree including duplicate frequencies."""
        if node is None:
            return 0
        return node.freq + self._total_count(node.left) + self._total_count(node.right)

    def rank(self, val: Any) -> int:
        """Return number of elements in the BST strictly less than val.

        Accounts for duplicate node frequencies.

        Time Complexity: O(h).
        Space Complexity: O(h).
        """
        def _rank(node: Optional[TreeNode]) -> int:
            if node is None:
                return 0
            if val < node.val:
                return _rank(node.left)
            elif val > node.val:
                left_cnt = self._total_count(node.left)
                return left_cnt + node.freq + _rank(node.right)
            else:
                # Elements strictly less than val are exactly those in node.left
                return self._total_count(node.left)

        return _rank(self.root)

    def select(self, k: int) -> Optional[Any]:
        """Return the k-th smallest element in the BST (1-indexed).

        Accounts for duplicate node frequencies.
        Returns None if k < 1 or k > total elements.

        Time Complexity: O(h).
        Space Complexity: O(h).
        """
        if k < 1 or k > self.size(include_duplicates=True):
            return None

        def _select(node: Optional[TreeNode], target_k: int) -> Optional[Any]:
            if node is None:
                return None
            left_count = self._total_count(node.left)

            if target_k <= left_count:
                return _select(node.left, target_k)
            elif target_k <= left_count + node.freq:
                return node.val
            else:
                return _select(node.right, target_k - left_count - node.freq)

        return _select(self.root, k)

    def size(self, include_duplicates: bool = True) -> int:
        """Return size of BST.

        If include_duplicates is True, sums frequencies;
        if False, counts distinct nodes.

        Time Complexity: O(n).
        Space Complexity: O(h).
        """
        def _size(node: Optional[TreeNode]) -> int:
            if node is None:
                return 0
            count = node.freq if include_duplicates else 1
            return count + _size(node.left) + _size(node.right)

        return _size(self.root)

    def height(self) -> int:
        """Return height of BST (0 if empty, 1 for single node).

        Time Complexity: O(n).
        Space Complexity: O(h).
        """
        def _height(node: Optional[TreeNode]) -> int:
            if node is None:
                return 0
            return 1 + max(_height(node.left), _height(node.right))

        return _height(self.root)

    @classmethod
    def create_from_array(cls, arr: List[Any]) -> BinarySearchTree:
        """Build a BST by inserting elements from an iterable in order.

        Time Complexity: O(n * h) where h can be O(log n) to O(n).
        Space Complexity: O(n).
        """
        tree = cls()
        for item in arr:
            tree.insert(item)
        return tree

    def is_valid_bst(self) -> bool:
        """Verify that the BST property strictly holds for all nodes.

        Since duplicates are handled via node.freq, left.val < node.val < right.val.

        Time Complexity: O(n).
        Space Complexity: O(h).
        """
        def _validate(node: Optional[TreeNode], min_val: Any, max_val: Any) -> bool:
            if node is None:
                return True
            if min_val is not None and node.val <= min_val:
                return False
            if max_val is not None and node.val >= max_val:
                return False
            return _validate(node.left, min_val, node.val) and _validate(node.right, node.val, max_val)

        return _validate(self.root, None, None)
