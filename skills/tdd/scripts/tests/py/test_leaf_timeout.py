"""In-process cases for veri/leaf_timeout.py, the module leaf-timeout.sh is a shim over."""
import importlib

import pytest

USAGE = "usage: leaf-timeout.sh <baseline-seconds> [refactor | --full <full-seconds>]"


@pytest.fixture
def leaf_timeout(monkeypatch):
    monkeypatch.delenv("VERI_ISSUE", raising=False)
    return importlib.import_module("veri.leaf_timeout")


def test_main_refuses_a_baseline_of_ten_with_its_diagnostic_and_usage_and_returns_2(monkeypatch, capsys, leaf_timeout):
    monkeypatch.delenv("VERI_TIMEOUT", raising=False)
    code = leaf_timeout.main(["ten"])
    out, err = capsys.readouterr()
    assert (code, out, err) == (
        2, "", "leaf-timeout: <baseline-seconds> must be a whole number >= 0: ten\n" + USAGE + "\n")


def test_main_with_veri_timeout_unset_derives_max_900_six_times_the_baseline_and_refuses_a_malformed_one(monkeypatch, capsys, leaf_timeout):
    monkeypatch.delenv("VERI_TIMEOUT", raising=False)
    seen = []
    for argv in (["0"], ["5"], ["150"], ["151"], ["200"], ["abc"], ["-1"], ["1.5"], []):
        code = leaf_timeout.main(argv)
        out, err = capsys.readouterr()
        seen.append((argv, code, out, err))
    refusal = "leaf-timeout: <baseline-seconds> must be a whole number >= 0: {}\n" + USAGE + "\n"
    assert seen == [
        (["0"], 0, "900\n", ""),
        (["5"], 0, "900\n", ""),
        (["150"], 0, "900\n", ""),
        (["151"], 0, "906\n", ""),
        (["200"], 0, "1200\n", ""),
        (["abc"], 2, "", refusal.format("abc")),
        (["-1"], 2, "", refusal.format("-1")),
        (["1.5"], 2, "", refusal.format("1.5")),
        ([], 2, "", refusal.format("")),
    ]


def test_main_prints_an_explicit_veri_timeout_as_given_whatever_the_baseline_and_refuses_one_not_a_whole_number_of_at_least_1(monkeypatch, capsys, leaf_timeout):
    seen = []
    for timeout, baseline in (("900", "200"), ("1800", "5"), ("1", "200"), ("0", "200"), ("abc", "200"), ("-1", "200"), ("1.5", "200")):
        monkeypatch.setenv("VERI_TIMEOUT", timeout)
        code = leaf_timeout.main([baseline])
        out, err = capsys.readouterr()
        seen.append((timeout, baseline, code, out, err))
    refusal = "leaf-timeout: VERI_TIMEOUT must be a whole number >= 1: {}\n"
    assert seen == [
        ("900", "200", 0, "900\n", ""),
        ("1800", "5", 0, "1800\n", ""),
        ("1", "200", 0, "1\n", ""),
        ("0", "200", 2, "", refusal.format("0")),
        ("abc", "200", 2, "", refusal.format("abc")),
        ("-1", "200", 2, "", refusal.format("-1")),
        ("1.5", "200", 2, "", refusal.format("1.5")),
    ]


def test_main_with_refactor_multiplies_the_derived_timeout_by_max_1_veri_refactor_budget_and_prints_an_explicit_veri_timeout_unmultiplied(monkeypatch, capsys, leaf_timeout):
    seen = []
    for timeout, budget, baseline in (
            (None, "5", "200"), (None, "1", "200"), (None, "0", "200"), (None, "3", "5"), (None, None, "5"),
            ("900", "5", "200"), ("1800", "5", "200")):
        for name, value in (("VERI_TIMEOUT", timeout), ("VERI_REFACTOR_BUDGET", budget)):
            if value is None:
                monkeypatch.delenv(name, raising=False)
            else:
                monkeypatch.setenv(name, value)
        code = leaf_timeout.main([baseline, "refactor"])
        out, err = capsys.readouterr()
        seen.append((timeout, budget, baseline, code, out, err))
    assert seen == [
        (None, "5", "200", 0, "6000\n", ""),
        (None, "1", "200", 0, "1200\n", ""),
        (None, "0", "200", 0, "1200\n", ""),
        (None, "3", "5", 0, "2700\n", ""),
        (None, None, "5", 0, "4500\n", ""),
        ("900", "5", "200", 0, "900\n", ""),
        ("1800", "5", "200", 0, "1800\n", ""),
    ]


def test_main_with_full_derives_from_the_full_tier_prints_an_explicit_veri_timeout_as_given_and_refuses_a_malformed_full_tier(monkeypatch, capsys, leaf_timeout):
    seen = []
    for timeout, argv in (
            (None, ["5", "--full", "600"]),
            ("900", ["5", "--full", "600"]), ("7200", ["5", "--full", "20"]), ("1", ["150", "--full", "151"]),
            (None, ["5", "--full", "abc"]), (None, ["5", "--full", "-1"]), (None, ["5", "--full", "1.5"]),
            (None, ["5", "--full"])):
        if timeout is None:
            monkeypatch.delenv("VERI_TIMEOUT", raising=False)
        else:
            monkeypatch.setenv("VERI_TIMEOUT", timeout)
        code = leaf_timeout.main(argv)
        out, err = capsys.readouterr()
        seen.append((timeout, argv, code, out, err))
    refusal = "leaf-timeout: <full-seconds> must be a whole number >= 0: {}\n" + USAGE + "\n"
    assert seen == [
        (None, ["5", "--full", "600"], 0, "3600\n", ""),
        ("900", ["5", "--full", "600"], 0, "900\n", ""),
        ("7200", ["5", "--full", "20"], 0, "7200\n", ""),
        ("1", ["150", "--full", "151"], 0, "1\n", ""),
        (None, ["5", "--full", "abc"], 2, "", refusal.format("abc")),
        (None, ["5", "--full", "-1"], 2, "", refusal.format("-1")),
        (None, ["5", "--full", "1.5"], 2, "", refusal.format("1.5")),
        (None, ["5", "--full"], 2, "", refusal.format("")),
    ]


def test_main_keeps_leaf_timeout_sh_argument_and_environment_quirks(monkeypatch, capsys, leaf_timeout):
    seen = []
    for timeout, budget, argv in (
            ("007", None, ["abc"]), ("007", None, []), ("", None, ["200"]), ("abc", None, []),
            (None, None, ["5", "--full"]), (None, None, ["200", "foo"]), (None, "5", ["200", "refactor", "x"]),
            (None, "", ["200", "refactor"]), (None, "-3", ["200", "refactor"])):
        for name, value in (("VERI_TIMEOUT", timeout), ("VERI_REFACTOR_BUDGET", budget)):
            if value is None:
                monkeypatch.delenv(name, raising=False)
            else:
                monkeypatch.setenv(name, value)
        code = leaf_timeout.main(argv)
        out, err = capsys.readouterr()
        seen.append((timeout, budget, argv, code, out, err))
    assert seen == [
        ("007", None, ["abc"], 0, "7\n", ""),
        ("007", None, [], 0, "7\n", ""),
        ("", None, ["200"], 0, "1200\n", ""),
        ("abc", None, [], 2, "", "leaf-timeout: VERI_TIMEOUT must be a whole number >= 1: abc\n"),
        (None, None, ["5", "--full"], 2, "", "leaf-timeout: <full-seconds> must be a whole number >= 0: \n" + USAGE + "\n"),
        (None, None, ["200", "foo"], 0, "1200\n", ""),
        (None, "5", ["200", "refactor", "x"], 0, "6000\n", ""),
        (None, "", ["200", "refactor"], 0, "6000\n", ""),
        (None, "-3", ["200", "refactor"], 2, "", "leaf-timeout: VERI_REFACTOR_BUDGET must be a whole number >= 0: -3\n"),
    ]


def test_main_reproduces_leaf_timeout_sh_bash_arithmetic_in_stdout_and_return_code_reading_leading_zeros_as_decimal_issue_776(monkeypatch, capsys, leaf_timeout):
    monkeypatch.delenv("VERI_TIMEOUT", raising=False)
    seen = []
    for budget, argv in (
            (None, ["0200"]), (None, ["08"]), (None, ["5", "--full", "0200"]), ("abc", ["200", "refactor"]),
            ("010", ["200", "refactor"]),
            (None, ["1537228672809129302"]), (None, ["768614336404564651", "refactor"]),
            (None, ["9223372036854775808"])):
        if budget is None:
            monkeypatch.delenv("VERI_REFACTOR_BUDGET", raising=False)
        else:
            monkeypatch.setenv("VERI_REFACTOR_BUDGET", budget)
        code = leaf_timeout.main(argv)
        out, _ = capsys.readouterr()
        seen.append((budget, argv, code, out))
    assert seen == [
        (None, ["0200"], 0, "1200\n"),
        (None, ["08"], 0, "900\n"),
        (None, ["5", "--full", "0200"], 0, "1200\n"),
        ("abc", ["200", "refactor"], 2, ""),
        ("010", ["200", "refactor"], 0, "12000\n"),
        (None, ["1537228672809129302"], 0, "9223372036854775812\n"),
        (None, ["768614336404564651", "refactor"], 0, "23058430092136939530\n"),
        (None, ["9223372036854775808"], 0, "55340232221128654848\n"),
    ]


def test_main_with_refactor_refuses_a_veri_refactor_budget_not_a_non_negative_whole_number_with_2_naming_it_issue_776(monkeypatch, capsys, leaf_timeout):
    monkeypatch.delenv("VERI_TIMEOUT", raising=False)
    seen = []
    for budget in ("abc", "-3", "1.5"):
        monkeypatch.setenv("VERI_REFACTOR_BUDGET", budget)
        code = leaf_timeout.main(["200", "refactor"])
        out, err = capsys.readouterr()
        seen.append((budget, code, out, "VERI_REFACTOR_BUDGET" in err))
    assert seen == [
        ("abc", 2, "", True),
        ("-3", 2, "", True),
        ("1.5", 2, "", True),
    ]


def test_main_prints_a_veri_timeout_given_with_leading_zeros_as_its_decimal_value_issue_776(monkeypatch, capsys, leaf_timeout):
    monkeypatch.setenv("VERI_TIMEOUT", "010")
    code = leaf_timeout.main(["200"])
    out, err = capsys.readouterr()
    assert (code, out, err) == (0, "10\n", "")
