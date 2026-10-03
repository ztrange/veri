"""In-process cases for veri/leaf_timeout.py, the module leaf-timeout.sh is a shim over."""
import importlib
import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

USAGE = "usage: leaf-timeout.sh <baseline-seconds> [refactor | --full <full-seconds>]"


@pytest.fixture
def leaf_timeout():
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
