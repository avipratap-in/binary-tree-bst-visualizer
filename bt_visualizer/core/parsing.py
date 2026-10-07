"""Lenient sequence parsing module.

Extracts tokens from raw user inputs with support for messy separators,
bracket stripping, contiguous letter splitting, and unicode characters.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, List, Optional


@dataclass
class ParsedSequence:
    """Represents the parsed outcome of a raw traversal sequence string.

    Attributes:
        tokens: The cleaned list of tokens (int or str).
        raw: The original raw string input.
        warnings: List of warning messages.
        notes: List of informational notes (e.g. separator interpretations).
    """
    tokens: List[Any] = field(default_factory=list)
    raw: str = ""
    warnings: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "tokens": self.tokens,
            "raw": self.raw,
            "warnings": self.warnings,
            "notes": self.notes,
            "formatted": ", ".join(str(t) for t in self.tokens),
        }


def parse_sequence(raw: Optional[str]) -> ParsedSequence:
    """Parse a raw sequence string into normalized tokens.

    Rules:
    - Messy separators allowed: commas, spaces, tabs, semicolons, pipes, newlines.
    - Surrounding brackets [..], (..), {..} and quotes are stripped.
    - If delimiterless and purely letters (e.g. "DBEAC"), split into individual characters.
    - Pure digit strings like "12345" are NOT split (treated as single token with a hint).
    - If all tokens are integers, converts them to int for numeric ordering.
    """
    if raw is None:
        return ParsedSequence(tokens=[], raw="", notes=["Empty input sequence."])

    raw_str = str(raw).strip()
    if not raw_str:
        return ParsedSequence(tokens=[], raw=raw_str, notes=["Empty input sequence."])

    cleaned = raw_str
    notes: List[str] = []
    warnings: List[str] = []

    # Strip surrounding brackets/parentheses
    if (cleaned.startswith("[") and cleaned.endswith("]")) or \
       (cleaned.startswith("(") and cleaned.endswith(")")) or \
       (cleaned.startswith("{") and cleaned.endswith("}")):
        cleaned = cleaned[1:-1].strip()

    # Check for presence of common delimiters
    has_delimiters = bool(re.search(r"[,;\s\|\n\t]", cleaned))

    # Special case: Contiguous string without delimiters
    if not has_delimiters and len(cleaned) > 1:
        if cleaned.isalpha():
            # e.g. "DBEAC" -> ['D', 'B', 'E', 'A', 'C']
            tokens_str = list(cleaned)
            notes.append("No separators detected: automatically split contiguous letters into individual characters.")
            return ParsedSequence(tokens=tokens_str, raw=raw_str, warnings=warnings, notes=notes)
        elif cleaned.isdigit():
            # e.g. "12345" -> single token, do NOT split
            notes.append("Single numeric token detected. If multiple values were intended, separate them with commas or spaces.")
            return ParsedSequence(tokens=[int(cleaned)], raw=raw_str, warnings=warnings, notes=notes)

    # Split using any mix of delimiters: comma, space, tab, semicolon, pipe, newline
    raw_pieces = re.split(r"[,;\s\|\n\t]+", cleaned)
    tokens_str: List[str] = []

    for piece in raw_pieces:
        p = piece.strip()
        if not p:
            continue
        # Strip surrounding quotes from individual token: e.g. 'A' or "A"
        if (p.startswith("'") and p.endswith("'")) or (p.startswith('"') and p.endswith('"')):
            p = p[1:-1].strip()
        if p:
            tokens_str.append(p)

    if not tokens_str:
        return ParsedSequence(tokens=[], raw=raw_str, notes=["No valid tokens found."])

    # Type normalization: Check if all tokens parse cleanly as integers
    all_ints = True
    parsed_ints: List[int] = []
    has_any_int = False
    has_any_str = False

    for t in tokens_str:
        if re.match(r"^-?\d+$", t):
            has_any_int = True
            parsed_ints.append(int(t))
        else:
            all_ints = False
            has_any_str = True

    if all_ints:
        final_tokens = parsed_ints
    else:
        # Keep as strings for consistent comparison
        final_tokens = tokens_str
        if has_any_int and has_any_str:
            warnings.append(
                "Mixed numeric and alphabetical tokens detected. Values will be treated as strings."
            )

    return ParsedSequence(tokens=final_tokens, raw=raw_str, warnings=warnings, notes=notes)
