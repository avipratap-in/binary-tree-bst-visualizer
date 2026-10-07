"""Validation and diagnostic engine for tree reconstruction inputs.

Analyzes raw user sequences and produces structured diagnostics, element
set diffs, duplicate alerts, ambiguity notices, and one-click corrective suggestions.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Set
from bt_visualizer.core.builders import (
    AmbiguousTreeError,
    TreeBuildError,
    build_bst_from_postorder,
    build_bst_from_preorder,
    build_from_inorder_level_order,
    build_from_inorder_postorder,
    build_from_inorder_preorder,
    build_from_preorder_postorder,
)
from bt_visualizer.core.parsing import ParsedSequence, parse_sequence
from bt_visualizer.core.traversals import (
    inorder_recursive,
    postorder_recursive,
    preorder_recursive,
)


def _find_duplicates(tokens: List[Any]) -> List[Any]:
    seen = set()
    dups = []
    for t in tokens:
        if t in seen and t not in dups:
            dups.append(t)
        seen.add(t)
    return dups


def _suggest_deduplication(tokens: List[Any]) -> str:
    counts: Dict[Any, int] = {}
    deduped = []
    for t in tokens:
        counts[t] = counts.get(t, 0) + 1
        if counts[t] == 1:
            deduped.append(str(t))
        else:
            deduped.append(f"{t}{counts[t]}")
    return ", ".join(deduped)


def validate_build_input(
    mode: str,
    raw_seq1: Optional[str],
    raw_seq2: Optional[str] = None,
) -> Dict[str, Any]:
    """Validate reconstruction inputs and generate helpful corrective suggestions."""
    p1 = parse_sequence(raw_seq1)
    tokens1 = p1.tokens

    two_seq_modes = {"in+pre", "in+post", "in+level", "pre+post"}
    p2 = parse_sequence(raw_seq2) if mode in two_seq_modes else None
    tokens2 = p2.tokens if p2 else None

    diagnostics: Dict[str, Any] = {
        "valid": False,
        "status": "neutral",  # neutral | success | warning | error
        "mode": mode,
        "seq1": p1.to_dict(),
        "seq2": p2.to_dict() if p2 else None,
        "message": "",
        "field_errors": {},
        "suggestions": [],
    }

    # 1. Empty checks
    if not tokens1:
        diagnostics["status"] = "neutral"
        diagnostics["message"] = "Enter the primary traversal sequence above."
        return diagnostics

    if mode in two_seq_modes and not tokens2:
        diagnostics["status"] = "neutral"
        diagnostics["message"] = "Enter the secondary traversal sequence."
        return diagnostics

    # 1b. Maximum node limit (50 nodes)
    count = max(len(tokens1), len(tokens2) if tokens2 else 0)
    if count > 50:
        diagnostics["status"] = "error"
        diagnostics["message"] = (
            f"Input sequence exceeds the maximum limit of 50 nodes (got {count}). "
            f"Please limit to 50 nodes for smooth visualization."
        )
        return diagnostics

    # 2. Check duplicates for general binary tree modes
    if mode in two_seq_modes:
        dups1 = _find_duplicates(tokens1)
        dups2 = _find_duplicates(tokens2) if tokens2 else []

        if dups1 or dups2:
            diagnostics["status"] = "error"
            dup_items = list(set(dups1 + dups2))
            diagnostics["message"] = (
                f"Duplicate value(s) {dup_items} detected. Tree reconstruction requires unique node labels."
            )
            if dups1:
                diagnostics["suggestions"].append({
                    "type": "replace",
                    "field": "seq1",
                    "label": f"Rename duplicates in Seq 1",
                    "value": _suggest_deduplication(tokens1),
                })
            if dups2:
                diagnostics["suggestions"].append({
                    "type": "replace",
                    "field": "seq2",
                    "label": f"Rename duplicates in Seq 2",
                    "value": _suggest_deduplication(tokens2),
                })
            return diagnostics

    # 3. Check element sets & lengths for 2-sequence modes
    if mode in two_seq_modes and tokens2 is not None:
        if len(tokens1) != len(tokens2):
            diagnostics["status"] = "error"
            diagnostics["message"] = (
                f"Length mismatch: Sequence 1 has {len(tokens1)} items, while Sequence 2 has {len(tokens2)} items."
            )
            return diagnostics

        set1 = set(tokens1)
        set2 = set(tokens2)
        if set1 != set2:
            diff1 = set1 - set2
            diff2 = set2 - set1
            diagnostics["status"] = "error"
            msg_parts = []
            if diff1:
                msg_parts.append(f"Missing in Sequence 2: {sorted(list(diff1), key=str)}")
            if diff2:
                msg_parts.append(f"Missing in Sequence 1: {sorted(list(diff2), key=str)}")
            diagnostics["message"] = "Inconsistent sequences: " + "; ".join(msg_parts)
            return diagnostics

    # 4. BST mode checks: ensure consistent data types
    if mode in {"bst-pre", "bst-post"}:
        def _is_num(val):
            if isinstance(val, (int, float)):
                return True
            s = str(val).strip()
            if s.startswith("-"):
                s = s[1:]
            return s.isdigit()

        has_num = any(_is_num(x) for x in tokens1)
        has_alpha = any(not _is_num(x) for x in tokens1)

        if has_num and has_alpha:
            diagnostics["status"] = "error"
            diagnostics["message"] = (
                "Mixed numbers and letters detected. BST requires all-numbers (numeric order) "
                "or all-letters (alphabetical order)."
            )
            return diagnostics

        dups = _find_duplicates(tokens1)
        if dups:
            diagnostics["status"] = "error"
            diagnostics["message"] = f"Duplicate value(s) {dups} detected in BST traversal."
            return diagnostics

        # Try building BST
        try:
            if mode == "bst-pre":
                build_bst_from_preorder(tokens1)
            else:
                build_bst_from_postorder(tokens1)
            diagnostics["valid"] = True
            diagnostics["status"] = "success"
            diagnostics["message"] = f"Valid BST traversal ({len(tokens1)} nodes)."
            return diagnostics
        except Exception as e:
            diagnostics["status"] = "error"
            diagnostics["message"] = str(e)
            return diagnostics

    # 5. Try target mode reconstruction
    try:
        if mode == "in+pre":
            build_from_inorder_preorder(tokens1, tokens2)
        elif mode == "in+post":
            build_from_inorder_postorder(tokens1, tokens2)
        elif mode == "in+level":
            build_from_inorder_level_order(tokens1, tokens2)
        elif mode == "pre+post":
            build_from_preorder_postorder(tokens1, tokens2)

        diagnostics["valid"] = True
        diagnostics["status"] = "success"
        diagnostics["message"] = f"Valid traversal pair ({len(tokens1)} nodes). Ready to build!"
        return diagnostics

    except AmbiguousTreeError as e:
        diagnostics["status"] = "warning"
        diagnostics["message"] = str(e)
        return diagnostics

    except TreeBuildError as e:
        # Direct build failed. Check for intelligent corrective suggestions!
        diagnostics["status"] = "error"
        diagnostics["message"] = str(e)

        # 5a. Check if fields were swapped:
        try:
            if mode == "in+pre":
                build_from_inorder_preorder(tokens2, tokens1)
            elif mode == "in+post":
                build_from_inorder_postorder(tokens2, tokens1)
            elif mode == "in+level":
                build_from_inorder_level_order(tokens2, tokens1)
            elif mode == "pre+post":
                build_from_preorder_postorder(tokens2, tokens1)

            # Swapping worked!
            diagnostics["suggestions"].append({
                "type": "swap_fields",
                "label": "Swap Sequence 1 and Sequence 2",
                "action": "swap",
            })
            diagnostics["message"] += " (The two sequences appear to be swapped)."
            return diagnostics
        except Exception:
            pass

        # 5b. Check if the pair matches another mode:
        alt_modes = [
            ("in+pre", "Inorder + Preorder", build_from_inorder_preorder),
            ("in+post", "Inorder + Postorder", build_from_inorder_postorder),
            ("in+level", "Inorder + Level Order", build_from_inorder_level_order),
            ("pre+post", "Preorder + Postorder", build_from_preorder_postorder),
        ]

        for alt_key, alt_label, alt_fn in alt_modes:
            if alt_key != mode:
                try:
                    alt_fn(tokens1, tokens2)
                    diagnostics["suggestions"].append({
                        "type": "switch_mode",
                        "label": f"Switch mode to {alt_label}",
                        "mode": alt_key,
                    })
                    break
                except Exception:
                    pass

        # 5c. Offer corrected valid partner sequences
        partner_suggestions = _generate_partner_suggestions(mode, tokens1, tokens2)
        diagnostics["suggestions"].extend(partner_suggestions)

        return diagnostics


def _tree_from_inorder(in_seq: List[Any]) -> Optional[TreeNode]:
    if not in_seq:
        return None
    mid = len(in_seq) // 2
    root = TreeNode(in_seq[mid])
    root.left = _tree_from_inorder(in_seq[:mid])
    root.right = _tree_from_inorder(in_seq[mid + 1 :])
    return root


def _tree_from_preorder(pre_seq: List[Any]) -> Optional[TreeNode]:
    if not pre_seq:
        return None
    root = TreeNode(pre_seq[0])
    rem = pre_seq[1:]
    if rem:
        mid = (len(rem) + 1) // 2
        root.left = _tree_from_preorder(rem[:mid])
        root.right = _tree_from_preorder(rem[mid:])
    return root


def _tree_from_postorder(post_seq: List[Any]) -> Optional[TreeNode]:
    if not post_seq:
        return None
    root = TreeNode(post_seq[-1])
    rem = post_seq[:-1]
    if rem:
        mid = len(rem) // 2
        root.left = _tree_from_postorder(rem[:mid])
        root.right = _tree_from_postorder(rem[mid:])
    return root


def _tree_from_level_order(lvl: List[Any]) -> Optional[TreeNode]:
    if not lvl:
        return None
    root = TreeNode(lvl[0])
    queue = [root]
    idx = 1
    while queue and idx < len(lvl):
        curr = queue.pop(0)
        if idx < len(lvl):
            curr.left = TreeNode(lvl[idx])
            queue.append(curr.left)
            idx += 1
        if idx < len(lvl):
            curr.right = TreeNode(lvl[idx])
            queue.append(curr.right)
            idx += 1
    return root


def _generate_partner_suggestions(
    mode: str, tokens1: List[Any], tokens2: List[Any]
) -> List[Dict[str, Any]]:
    from bt_visualizer.core.traversals import (
        inorder_recursive,
        level_order,
        postorder_recursive,
        preorder_recursive,
    )

    suggestions: List[Dict[str, Any]] = []
    try:
        if mode == "in+pre":
            t1 = _tree_from_inorder(tokens1)
            if t1:
                valid_pre = ", ".join(str(x) for x in preorder_recursive(t1))
                suggestions.append({
                    "type": "replace",
                    "field": "seq2",
                    "label": f"Preorder: {valid_pre}",
                    "value": valid_pre,
                })
            t2 = _tree_from_preorder(tokens2)
            if t2:
                valid_in = ", ".join(str(x) for x in inorder_recursive(t2))
                suggestions.append({
                    "type": "replace",
                    "field": "seq1",
                    "label": f"Inorder: {valid_in}",
                    "value": valid_in,
                })
        elif mode == "in+post":
            t1 = _tree_from_inorder(tokens1)
            if t1:
                valid_post = ", ".join(str(x) for x in postorder_recursive(t1))
                suggestions.append({
                    "type": "replace",
                    "field": "seq2",
                    "label": f"Postorder: {valid_post}",
                    "value": valid_post,
                })
            t2 = _tree_from_postorder(tokens2)
            if t2:
                valid_in = ", ".join(str(x) for x in inorder_recursive(t2))
                suggestions.append({
                    "type": "replace",
                    "field": "seq1",
                    "label": f"Inorder: {valid_in}",
                    "value": valid_in,
                })
        elif mode == "in+level":
            t1 = _tree_from_inorder(tokens1)
            if t1:
                valid_lvl = ", ".join(str(x) for x in level_order(t1))
                suggestions.append({
                    "type": "replace",
                    "field": "seq2",
                    "label": f"Level-order: {valid_lvl}",
                    "value": valid_lvl,
                })
            t2 = _tree_from_level_order(tokens2)
            if t2:
                valid_in = ", ".join(str(x) for x in inorder_recursive(t2))
                suggestions.append({
                    "type": "replace",
                    "field": "seq1",
                    "label": f"Inorder: {valid_in}",
                    "value": valid_in,
                })
    except Exception:
        pass
    return suggestions

