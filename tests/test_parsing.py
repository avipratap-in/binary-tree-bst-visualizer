"""Comprehensive tests for lenient sequence parsing in core/parsing.py."""
import pytest
from bt_visualizer.core.parsing import parse_sequence


def test_clean_comma_separated():
    res = parse_sequence("D, B, E, A, C")
    assert res.tokens == ["D", "B", "E", "A", "C"]
    assert res.warnings == []


def test_messy_separators():
    res = parse_sequence(" D,, B  E ;A|C, \n\t")
    assert res.tokens == ["D", "B", "E", "A", "C"]


def test_enclosing_brackets_and_quotes():
    res1 = parse_sequence("[D, B, E, A, C]")
    assert res1.tokens == ["D", "B", "E", "A", "C"]

    res2 = parse_sequence("( 'D', \"B\", 'E' )")
    assert res2.tokens == ["D", "B", "E"]

    res3 = parse_sequence("{10; 20; 30}")
    assert res3.tokens == [10, 20, 30]


def test_contiguous_letters_without_separators():
    res = parse_sequence("DBEAC")
    assert res.tokens == ["D", "B", "E", "A", "C"]
    assert any("split contiguous letters" in note.lower() for note in res.notes)


def test_pure_digits_not_split():
    res = parse_sequence("12345")
    # Must NOT split into [1, 2, 3, 4, 5]
    assert res.tokens == [12345]
    assert any("single numeric token" in note.lower() for note in res.notes)


def test_empty_and_whitespace_only():
    res_none = parse_sequence(None)
    assert res_none.tokens == []

    res_empty = parse_sequence("")
    assert res_empty.tokens == []

    res_spaces = parse_sequence("   \t  \n ")
    assert res_spaces.tokens == []


def test_single_token():
    res_str = parse_sequence("A")
    assert res_str.tokens == ["A"]

    res_num = parse_sequence("42")
    assert res_num.tokens == [42]


def test_unicode_letters():
    res = parse_sequence("α, β, γ, δ")
    assert res.tokens == ["α", "β", "γ", "δ"]


def test_duplicate_tokens():
    res = parse_sequence("A, B, A, C")
    assert res.tokens == ["A", "B", "A", "C"]


def test_numeric_tokens_parsed_as_int():
    res = parse_sequence("10, 20, -5, 100")
    assert res.tokens == [10, 20, -5, 100]
    assert all(isinstance(t, int) for t in res.tokens)


def test_mixed_tokens_flagged_with_warning():
    res = parse_sequence("10, B, 30")
    assert res.tokens == ["10", "B", "30"]
    assert len(res.warnings) > 0
