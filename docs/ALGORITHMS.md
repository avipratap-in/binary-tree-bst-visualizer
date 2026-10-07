# Data Structures & Algorithms Reference Guide
## Binary Tree & Binary Search Tree Visualizer

This document provides a clear, conceptual explanation of every algorithm implemented in the project. It is structured to serve directly as a reference for academic analysis, documentation, and the DSAP Capstone Report.

---

## 1. Node Representation & Duplicate Handling

### The `TreeNode` Model
A binary tree node consists of:
- `val`: The primary key or value stored.
- `freq`: A frequency counter for duplicate handling (default: `1`).
- `left`: Pointer to the left subtree.
- `right`: Pointer to the right subtree.
- `node_id`: A unique string identifier used by the visualizer to track nodes across animation frames.

### Why Frequency-Based Duplicate Handling?
Standard BST rules require strict ordering ($left < root < right$). Handling duplicates by either placing identical keys into the left or right subtrees causes asymmetric, unbalanced, and distorted trees, degrading query performance toward $O(n)$. 

By incorporating a `freq` counter:
- Each distinct key appears as a single node in the tree.
- Inserting a duplicate simply increments `node.freq`.
- Deleting an element decrements `node.freq` if `freq > 1`, only physically deleting the node when `freq == 1`.
- This preserves the strict BST invariant ($left.val < node.val < right.val$) while maintaining compact tree heights.

---

## 2. Binary Search Tree (BST) Operations

### Search
- **Concept:** Start at the root. Compare target $v$ with current node:
  - If $v == curr.val$, the element is found.
  - If $v < curr.val$, recurse/iterate left.
  - If $v > curr.val$, recurse/iterate right.
  - If a `null` reference is hit, the element is not in the tree.
- **Time Complexity:** Average $O(\log n)$, Worst $O(n)$ (skewed tree).
- **Space Complexity:** $O(1)$ iterative, $O(h)$ recursive.

### Insertion
- **Concept:** Search down the tree to find the correct insertion location:
  - If target $v$ matches an existing node, increment `node.freq += 1`.
  - Otherwise, attach a new `TreeNode(v)` as the left or right child of the appropriate leaf.
- **Time Complexity:** Average $O(\log n)$, Worst $O(n)$.

---

### Removal (The Three Cases)
Removing a node with value $v$ requires searching for it and handling three structural cases when `freq == 1`:

```
Case 1: Leaf Node        Case 2: One Child        Case 3: Two Children
     (50)                    (50)                       (50) [Target]
    /    \                  /    \                     /    \
  (30)   (70)             (30)   (70)                (30)   (70)
  /                        /                         /  \   /  \
(20) [Target]            (20) [Target]             (20)(40)(60)(80)
   \                       /                                /
 (remove directly)       (10)                             (55) [Successor]
                         (bypass 20 -> 10)         (copy 55 to root, delete 55)
```

1. **Case 1: The node is a leaf (no children).**
   - Simply sever the parent's pointer to this node (`parent.left = None` or `parent.right = None`).
2. **Case 2: The node has exactly one child.**
   - Bypass the node: link the parent directly to the node's single child (`parent.left = curr.left` or `parent.left = curr.right`).
3. **Case 3: The node has two children (Successor Replacement).**
   - **Why two children cannot be directly removed:** A binary tree node cannot have three children, nor can its subtrees be arbitrarily detached.
   - **The Inorder Successor Strategy:**
     1. Locate the **inorder successor** (the smallest value in the node's right subtree, found by going to `node.right` and then following `left` pointers as far as possible).
     2. The inorder successor is guaranteed to have **at most one child** (a right child), because if it had a left child, it wouldn't be the smallest.
     3. Copy the successor's `val` and `freq` into the target node.
     4. Delete the successor node from the right subtree (which falls into Case 1 or Case 2).
   - **Preserving the BST Invariant:** Because the successor is the smallest value in the right subtree that is still greater than everything in the left subtree, replacing the target node with the successor preserves the BST ordering invariant across all nodes.

---

### Min and Max
- **Minimum:** From root, follow `left` pointers until reaching a node with `left == None`.
- **Maximum:** From root, follow `right` pointers until reaching a node with `right == None`.
- **Complexity:** $O(h)$ time, $O(1)$ space.

### Inorder Predecessor and Successor
- **Predecessor (largest value strictly $< v$):**
  - Start at root with `pred = None`.
  - If $v \le curr.val$, move left.
  - If $v > curr.val$, record `pred = curr` as a candidate and move right.
- **Successor (smallest value strictly $> v$):**
  - Start at root with `succ = None`.
  - If $v \ge curr.val$, move right.
  - If $v < curr.val$, record `succ = curr` as a candidate and move left.
- **Complexity:** $O(h)$ time, $O(1)$ space.

### Order Statistics: Rank and Select
- **Rank ($v$):** Counts how many elements in the tree are strictly smaller than $v$.
  - At each node:
    - If $v < curr.val$, search left.
    - If $v > curr.val$, add `size(curr.left) + curr.freq` to accumulated count and search right.
    - If $v == curr.val$, add `size(curr.left)` and return.
- **Select ($k$):** Finds the $k$-th smallest element (1-indexed).
  - Let $L = size(curr.left)$.
  - If $k \le L$, recurse left.
  - Else if $k \le L + curr.freq$, return `curr.val`.
  - Else, set $k = k - (L + curr.freq)$ and recurse right.
- **Complexity:** $O(h)$ time, $O(h)$ space.

---

## 3. Tree Traversals

| Traversal | Order | Recursive Principle | Iterative Mechanism |
| :--- | :--- | :--- | :--- |
| **Preorder** | Root $\to$ Left $\to$ Right | Visit node, recurse left, recurse right | Explicit Stack: Pop node, push right child first, then left child |
| **Inorder** | Left $\to$ Root $\to$ Right | Recurse left, visit node, recurse right | Explicit Stack: Push all left nodes, pop, visit, advance to right |
| **Postorder** | Left $\to$ Right $\to$ Root | Recurse left, recurse right, visit node | Explicit Stack with `last_visited` pointer to avoid premature root processing |
| **Level-Order** | Level by level (BFS) | N/A (inherently queue-driven) | FIFO Queue (`collections.deque`): Pop node, append left, append right |

---

## 4. Tree Structural Properties

1. **Leaf Count:** Nodes where `left == None and right == None`.
2. **Internal Node Count:** Nodes where `left != None or right != None`.
3. **Height:** Maximum depth from root to any leaf ($0$ for empty tree, $1$ for single root).
4. **Full Binary Tree:** Every node has either $0$ or $2$ children (no node has exactly 1 child).
5. **Complete Binary Tree:** All levels are completely filled except possibly the last level, where all nodes are as far left as possible. Verified using BFS queue with null detection.
6. **Perfect Binary Tree:** All internal nodes have 2 children and all leaves reside at the identical depth ($size = 2^h - 1$).
7. **Height-Balanced (AVL):** For every node in the tree, $|height(left) - height(right)| \le 1$. Computed in $O(n)$ bottom-up.

---

## 5. Tree Reconstruction Algorithms

### Reconstructing from Inorder + Preorder
- **Preorder:** Gives root order (`[root, ...left..., ...right...]`).
- **Inorder:** Divides subtrees (`[...left..., root, ...right...]`).
- **Algorithm:**
  1. Pick next root from preorder sequence.
  2. Locate root in inorder list at index $mid$.
  3. All elements to the left of $mid$ belong to the left subtree; elements to the right belong to the right subtree.
  4. Recurse for left and right partitions.

### Reconstructing from Inorder + Postorder
- **Postorder:** Root is always the last element (`[...left..., ...right..., root]`).
- **Algorithm:**
  1. Pick root from the end of postorder.
  2. Partition inorder into left and right subtrees.
  3. Reconstruct right subtree first, then left subtree.

### Reconstructing from Inorder + Level-Order
- **Level-Order:** Root is always the first element.
- **Algorithm:**
  1. Pick root from head of level-order.
  2. Filter remaining level-order elements into two ordered lists based on membership in the left and right inorder subsets.
  3. Recurse.

---

### Preorder + Postorder Ambiguity Analysis

> **Theorem:** Preorder and Postorder traversals uniquely determine a binary tree **if and only if** the tree is a **Full Binary Tree** (every non-leaf node has two children).

#### Proof of Ambiguity for Non-Full Trees:
Consider a two-node tree consisting of root `1` and child `2`:

```
Tree A (Left child):      Tree B (Right child):
      1                         1
     /                           \
    2                             2
```

- **Traversals for Tree A:**
  - Preorder: `[1, 2]`
  - Postorder: `[2, 1]`
- **Traversals for Tree B:**
  - Preorder: `[1, 2]`
  - Postorder: `[2, 1]`

Both trees produce identical preorder and postorder sequences. Without an inorder traversal, it is mathematically impossible to determine whether node `2` is a left child or a right child.

#### Detection in Code:
During recursive construction:
- Root is `preorder[pre_start]`.
- Candidate left child root is `preorder[pre_start + 1]`.
- Candidate right child root is `postorder[post_end - 1]`.
- If `preorder[pre_start + 1] == postorder[post_end - 1]`, the root has **only one child**. The algorithm immediately raises `AmbiguousTreeError` rather than guessing.

---

## 6. Time and Space Complexity Summary

| Algorithm / Operation | Average Time | Worst-Case Time | Space Complexity |
| :--- | :--- | :--- | :--- |
| **BST Search** | $O(\log n)$ | $O(n)$ | $O(1)$ |
| **BST Insert** | $O(\log n)$ | $O(n)$ | $O(h)$ |
| **BST Remove** | $O(\log n)$ | $O(n)$ | $O(h)$ |
| **BST Min / Max** | $O(\log n)$ | $O(n)$ | $O(1)$ |
| **BST Predecessor / Successor** | $O(\log n)$ | $O(n)$ | $O(1)$ |
| **BST Rank / Select** | $O(\log n)$ | $O(n)$ | $O(h)$ |
| **BST Create from Array** | $O(n \log n)$ | $O(n^2)$ | $O(n)$ |
| **Preorder / Inorder / Postorder (DFS)** | $O(n)$ | $O(n)$ | $O(h)$ |
| **Level-Order (BFS)** | $O(n)$ | $O(n)$ | $O(w) \le O(n)$ |
| **Property Analyzers (size, height, AVL)** | $O(n)$ | $O(n)$ | $O(h)$ |
| **Build: Inorder + Preorder** | $O(n)$ | $O(n)$ | $O(n)$ |
| **Build: Inorder + Postorder** | $O(n)$ | $O(n)$ | $O(n)$ |
| **Build: Inorder + Level-Order** | $O(n^2)$ | $O(n^2)$ | $O(n)$ |
| **Build: Preorder + Postorder (Full)** | $O(n)$ | $O(n)$ | $O(n)$ |
| **Build: BST from Preorder / Postorder** | $O(n)$ | $O(n)$ | $O(n)$ |
