"""In-process cases for veri/time_budget.py, the module time-budget.sh is a shim over."""
import importlib
import io
import os
import sys

import pytest


@pytest.fixture(autouse=True)
def defaults(monkeypatch):
    monkeypatch.delenv("VERI_UNIT_BUDGET", raising=False)
    monkeypatch.delenv("VERI_TIME_WARN_RATIO", raising=False)


@pytest.fixture
def time_budget():
    return importlib.import_module("veri.time_budget")


def test_main_prints_the_defaults_with_or_without_an_argument_and_returns_2_on_a_non_numeric_budget(capfd, monkeypatch, time_budget):
    answers = []
    for argv in ([], ["--bogus"]):
        code = time_budget.main(argv)
        answers.append((code,) + capfd.readouterr())
    monkeypatch.setenv("VERI_UNIT_BUDGET", "ten")
    code = time_budget.main([])
    answers.append((code,) + capfd.readouterr())
    assert answers == [
        (0, "10\n1.5\n", ""),
        (0, "10\n1.5\n", ""),
        (2, "", "time-budget: VERI_UNIT_BUDGET must be a number of seconds: ten\n"),
    ]


def test_main_returns_2_on_a_non_numeric_ratio_and_names_only_the_budget_when_both_are_bad(capfd, monkeypatch, time_budget):
    answers = []
    monkeypatch.setenv("VERI_TIME_WARN_RATIO", "1,5")
    code = time_budget.main([])
    answers.append((code,) + capfd.readouterr())
    monkeypatch.setenv("VERI_UNIT_BUDGET", "ten")
    code = time_budget.main([])
    answers.append((code,) + capfd.readouterr())
    assert answers == [
        (2, "", "time-budget: VERI_TIME_WARN_RATIO must be a number: 1,5\n"),
        (2, "", "time-budget: VERI_UNIT_BUDGET must be a number of seconds: ten\n"),
    ]


def test_main_treats_an_empty_budget_as_unset_and_accepts_only_a_whole_numeric_value_as_given(capfd, monkeypatch, time_budget):
    answers = []
    monkeypatch.setenv("VERI_UNIT_BUDGET", "")
    code = time_budget.main([])
    answers.append((code,) + capfd.readouterr())
    for value in ("1.", "-1", "1,5", "2\n", "010", "01.50"):
        monkeypatch.setenv("VERI_UNIT_BUDGET", value)
        code = time_budget.main([])
        answers.append((code,) + capfd.readouterr())
    refused = "time-budget: VERI_UNIT_BUDGET must be a number of seconds: {}\n"
    assert answers == [
        (0, "10\n1.5\n", ""),
        (2, "", refused.format("1.")),
        (2, "", refused.format("-1")),
        (2, "", refused.format("1,5")),
        (2, "", refused.format("2\n")),
        (0, "010\n1.5\n", ""),
        (0, "01.50\n1.5\n", ""),
    ]


def test_main_echoes_a_non_utf8_byte_in_either_value_as_that_byte(monkeypatch, time_budget):
    def run():
        out = io.TextIOWrapper(io.BytesIO(), encoding="utf-8", errors="backslashreplace")
        err = io.TextIOWrapper(io.BytesIO(), encoding="utf-8", errors="backslashreplace")
        monkeypatch.setattr(sys, "stdout", out)
        monkeypatch.setattr(sys, "stderr", err)
        code = time_budget.main([])
        out.flush()
        err.flush()
        return code, out.buffer.getvalue(), err.buffer.getvalue()

    answers = []
    monkeypatch.setitem(os.environb, b"VERI_UNIT_BUDGET", b"\xff")
    answers.append(run())
    monkeypatch.setitem(os.environb, b"VERI_UNIT_BUDGET", b"010")
    monkeypatch.setitem(os.environb, b"VERI_TIME_WARN_RATIO", b"1\xff")
    answers.append(run())
    monkeypatch.setitem(os.environb, b"VERI_TIME_WARN_RATIO", b"01.50")
    answers.append(run())
    assert answers == [
        (2, b"", b"time-budget: VERI_UNIT_BUDGET must be a number of seconds: \xff\n"),
        (2, b"", b"time-budget: VERI_TIME_WARN_RATIO must be a number: 1\xff\n"),
        (0, b"010\n01.50\n", b""),
    ]


def test_main_raises_rather_than_returning_0_when_stdout_is_closed(monkeypatch, time_budget):
    monkeypatch.setattr(sys, "stdout", None)
    with pytest.raises(Exception):
        time_budget.main([])
