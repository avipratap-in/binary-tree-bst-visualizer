"""Core API request handlers independent of web framework (Flask/Pyodide).

Provides pure Python implementations for all visualizer API endpoints and
a single unified dispatcher: handle(route: str, payload_json: str) -> str.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

try:
    from bt_visualizer.core.binary_tree import BinaryTree, TreeNode
    from bt_visualizer.core.builders import AmbiguousTreeError, TreeBuildError
    from bt_visualizer.core.generators import (
        generate_random_binary_tree,
        generate_traversal_pair,
        get_random_labels,
    )
    from bt_visualizer.core.parsing import parse_sequence
    from bt_visualizer.core.properties import get_all_properties
    from bt_visualizer.core.validator import validate_build_input
    from bt_visualizer.recorder.bst_recorder import (
        record_create_from_array,
        record_insert,
        record_max,
        record_min,
        record_predecessor,
        record_rank,
        record_remove,
        record_search,
        record_select,
        record_successor,
    )
    from bt_visualizer.recorder.build_recorder import (
        record_build_bst_from_postorder,
        record_build_bst_from_preorder,
        record_build_inorder_level_order,
        record_build_inorder_postorder,
        record_build_inorder_preorder,
        record_build_preorder_postorder,
    )
    from bt_visualizer.recorder.steps import StepRecorder
    from bt_visualizer.recorder.traversal_recorder import (
        record_inorder,
        record_level_order,
        record_postorder,
        record_preorder,
    )
except ImportError:
    from core.binary_tree import BinaryTree, TreeNode
    from core.builders import AmbiguousTreeError, TreeBuildError
    from core.generators import (
        generate_random_binary_tree,
        generate_traversal_pair,
        get_random_labels,
    )
    from core.parsing import parse_sequence
    from core.properties import get_all_properties
    from core.validator import validate_build_input
    from recorder.bst_recorder import (
        record_create_from_array,
        record_insert,
        record_max,
        record_min,
        record_predecessor,
        record_rank,
        record_remove,
        record_search,
        record_select,
        record_successor,
    )
    from recorder.build_recorder import (
        record_build_bst_from_postorder,
        record_build_bst_from_preorder,
        record_build_inorder_level_order,
        record_build_inorder_postorder,
        record_build_inorder_preorder,
        record_build_preorder_postorder,
    )
    from recorder.steps import StepRecorder
    from recorder.traversal_recorder import (
        record_inorder,
        record_level_order,
        record_postorder,
        record_preorder,
    )


def deserialize_tree(data: Optional[Dict[str, Any]]) -> Optional[TreeNode]:
    """Recursively reconstruct a TreeNode subtree from JSON dict.

    Handles both 'value' and 'val' keys, frequencies, and IDs.
    """
    if data is None:
        return None
    if not isinstance(data, dict):
        raise ValueError("Tree node must be a JSON object or null.")

    val = data.get("value") if "value" in data else data.get("val")
    if val is None:
        raise ValueError("Tree node must contain a 'value' or 'val' attribute.")

    node_id = str(data.get("id")) if data.get("id") else None
    freq = int(data.get("freq", 1))

    left = deserialize_tree(data.get("left"))
    right = deserialize_tree(data.get("right"))

    return TreeNode(
        val=val,
        left=left,
        right=right,
        node_id=node_id,
        freq=freq,
    )


# =========================================================================
# Route Handlers
# =========================================================================

def handle_health(payload: Optional[Dict[str, Any]] = None) -> tuple[Dict[str, Any], int]:
    return {"status": "ok", "service": "bt_visualizer"}, 200


def handle_bst_create(payload: Optional[Dict[str, Any]]) -> tuple[Dict[str, Any], int]:
    if not isinstance(payload, dict) or "values" not in payload:
        return {"error": "Bad Request", "message": "Payload must include a 'values' list."}, 400

    values = payload["values"]
    if not isinstance(values, list):
        return {"error": "Bad Request", "message": "'values' must be an array."}, 400

    result = record_create_from_array(values)
    return result, 200


def handle_bst_operation(payload: Optional[Dict[str, Any]]) -> tuple[Dict[str, Any], int]:
    if not isinstance(payload, dict):
        return {"error": "Bad Request", "message": "Invalid JSON body."}, 400

    op = payload.get("op")
    valid_ops = {"insert", "remove", "search", "min", "max", "pred", "succ", "rank", "select"}
    if op not in valid_ops:
        return {
            "error": "Bad Request",
            "message": f"Unsupported operation '{op}'. Supported: {sorted(list(valid_ops))}.",
        }, 400

    try:
        tree_root = deserialize_tree(payload.get("tree"))
    except Exception as e:
        return {"error": "Bad Request", "message": f"Malformed tree structure: {str(e)}"}, 400

    val = payload.get("value")
    if op in {"insert", "remove", "search", "pred", "succ", "rank", "select"}:
        if val is None:
            return {
                "error": "Bad Request",
                "message": f"Operation '{op}' requires a 'value' parameter.",
            }, 400

    try:
        if op == "insert":
            result = record_insert(tree_root, val)
        elif op == "remove":
            result = record_remove(tree_root, val)
        elif op == "search":
            result = record_search(tree_root, val)
        elif op == "min":
            result = record_min(tree_root)
        elif op == "max":
            result = record_max(tree_root)
        elif op == "pred":
            result = record_predecessor(tree_root, val)
        elif op == "succ":
            result = record_successor(tree_root, val)
        elif op == "rank":
            result = record_rank(tree_root, val)
        elif op == "select":
            k = int(val)
            result = record_select(tree_root, k)
        else:
            return {"error": "Bad Request", "message": "Unrecognized operation."}, 400

        return result, 200
    except Exception as e:
        return {"error": "Bad Request", "message": str(e)}, 400


def handle_traverse(payload: Optional[Dict[str, Any]]) -> tuple[Dict[str, Any], int]:
    if not isinstance(payload, dict):
        return {"error": "Bad Request", "message": "Invalid JSON body."}, 400

    order = payload.get("order")
    valid_orders = {"pre", "in", "post", "level"}
    if order not in valid_orders:
        return {
            "error": "Bad Request",
            "message": f"Invalid order '{order}'. Must be one of: {sorted(list(valid_orders))}.",
        }, 400

    try:
        tree_root = deserialize_tree(payload.get("tree"))
    except Exception as e:
        return {"error": "Bad Request", "message": f"Malformed tree structure: {str(e)}"}, 400

    if order == "pre":
        result = record_preorder(tree_root)
    elif order == "in":
        result = record_inorder(tree_root)
    elif order == "post":
        result = record_postorder(tree_root)
    elif order == "level":
        result = record_level_order(tree_root)
    else:
        return {"error": "Bad Request", "message": "Unrecognized order."}, 400

    return result, 200


def handle_properties(payload: Optional[Dict[str, Any]]) -> tuple[Dict[str, Any], int]:
    if not isinstance(payload, dict):
        return {"error": "Bad Request", "message": "Invalid JSON body."}, 400

    try:
        tree_root = deserialize_tree(payload.get("tree"))
        props = get_all_properties(tree_root)
        return {"properties": props}, 200
    except Exception as e:
        return {"error": "Bad Request", "message": f"Malformed tree structure: {str(e)}"}, 400


def handle_build(payload: Optional[Dict[str, Any]]) -> tuple[Dict[str, Any], int]:
    if not isinstance(payload, dict):
        return {"error": "Bad Request", "message": "Invalid JSON body."}, 400

    mode = payload.get("mode")
    valid_modes = {"in+pre", "in+post", "in+level", "pre+post", "bst-pre", "bst-post"}
    if mode not in valid_modes:
        return {
            "error": "Bad Request",
            "message": f"Invalid mode '{mode}'. Must be one of: {sorted(list(valid_modes))}.",
        }, 400

    raw_seq1 = payload.get("seq1")
    if raw_seq1 is None:
        return {"error": "Bad Request", "message": "'seq1' is required."}, 400

    if isinstance(raw_seq1, str):
        p1 = parse_sequence(raw_seq1)
        seq1 = p1.tokens
    elif isinstance(raw_seq1, list):
        p1 = parse_sequence(", ".join(str(x) for x in raw_seq1))
        seq1 = raw_seq1
    else:
        return {"error": "Bad Request", "message": "'seq1' must be a string or array."}, 400

    raw_seq2 = payload.get("seq2")
    two_seq_modes = {"in+pre", "in+post", "in+level", "pre+post"}
    seq2 = None
    p2 = None

    if mode in two_seq_modes:
        if raw_seq2 is None:
            return {"error": "Bad Request", "message": f"Mode '{mode}' requires 'seq2'."}, 400
        if isinstance(raw_seq2, str):
            p2 = parse_sequence(raw_seq2)
            seq2 = p2.tokens
        elif isinstance(raw_seq2, list):
            p2 = parse_sequence(", ".join(str(x) for x in raw_seq2))
            seq2 = raw_seq2
        else:
            return {"error": "Bad Request", "message": "'seq2' must be a string or array."}, 400

    max_len = max(len(seq1), len(seq2) if seq2 else 0)
    if max_len > 50:
        return {
            "error": "Bad Request",
            "message": f"Input sequence exceeds the maximum limit of 50 nodes (got {max_len}). Please limit sequences to 50 nodes for smooth visualization.",
        }, 400

    if mode in {"bst-pre", "bst-post"}:
        def _is_num(val):
            if isinstance(val, (int, float)):
                return True
            s = str(val).strip()
            if s.startswith("-"):
                s = s[1:]
            return s.isdigit()

        has_num = any(_is_num(x) for x in seq1)
        has_alpha = any(not _is_num(x) for x in seq1)
        if has_num and has_alpha:
            return {
                "error": "Bad Request",
                "message": "Mixed numbers and letters detected in BST mode. Please use all-numbers (compared numerically) or all-letters (compared alphabetically).",
            }, 400

    try:
        if mode == "in+pre":
            result = record_build_inorder_preorder(inorder=seq1, preorder=seq2)
        elif mode == "in+post":
            result = record_build_inorder_postorder(inorder=seq1, postorder=seq2)
        elif mode == "in+level":
            result = record_build_inorder_level_order(inorder=seq1, level_order=seq2)
        elif mode == "pre+post":
            result = record_build_preorder_postorder(preorder=seq1, postorder=seq2)
        elif mode == "bst-pre":
            result = record_build_bst_from_preorder(preorder=seq1)
        elif mode == "bst-post":
            result = record_build_bst_from_postorder(postorder=seq1)
        else:
            return {"error": "Bad Request", "message": "Unrecognized mode."}, 400

        result["parsed_seq1"] = p1.to_dict() if p1 else None
        result["parsed_seq2"] = p2.to_dict() if p2 else None

        return result, 200
    except (TreeBuildError, AmbiguousTreeError, ValueError) as e:
        return {"error": "Bad Request", "message": str(e)}, 400


def handle_validate_build(payload: Optional[Dict[str, Any]]) -> tuple[Dict[str, Any], int]:
    payload = payload or {}
    mode = payload.get("mode", "in+pre")
    seq1 = payload.get("seq1", "")
    seq2 = payload.get("seq2", None)

    diagnostics = validate_build_input(mode, seq1, seq2)
    return diagnostics, 200


def handle_random_build(payload: Optional[Dict[str, Any]]) -> tuple[Dict[str, Any], int]:
    payload = payload or {}
    raw_mode = payload.get("mode", "in+pre")
    mode = str(raw_mode).replace(" ", "+")
    n_str = payload.get("n", "7")
    labels = str(payload.get("labels", "letters")).lower()

    try:
        n = int(n_str)
        n = max(3, min(15, n))
    except (ValueError, TypeError):
        n = 7

    if labels not in {"letters", "numbers"}:
        labels = "letters"

    try:
        seq1, seq2 = generate_traversal_pair(mode, n, labels)
        return {
            "mode": mode,
            "labels": labels,
            "seq1": ", ".join(str(x) for x in seq1),
            "seq2": ", ".join(str(x) for x in seq2) if seq2 is not None else None,
            "tokens1": seq1,
            "tokens2": seq2,
        }, 200
    except Exception as e:
        return {"error": "Bad Request", "message": str(e)}, 400


def handle_random(payload: Optional[Dict[str, Any]]) -> tuple[Dict[str, Any], int]:
    payload = payload or {}
    tree_type = str(payload.get("type", "bst")).lower()
    n_str = payload.get("n", "7")
    labels = str(payload.get("labels", "numbers")).lower()

    if labels not in {"numbers", "letters"}:
        return {
            "error": "Bad Request",
            "message": "Parameter 'labels' must be either 'numbers' or 'letters'.",
        }, 400

    try:
        n = int(n_str)
    except (ValueError, TypeError):
        return {"error": "Bad Request", "message": "'n' must be a valid integer."}, 400

    max_n = 26 if labels == "letters" else 30
    if n < 1 or n > max_n:
        return {
            "error": "Bad Request",
            "message": f"'n' must be between 1 and {max_n} for {'alphabetic' if labels == 'letters' else 'numeric'} labels.",
        }, 400

    if tree_type == "bst":
        values = get_random_labels(n, labels)
        result = record_create_from_array(values)
        return result, 200
    elif tree_type == "binary":
        root = generate_random_binary_tree(n, label_type=labels)
        label_desc = "alphabetic" if labels == "letters" else "numeric"
        rec = StepRecorder(
            operation="random_binary",
            pseudocode=[f"random {label_desc} binary tree generated"],
        )
        rec.record_step(
            tree_root=root,
            highlight_nodes=[],
            message=f"Generated random binary tree with {n} {label_desc} nodes.",
            pseudo_line=0,
        )
        return rec.to_dict(), 200
    else:
        return {
            "error": "Bad Request",
            "message": "Parameter 'type' must be either 'bst' or 'binary'.",
        }, 400


def handle_examples(payload: Optional[Dict[str, Any]] = None) -> tuple[Dict[str, Any], int]:
    balanced_vals = [50, 25, 75, 12, 37, 62, 87]
    skewed_vals = [10, 20, 30, 40, 50]
    duplicate_vals = [50, 30, 70, 30, 50, 80, 20]
    full_tree = BinaryTree.from_level_order([1, 2, 3, 4, 5, 6, 7])

    presets = [
        {
            "id": "balanced_bst",
            "name": "Balanced BST",
            "type": "bst",
            "values": balanced_vals,
            "description": "A well-balanced BST with 7 nodes (height = 3).",
        },
        {
            "id": "skewed_bst",
            "name": "Right-Skewed BST",
            "type": "bst",
            "values": skewed_vals,
            "description": "A completely skewed BST demonstrating O(n) degeneration.",
        },
        {
            "id": "duplicate_bst",
            "name": "BST with Duplicates",
            "type": "bst",
            "values": duplicate_vals,
            "description": "A BST demonstrating frequency counts for repeated values.",
        },
        {
            "id": "full_binary_tree",
            "name": "Full & Perfect Binary Tree",
            "type": "binary",
            "tree": full_tree.root.to_dict(),
            "description": "A perfect binary tree of height 3.",
        },
    ]
    return {"examples": presets}, 200


# Map of normalized route paths to handler functions
ROUTE_HANDLERS = {
    "api/health": handle_health,
    "api/bst/create": handle_bst_create,
    "api/bst/operation": handle_bst_operation,
    "api/traverse": handle_traverse,
    "api/properties": handle_properties,
    "api/build": handle_build,
    "api/build/validate": handle_validate_build,
    "api/build/random": handle_random_build,
    "api/random": handle_random,
    "api/examples": handle_examples,
}


def handle(route: str, payload_json: str = "{}") -> str:
    """Unified API dispatcher.

    Accepts route (e.g. 'api/health', '/api/bst/create') and payload JSON string.
    Returns a JSON string conforming to:
        {"status": 200, "body": {...}} or {"status": 400, "body": {"message": "..."}}
    """
    # Parse payload JSON if provided
    params: Dict[str, Any] = {}
    if payload_json:
        if isinstance(payload_json, dict):
            params = payload_json
        elif isinstance(payload_json, str):
            payload_str = payload_json.strip()
            if payload_str:
                try:
                    parsed = json.loads(payload_str)
                    if isinstance(parsed, dict):
                        params = parsed
                    else:
                        params = {"data": parsed}
                except Exception:
                    return json.dumps({
                        "status": 400,
                        "body": {"error": "Bad Request", "message": "Invalid JSON payload."},
                    })

    # Parse route and extract query params if embedded in route string
    parsed_url = urlparse(route)
    clean_route = parsed_url.path.strip("/")
    if parsed_url.query:
        query_dict = parse_qs(parsed_url.query)
        # Flatten query list values where appropriate
        for k, v in query_dict.items():
            if k not in params:
                params[k] = v[0] if len(v) == 1 else v

    handler = ROUTE_HANDLERS.get(clean_route)
    if not handler:
        return json.dumps({
            "status": 404,
            "body": {"error": "Not Found", "message": f"Unknown route: {route}"},
        })

    try:
        body, status = handler(params)
    except Exception as exc:
        body = {"error": "Internal Error", "message": str(exc)}
        status = 500

    return json.dumps({"status": status, "body": body})
