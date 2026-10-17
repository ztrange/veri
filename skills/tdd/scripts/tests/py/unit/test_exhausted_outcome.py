"""In-process cases for veri/exhausted_outcome.py, the module exhausted-outcome.sh is a shim over."""
import importlib
import io
import re
import sys

import pytest


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


def test_main_prints_the_last_needs_user_and_every_later_line_returns_3_on_empty_stdin_drops_nul_and_ignores_arguments(monkeypatch, capsys, exhausted_outcome):
    results = {}
    for text, argv in (
        ("NEEDS_USER: q\n\n\n", []),
        ("NEEDS_USER: a\nx\nNEEDS_USER: q\ny\n\nz", []),
        ("NEEDS_USER:", []),
        ("", []),
        ("SPLIT: a\0b", []),
        ("NEEDS_USER: q", ["extra", "args"]),
    ):
        monkeypatch.setattr(sys, "stdin", io.StringIO(text))
        code = exhausted_outcome.main(argv)
        results[(text, *argv)] = (code, *capsys.readouterr())

    assert results == {
        ("NEEDS_USER: q\n\n\n",): (1, "q\n\n\n", ""),
        ("NEEDS_USER: a\nx\nNEEDS_USER: q\ny\n\nz",): (1, "q\ny\n\nz\n", ""),
        ("NEEDS_USER:",): (1, "\n", ""),
        ("",): (3, "", ""),
        ("SPLIT: a\0b",): (0, "ab\n", ""),
        ("NEEDS_USER: q", "extra", "args"): (1, "q\n", ""),
    }


def test_main_reads_stdin_as_bytes_and_keeps_the_c_locale_behaviour_whatever_the_callers_locale(monkeypatch, exhausted_outcome):
    stdin_errors = {"C": "surrogateescape", "C.UTF-8": "strict"}
    results = {}
    for locale, errors in stdin_errors.items():
        for data in (b"SPLIT: \xff", b"SPLIT:\xc2\xa0a"):
            monkeypatch.setenv("LC_ALL", locale)
            out = io.BytesIO()
            monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(data), encoding="utf-8", errors=errors))
            monkeypatch.setattr(sys, "stdout", io.TextIOWrapper(out, encoding="utf-8", errors=errors))
            try:
                code = exhausted_outcome.main([])
            except Exception as error:
                code = type(error).__name__
            sys.stdout.flush()
            results[(locale, data)] = (code, out.getvalue())

    assert results == {
        ("C", b"SPLIT: \xff"): (0, b"\xff\n"),
        ("C", b"SPLIT:\xc2\xa0a"): (0, b"\xc2\xa0a\n"),
        ("C.UTF-8", b"SPLIT: \xff"): (0, b"\xff\n"),
        ("C.UTF-8", b"SPLIT:\xc2\xa0a"): (0, b"\xc2\xa0a\n"),
    }
    doc = exhausted_outcome.__doc__
    assert re.search(r"\bC[- ]locale\b", doc) and "UTF-8" in doc, doc


def test_a_split_report_exits_0_with_its_criteria_a_needs_user_report_exits_1_with_its_answer_and_neither_exits_3_with_nothing(run_cli, exhausted_outcome):
    split_report = ("The step names four behaviours at once, so no one green could carry it.\n"
                    "SPLIT: detect-test-command.sh exits 2 on an unknown --mode value\n"
                    "SPLIT: detect-test-command.sh exits 2 when given both an issue and --all")
    user_report = ("This one is not a split: the criterion contradicts the step before it.\n"
                   "NEEDS_USER: step 2 says exit 1 and step 4 says exit 2 for the same refusal — which wins is a\n"
                   "decision this run has no authority to make.")
    neither_report = "I read the step and the rejection reason and I am not sure what to make of them."

    assert run_cli(exhausted_outcome, [], stdin=split_report) == (
        0, "detect-test-command.sh exits 2 on an unknown --mode value\n"
           "detect-test-command.sh exits 2 when given both an issue and --all\n", "")
    assert run_cli(exhausted_outcome, [], stdin=user_report) == (
        1, "step 2 says exit 1 and step 4 says exit 2 for the same refusal — which wins is a\n"
           "decision this run has no authority to make.\n", "")
    assert run_cli(exhausted_outcome, [], stdin=neither_report) == (3, "", "")


def test_extra_arguments_are_ignored_and_nothing_is_ever_written_to_stderr(run_cli, exhausted_outcome):
    assert run_cli(exhausted_outcome, ["extra", "args"], stdin="SPLIT: a") == (0, "a\n", "")
    for report in ("SPLIT: a", "NEEDS_USER: q", "neither"):
        assert run_cli(exhausted_outcome, [], stdin=report)[2] == ""
