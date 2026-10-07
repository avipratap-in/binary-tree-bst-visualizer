"""Step recorder data definitions and serialization contracts.

Schema:
{
  "operation": "<op_name>",
  "pseudocode": ["line 0", "line 1", ...],
  "steps": [
    {
      "tree": <nested structure with unique node ids, value, freq, left, right>,
      "highlight_nodes": [ids],
      "highlight_edges": [[parent_id, child_id]],
      "visited": [values collected so far, used for traversals],
      "message": "text shown in the status box",
      "pseudo_line": <index of the active pseudocode line>,
      "stats": {"n": <node count>, "h": <height>}
    }
  ]
}
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from bt_visualizer.core.binary_tree import TreeNode
from bt_visualizer.core.properties import height, size


class StepRecorder:
    """Collects animation frames during algorithm execution."""

    def __init__(self, operation: str, pseudocode: Optional[List[str]] = None) -> None:
        self.operation = operation
        self.pseudocode = pseudocode if pseudocode is not None else []
        self.steps: List[Dict[str, Any]] = []

    def record_step(
        self,
        tree_root: Optional[TreeNode],
        highlight_nodes: Optional[List[str]] = None,
        highlight_edges: Optional[List[Tuple[str, str]]] = None,
        visited: Optional[List[Any]] = None,
        message: str = "",
        pseudo_line: int = -1,
    ) -> None:
        """Capture a discrete animation frame.

        Deep clones/serializes the tree to preserve the state at this exact point in time.
        """
        tree_dict = tree_root.to_dict() if tree_root is not None else None
        h_nodes = list(highlight_nodes) if highlight_nodes is not None else []
        h_edges = [list(edge) for edge in (highlight_edges or [])]
        vis = list(visited) if visited is not None else []
        stats = {
            "n": size(tree_root),
            "h": height(tree_root),
        }

        self.steps.append({
            "tree": tree_dict,
            "highlight_nodes": h_nodes,
            "highlight_edges": h_edges,
            "visited": vis,
            "message": message,
            "pseudo_line": pseudo_line,
            "stats": stats,
        })

    def to_dict(self) -> Dict[str, Any]:
        """Convert recorded animation timeline to final JSON-serializable dictionary."""
        return {
            "operation": self.operation,
            "pseudocode": self.pseudocode,
            "steps": self.steps,
        }
