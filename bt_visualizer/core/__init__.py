"""Pure Data Structures & Algorithms Core Layer.

Exports core TreeNode, BinaryTree, BinarySearchTree, traversals,
property analyzers, and traversal-based builders.
"""
from bt_visualizer.core.binary_tree import TreeNode, BinaryTree
from bt_visualizer.core.bst import BinarySearchTree
from bt_visualizer.core.traversals import (
    preorder_recursive,
    preorder_iterative,
    inorder_recursive,
    inorder_iterative,
    postorder_recursive,
    postorder_iterative,
    level_order,
)
from bt_visualizer.core.properties import (
    leaf_count,
    internal_node_count,
    height,
    size,
    is_full,
    is_complete,
    is_perfect,
    is_balanced,
    get_all_properties,
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

__all__ = [
    "TreeNode",
    "BinaryTree",
    "BinarySearchTree",
    "preorder_recursive",
    "preorder_iterative",
    "inorder_recursive",
    "inorder_iterative",
    "postorder_recursive",
    "postorder_iterative",
    "level_order",
    "leaf_count",
    "internal_node_count",
    "height",
    "size",
    "is_full",
    "is_complete",
    "is_perfect",
    "is_balanced",
    "get_all_properties",
    "TreeBuildError",
    "AmbiguousTreeError",
    "build_from_inorder_preorder",
    "build_from_inorder_postorder",
    "build_from_inorder_level_order",
    "build_from_preorder_postorder",
    "build_bst_from_preorder",
    "build_bst_from_postorder",
]
