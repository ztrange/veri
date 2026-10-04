"""In-process cases for veri/exhausted_outcome.py, the module exhausted-outcome.sh is a shim over."""
import importlib
import io
import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


@pytest.fixture
def exhausted_outcome():
    return importlib.import_module("veri.exhausted_outcome")


def test_main_returns_0_for_a_split_1_for_needs_user_and_3_for_neither_never_2(monkeypatch, capsys, exhausted_outcome):
    results = {}
    for text in ("SPLIT: a", "NEEDS_USER: q", "neither"):
        monkeypatch.setattr(sys, "stdin", io.StringIO(text))
        code = exhausted_outcome.main([])
        results[text] = (code, *capsys.readouterr())

    assert results == {
        "SPLIT: a": (0, "a\n", ""),
        "NEEDS_USER: q": (1, "q\n", ""),
        "neither": (3, "", ""),
    }
    assert all(code in (0, 1, 3) for code, _, _ in results.values())


def test_main_reads_markers_at_column_0_case_sensitively_strips_leading_whitespace_only_and_any_split_wins(monkeypatch, capsys, exhausted_outcome):
    results = {}
    for text in (
        " SPLIT: a",
        "split: a",
        "SPLIT:\t  a  ",
        "SPLIT: a\r",
        "SPLIT:\r",
        "SPLIT: x\nSPLIT: x\nSPLIT:\nSPLIT: y",
        "NEEDS_USER: q\nSPLIT: a\nNEEDS_USER: r",
    ):
        monkeypatch.setattr(sys, "stdin", io.StringIO(text))
        code = exhausted_outcome.main([])
        results[text] = (code, *capsys.readouterr())

    assert results == {
        " SPLIT: a": (3, "", ""),
        "split: a": (3, "", ""),
        "SPLIT:\t  a  ": (0, "a  \n", ""),
        "SPLIT: a\r": (0, "a\r\n", ""),
        "SPLIT:\r": (0, "\n", ""),
        "SPLIT: x\nSPLIT: x\nSPLIT:\nSPLIT: y": (0, "x\nx\n\ny\n", ""),
        "NEEDS_USER: q\nSPLIT: a\nNEEDS_USER: r": (0, "a\n", ""),
    }
