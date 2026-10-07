"""Step recorder for Binary Search Tree operations.

Instruments BST operations:
- search
- insert
- remove
- min
- max
- predecessor
- successor
- rank
- select
- create_from_array

Complies with the visualizer JSON contract schema.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from bt_visualizer.core.binary_tree import TreeNode
from bt_visualizer.core.bst import BinarySearchTree
from bt_visualizer.recorder.steps import StepRecorder


def record_search(root: Optional[TreeNode], val: Any) -> Dict[str, Any]:
    """Record step-by-step search in a BST."""
    pseudocode = [
        "if root is null: return not found",
        "if v == curr.val: return found",
        "if v < curr.val: search left subtree",
        "else: search right subtree",
    ]
    recorder = StepRecorder(operation="search", pseudocode=pseudocode)

    if root is None:
        recorder.record_step(
            tree_root=None,
            highlight_nodes=[],
            message="Tree is empty. Value not found.",
            pseudo_line=0,
        )
        return recorder.to_dict()

    curr: Optional[TreeNode] = root
    parent: Optional[TreeNode] = None
    edges: List[Tuple[str, str]] = []

    while curr is not None:
        h_edges = [(parent.node_id, curr.node_id)] if parent else []
        recorder.record_step(
            tree_root=root,
            highlight_nodes=[curr.node_id],
            highlight_edges=h_edges,
            message=f"Comparing target {val} with current node {curr.val}.",
            pseudo_line=1 if curr.val == val else (2 if val < curr.val else 3),
        )

        if curr.val == val:
            freq_msg = f" (frequency: {curr.freq})" if curr.freq > 1 else ""
            recorder.record_step(
                tree_root=root,
                highlight_nodes=[curr.node_id],
                highlight_edges=h_edges,
                message=f"Value {val} found in tree{freq_msg}!",
                pseudo_line=1,
            )
            return recorder.to_dict()
        elif val < curr.val:
            parent = curr
            curr = curr.left
            if curr is None:
                recorder.record_step(
                    tree_root=root,
                    highlight_nodes=[parent.node_id],
                    message=f"{val} < {parent.val}, but left child is null. Value {val} not found.",
                    pseudo_line=0,
                )
        else:
            parent = curr
            curr = curr.right
            if curr is None:
                recorder.record_step(
                    tree_root=root,
                    highlight_nodes=[parent.node_id],
                    message=f"{val} > {parent.val}, but right child is null. Value {val} not found.",
                    pseudo_line=0,
                )

    return recorder.to_dict()


def record_insert(root: Optional[TreeNode], val: Any) -> Dict[str, Any]:
    """Record step-by-step insertion into a BST (incrementing freq on duplicate)."""
    pseudocode = [
        "if tree is empty: create root node",
        "if v == curr.val: increment curr.freq",
        "if v < curr.val: go left (insert if null)",
        "else: go right (insert if null)",
    ]
    recorder = StepRecorder(operation="insert", pseudocode=pseudocode)

    # Work on a clone so we don't prematurely mutate if original is passed
    tree_root = root.clone() if root is not None else None

    if tree_root is None:
        new_node = TreeNode(val)
        recorder.record_step(
            tree_root=None,
            highlight_nodes=[],
            message=f"Tree is empty. Creating root node with value {val}.",
            pseudo_line=0,
        )
        recorder.record_step(
            tree_root=new_node,
            highlight_nodes=[new_node.node_id],
            message=f"Root node {val} created.",
            pseudo_line=0,
        )
        return recorder.to_dict()

    curr: TreeNode = tree_root
    parent: Optional[TreeNode] = None

    while True:
        h_edges = [(parent.node_id, curr.node_id)] if parent else []
        recorder.record_step(
            tree_root=tree_root,
            highlight_nodes=[curr.node_id],
            highlight_edges=h_edges,
            message=f"Comparing {val} with current node {curr.val}.",
            pseudo_line=1 if val == curr.val else (2 if val < curr.val else 3),
        )

        if val == curr.val:
            curr.freq += 1
            recorder.record_step(
                tree_root=tree_root,
                highlight_nodes=[curr.node_id],
                highlight_edges=h_edges,
                message=f"Duplicate value {val} found. Incremented frequency to {curr.freq}.",
                pseudo_line=1,
            )
            break
        elif val < curr.val:
            if curr.left is None:
                new_node = TreeNode(val)
                curr.left = new_node
                recorder.record_step(
                    tree_root=tree_root,
                    highlight_nodes=[new_node.node_id],
                    highlight_edges=[(curr.node_id, new_node.node_id)],
                    message=f"Inserted {val} as left child of {curr.val}.",
                    pseudo_line=2,
                )
                break
            else:
                parent = curr
                curr = curr.left
        else:
            if curr.right is None:
                new_node = TreeNode(val)
                curr.right = new_node
                recorder.record_step(
                    tree_root=tree_root,
                    highlight_nodes=[new_node.node_id],
                    highlight_edges=[(curr.node_id, new_node.node_id)],
                    message=f"Inserted {val} as right child of {curr.val}.",
                    pseudo_line=3,
                )
                break
            else:
                parent = curr
                curr = curr.right

    return recorder.to_dict()


def record_remove(root: Optional[TreeNode], val: Any) -> Dict[str, Any]:
    """Record step-by-step removal from a BST adhering to required pseudocode."""
    pseudocode = [
        "search for v",
        "if v's freq > 1, decrement by 1",
        "else if v is a leaf, remove leaf v",
        "else if v has 1 child, bypass v",
        "else replace v with successor",
    ]
    recorder = StepRecorder(operation="remove", pseudocode=pseudocode)

    if root is None:
        recorder.record_step(
            tree_root=None,
            highlight_nodes=[],
            message=f"Tree is empty. Cannot remove {val}.",
            pseudo_line=0,
        )
        return recorder.to_dict()

    tree_root: Optional[TreeNode] = root.clone()

    # Step 1: Search for v
    curr: Optional[TreeNode] = tree_root
    parent: Optional[TreeNode] = None
    h_edges: List[Tuple[str, str]] = []

    while curr is not None and curr.val != val:
        h_edges = [(parent.node_id, curr.node_id)] if parent else []
        recorder.record_step(
            tree_root=tree_root,
            highlight_nodes=[curr.node_id],
            highlight_edges=h_edges,
            message=f"Searching for {val}: currently at {curr.val}.",
            pseudo_line=0,
        )
        parent = curr
        if val < curr.val:
            curr = curr.left
        else:
            curr = curr.right

    if curr is None:
        recorder.record_step(
            tree_root=tree_root,
            highlight_nodes=[],
            message=f"Value {val} not found in tree. Removal halted.",
            pseudo_line=0,
        )
        return recorder.to_dict()

    # Target found
    target_node = curr
    recorder.record_step(
        tree_root=tree_root,
        highlight_nodes=[target_node.node_id],
        message=f"Found target node {val}.",
        pseudo_line=0,
    )

    # Case 2: freq > 1
    if target_node.freq > 1:
        target_node.freq -= 1
        recorder.record_step(
            tree_root=tree_root,
            highlight_nodes=[target_node.node_id],
            message=f"Node {val} has freq > 1. Decremented frequency to {target_node.freq}. Removal of {val} is complete.",
            pseudo_line=1,
        )
        return recorder.to_dict()

    # Case 3: Leaf
    if target_node.left is None and target_node.right is None:
        recorder.record_step(
            tree_root=tree_root,
            highlight_nodes=[target_node.node_id],
            message=f"Target node {val} is a leaf node.",
            pseudo_line=2,
        )
        if parent is None:
            # Removing root
            tree_root = None
        elif parent.left == target_node:
            parent.left = None
        else:
            parent.right = None

        recorder.record_step(
            tree_root=tree_root,
            highlight_nodes=[],
            message=f"Removal of {val} is complete.",
            pseudo_line=2,
        )
        return recorder.to_dict()

    # Case 4: One child
    if target_node.left is None or target_node.right is None:
        child = target_node.left if target_node.left is not None else target_node.right
        recorder.record_step(
            tree_root=tree_root,
            highlight_nodes=[target_node.node_id, child.node_id],
            highlight_edges=[(target_node.node_id, child.node_id)],
            message=f"Node {val} has 1 child ({child.val}). Bypassing {val}.",
            pseudo_line=3,
        )
        if parent is None:
            tree_root = child
        elif parent.left == target_node:
            parent.left = child
        else:
            parent.right = child

        recorder.record_step(
            tree_root=tree_root,
            highlight_nodes=[child.node_id],
            message=f"Removal of {val} is complete.",
            pseudo_line=3,
        )
        return recorder.to_dict()

    # Case 5: Two children
    recorder.record_step(
        tree_root=tree_root,
        highlight_nodes=[target_node.node_id],
        message=f"Node {val} has 2 children. Finding inorder successor in right subtree.",
        pseudo_line=4,
    )

    # Find successor (min node in right subtree)
    succ_parent = target_node
    succ = target_node.right
    succ_edges = [(target_node.node_id, succ.node_id)]

    while succ.left is not None:
        succ_parent = succ
        succ = succ.left
        succ_edges.append((succ_parent.node_id, succ.node_id))

    recorder.record_step(
        tree_root=tree_root,
        highlight_nodes=[target_node.node_id, succ.node_id],
        highlight_edges=succ_edges,
        message=f"Found inorder successor {succ.val}. Replacing {val} with {succ.val}.",
        pseudo_line=4,
    )

    # Replace target data with successor data
    target_node.val = succ.val
    target_node.freq = succ.freq

    # Remove successor from right subtree
    if succ_parent.left == succ:
        succ_parent.left = succ.right
    else:
        succ_parent.right = succ.right

    recorder.record_step(
        tree_root=tree_root,
        highlight_nodes=[target_node.node_id],
        message=f"Removal of {val} is complete.",
        pseudo_line=4,
    )

    return recorder.to_dict()


def record_min(root: Optional[TreeNode]) -> Dict[str, Any]:
    """Record step-by-step min query in a BST."""
    pseudocode = [
        "if tree is empty: return null",
        "while curr.left exists: go left",
        "return curr.val (minimum)",
    ]
    recorder = StepRecorder(operation="min", pseudocode=pseudocode)

    if root is None:
        recorder.record_step(
            tree_root=None,
            highlight_nodes=[],
            message="Tree is empty. Minimum does not exist.",
            pseudo_line=0,
        )
        return recorder.to_dict()

    curr: TreeNode = root
    parent: Optional[TreeNode] = None

    while curr.left is not None:
        h_edges = [(parent.node_id, curr.node_id)] if parent else []
        recorder.record_step(
            tree_root=root,
            highlight_nodes=[curr.node_id],
            highlight_edges=h_edges,
            message=f"Node {curr.val} has left child. Traversing left.",
            pseudo_line=1,
        )
        parent = curr
        curr = curr.left

    h_edges = [(parent.node_id, curr.node_id)] if parent else []
    recorder.record_step(
        tree_root=root,
        highlight_nodes=[curr.node_id],
        highlight_edges=h_edges,
        message=f"Node {curr.val} has no left child. Minimum value is {curr.val}.",
        pseudo_line=2,
    )

    return recorder.to_dict()


def record_max(root: Optional[TreeNode]) -> Dict[str, Any]:
    """Record step-by-step max query in a BST."""
    pseudocode = [
        "if tree is empty: return null",
        "while curr.right exists: go right",
        "return curr.val (maximum)",
    ]
    recorder = StepRecorder(operation="max", pseudocode=pseudocode)

    if root is None:
        recorder.record_step(
            tree_root=None,
            highlight_nodes=[],
            message="Tree is empty. Maximum does not exist.",
            pseudo_line=0,
        )
        return recorder.to_dict()

    curr: TreeNode = root
    parent: Optional[TreeNode] = None

    while curr.right is not None:
        h_edges = [(parent.node_id, curr.node_id)] if parent else []
        recorder.record_step(
            tree_root=root,
            highlight_nodes=[curr.node_id],
            highlight_edges=h_edges,
            message=f"Node {curr.val} has right child. Traversing right.",
            pseudo_line=1,
        )
        parent = curr
        curr = curr.right

    h_edges = [(parent.node_id, curr.node_id)] if parent else []
    recorder.record_step(
        tree_root=root,
        highlight_nodes=[curr.node_id],
        highlight_edges=h_edges,
        message=f"Node {curr.val} has no right child. Maximum value is {curr.val}.",
        pseudo_line=2,
    )

    return recorder.to_dict()


def record_predecessor(root: Optional[TreeNode], val: Any) -> Dict[str, Any]:
    """Record step-by-step inorder predecessor search."""
    pseudocode = [
        "start at root, pred = null",
        "if v <= curr.val: go left",
        "else: pred = curr, go right",
        "return pred",
    ]
    recorder = StepRecorder(operation="predecessor", pseudocode=pseudocode)

    if root is None:
        recorder.record_step(
            tree_root=None,
            message="Tree is empty. Predecessor is null.",
            pseudo_line=0,
        )
        return recorder.to_dict()

    curr: Optional[TreeNode] = root
    pred: Optional[TreeNode] = None

    while curr is not None:
        pred_id = [pred.node_id] if pred else []
        recorder.record_step(
            tree_root=root,
            highlight_nodes=[curr.node_id] + pred_id,
            message=f"Comparing target {val} with current {curr.val} (candidate pred: {pred.val if pred else 'None'}).",
            pseudo_line=1 if val <= curr.val else 2,
        )
        if val <= curr.val:
            curr = curr.left
        else:
            pred = curr
            curr = curr.right

    pred_res = pred.val if pred else "None"
    pred_nodes = [pred.node_id] if pred else []
    recorder.record_step(
        tree_root=root,
        highlight_nodes=pred_nodes,
        message=f"Inorder predecessor of {val} is {pred_res}.",
        pseudo_line=3,
    )
    return recorder.to_dict()


def record_successor(root: Optional[TreeNode], val: Any) -> Dict[str, Any]:
    """Record step-by-step inorder successor search."""
    pseudocode = [
        "start at root, succ = null",
        "if v >= curr.val: go right",
        "else: succ = curr, go left",
        "return succ",
    ]
    recorder = StepRecorder(operation="successor", pseudocode=pseudocode)

    if root is None:
        recorder.record_step(
            tree_root=None,
            message="Tree is empty. Successor is null.",
            pseudo_line=0,
        )
        return recorder.to_dict()

    curr: Optional[TreeNode] = root
    succ: Optional[TreeNode] = None

    while curr is not None:
        succ_id = [succ.node_id] if succ else []
        recorder.record_step(
            tree_root=root,
            highlight_nodes=[curr.node_id] + succ_id,
            message=f"Comparing target {val} with current {curr.val} (candidate succ: {succ.val if succ else 'None'}).",
            pseudo_line=1 if val >= curr.val else 2,
        )
        if val >= curr.val:
            curr = curr.right
        else:
            succ = curr
            curr = curr.left

    succ_res = succ.val if succ else "None"
    succ_nodes = [succ.node_id] if succ else []
    recorder.record_step(
        tree_root=root,
        highlight_nodes=succ_nodes,
        message=f"Inorder successor of {val} is {succ_res}.",
        pseudo_line=3,
    )
    return recorder.to_dict()


def record_rank(root: Optional[TreeNode], val: Any) -> Dict[str, Any]:
    """Record step-by-step rank calculation (elements strictly less than val)."""
    pseudocode = [
        "rank = 0, curr = root",
        "if v < curr.val: search left subtree",
        "if v > curr.val: rank += left_size + freq, search right subtree",
        "if v == curr.val: rank += left_size, return rank",
    ]
    recorder = StepRecorder(operation="rank", pseudocode=pseudocode)

    if root is None:
        recorder.record_step(
            tree_root=None,
            message="Tree is empty. Rank is 0.",
            pseudo_line=0,
        )
        return recorder.to_dict()

    bst = BinarySearchTree(root)
    curr: Optional[TreeNode] = root
    accumulated_rank = 0

    while curr is not None:
        left_count = bst._total_count(curr.left)
        recorder.record_step(
            tree_root=root,
            highlight_nodes=[curr.node_id],
            message=f"At node {curr.val}: left subtree size={left_count}, current accumulated rank={accumulated_rank}.",
            pseudo_line=1 if val < curr.val else (2 if val > curr.val else 3),
        )

        if val < curr.val:
            curr = curr.left
        elif val > curr.val:
            accumulated_rank += left_count + curr.freq
            curr = curr.right
        else:
            accumulated_rank += left_count
            break

    recorder.record_step(
        tree_root=root,
        highlight_nodes=[curr.node_id] if curr else [],
        message=f"Final rank of {val} is {accumulated_rank} (elements strictly smaller than {val}).",
        pseudo_line=3 if curr and curr.val == val else 0,
    )
    return recorder.to_dict()


def record_select(root: Optional[TreeNode], k: int) -> Dict[str, Any]:
    """Record step-by-step select operation (k-th smallest, 1-indexed)."""
    pseudocode = [
        "if k < 1 or k > total_size: return null",
        "if k <= left_size: search left subtree",
        "else if k <= left_size + freq: return curr.val",
        "else: k -= left_size + freq, search right subtree",
    ]
    recorder = StepRecorder(operation="select", pseudocode=pseudocode)

    bst = BinarySearchTree(root)
    total_elements = bst.size(include_duplicates=True)

    if k < 1 or k > total_elements or root is None:
        recorder.record_step(
            tree_root=root,
            message=f"k={k} is out of bounds (valid range: 1 to {total_elements}).",
            pseudo_line=0,
        )
        return recorder.to_dict()

    curr: Optional[TreeNode] = root
    target_k = k

    while curr is not None:
        left_count = bst._total_count(curr.left)
        recorder.record_step(
            tree_root=root,
            highlight_nodes=[curr.node_id],
            message=f"At node {curr.val}: left_size={left_count}, looking for k={target_k}.",
            pseudo_line=1 if target_k <= left_count else (2 if target_k <= left_count + curr.freq else 3),
        )

        if target_k <= left_count:
            curr = curr.left
        elif target_k <= left_count + curr.freq:
            recorder.record_step(
                tree_root=root,
                highlight_nodes=[curr.node_id],
                message=f"Found {k}-th smallest element: {curr.val}.",
                pseudo_line=2,
            )
            return recorder.to_dict()
        else:
            target_k -= (left_count + curr.freq)
            curr = curr.right

    return recorder.to_dict()


def record_create_from_array(arr: List[Any]) -> Dict[str, Any]:
    """Record step-by-step creation of BST from an array."""
    pseudocode = [
        "tree = empty BST",
        "for each val in array: insert(val)",
        "BST creation complete",
    ]
    recorder = StepRecorder(operation="create_from_array", pseudocode=pseudocode)

    recorder.record_step(
        tree_root=None,
        message=f"Starting BST creation from array: {arr}.",
        pseudo_line=0,
    )

    bst = BinarySearchTree()
    for idx, val in enumerate(arr):
        bst.insert(val)
        node = bst.search(val)
        node_id = [node.node_id] if node else []
        recorder.record_step(
            tree_root=bst.root,
            highlight_nodes=node_id,
            message=f"[{idx+1}/{len(arr)}] Inserted {val} into BST.",
            pseudo_line=1,
        )

    recorder.record_step(
        tree_root=bst.root,
        highlight_nodes=[],
        message=f"BST creation from array complete ({len(arr)} values processed).",
        pseudo_line=2,
    )
    return recorder.to_dict()
