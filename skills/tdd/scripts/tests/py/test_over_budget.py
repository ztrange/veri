"""In-process cases for veri/over_budget.py, the module over-budget.sh is a shim over."""
import importlib
import os
import pathlib
import subprocess
import sys

import pytest


@pytest.fixture
def over_budget():
    return importlib.import_module("veri.over_budget")


def _time_budget(monkeypatch, code, stdout):
    """subprocess.run answering time-budget.sh with <code> and <stdout>; returns the calls made."""
    calls = []

    def fake_run(args, *rest, **kwargs):
        calls.append(args)
        if pathlib.Path(args[0]).name != "time-budget.sh":
            raise AssertionError("unexpected subprocess call: %r" % (args,))
        return subprocess.CompletedProcess(args, code, stdout, "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    return calls


def test_main_refuses_a_missing_argument_with_2_and_answers_0_1_or_2_from_time_budget(capsys, monkeypatch, over_budget):
    calls = _time_budget(monkeypatch, 0, "10\n1.5\n")
    for argv in ([], ["unit"], ["unit", "10"], ["unit", "10", ""]):
        code = over_budget.main(argv)
        out, err = capsys.readouterr()
        assert (argv, code, out, err) == (argv, 2, "", "usage: over-budget.sh <tier> <seconds> <usual>\n")
    assert calls == []

    code = over_budget.main(["unit", "12", "100"])
    out, _ = capsys.readouterr()
    assert (code, out) == (0, "⏱ unit tier took 12 s (usual 100 s, ratio 1.5, unit budget 10 s)\n")

    code = over_budget.main(["unit", "4", "100"])
    out, _ = capsys.readouterr()
    assert (code, out) == (1, "")

    _time_budget(monkeypatch, 2, "")
    code = over_budget.main(["unit", "12", "100"])
    out, _ = capsys.readouterr()
    assert (code, out) == (2, "")


def test_main_runs_time_budget_beside_the_scripts_with_no_argument_and_reads_its_first_and_last_lines(capsys, monkeypatch, over_budget):
    monkeypatch.setenv("VERI_TIME_WARN_RATIO", "1.5")
    seen = []

    def fake_run(args, *rest, **kwargs):
        seen.append((list(args), rest, kwargs))
        if kwargs.get("env") is None:
            assert os.environ.get("VERI_TIME_WARN_RATIO") == "1.5"
        return subprocess.CompletedProcess(args, 0, "1000\n7\n1.5\n", "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    beside = pathlib.Path(over_budget.__file__).resolve().parents[1] / "time-budget.sh"

    code = over_budget.main(["all", "160", "100", "extra"])
    out, _ = capsys.readouterr()
    assert (code, out) == (0, "⏱ all tier took 160 s (usual 100 s, ratio 1.5, unit budget 1000 s)\n")

    code = over_budget.main(["unit", "12", "100", "extra"])
    out, _ = capsys.readouterr()
    assert (code, out) == (1, "")

    assert len(seen) == 2
    for args, rest, kwargs in seen:
        assert rest == ()
        assert [pathlib.Path(args[0]).resolve()] + args[1:] == [beside]
        assert kwargs.get("env") is None
        assert kwargs.get("stdout") == subprocess.PIPE or kwargs.get("capture_output")
        assert kwargs.get("stderr") is None and not kwargs.get("capture_output")


def test_main_compares_strictly_matches_the_tier_exactly_multiplies_as_doubles_and_prints_each_value_as_given(capsys, monkeypatch, over_budget):
    _time_budget(monkeypatch, 0, "10\n1.5\n")
    for argv in (["unit", "10", "100"], ["all", "150", "100"], ["Unit", "12", "100"], ["all", "0.15", "0.1"]):
        code = over_budget.main(argv)
        out, _ = capsys.readouterr()
        assert (argv, code, out) == (argv, 1, "")

    _time_budget(monkeypatch, 0, "10.0\n1.50\n")
    code = over_budget.main(["unit", "12.0", "100"])
    out, _ = capsys.readouterr()
    assert (code, out) == (0, "⏱ unit tier took 12.0 s (usual 100 s, ratio 1.50, unit budget 10.0 s)\n")


def test_main_reads_what_macos_awk_reads_as_a_number_as_a_number(capsys, monkeypatch, over_budget):
    _time_budget(monkeypatch, 0, "10\n1.5\n")
    for seconds in (" 12", "+200", ".5e3", "200.", "2e2", "inf", "0x1A"):
        code = over_budget.main(["all", seconds, "1"])
        capsys.readouterr()
        assert (seconds, code) == (seconds, 0)
    for argv in (["all", "nan", "1"], ["all", "-inf", "-1"]):
        code = over_budget.main(argv)
        capsys.readouterr()
        assert (argv, code) == (argv, 1)


def test_main_keeps_a_number_with_the_whitespace_macos_awk_skips_and_reads_a_trailing_formfeed_or_vtab_as_a_string(capsys, monkeypatch, over_budget):
    _time_budget(monkeypatch, 0, "10\n1.5\n")
    for seconds in ("\f1000", "\v1000", "\r1000", "1000 ", "1000\t", "1000\r"):
        code = over_budget.main(["all", seconds, "100"])
        capsys.readouterr()
        assert (seconds, code) == (seconds, 0)
    for seconds in ("1000\f", "1000\v"):
        code = over_budget.main(["all", seconds, "100"])
        capsys.readouterr()
        assert (seconds, code) == (seconds, 1)


def test_main_compares_seconds_awk_reads_as_a_string_as_text_against_the_budget_and_the_product_in_percent_6g(capsys, monkeypatch, over_budget):
    _time_budget(monkeypatch, 0, "10\n1.5\n")
    for argv, expected in ((["unit", "abc", "100"], 0), (["all", "160s", "100"], 0), (["all", "1000s", "100"], 1),
                           (["all", "1e", "1000"], 0), (["all", "1_000", "1000"], 0),
                           (["unit", "12x", "100"], 0), (["all", "12x", "100"], 1),
                           (["all", "1.6x", "1000001"], 0), (["all", "1.6x", "1000000"], 1),
                           (["all", "NaN", "100"], 1), (["all", "-Infinity", "-100"], 1),
                           (["all", "abc", "inf"], 1), (["all", "j", "inf"], 0),
                           (["all", "abc", "nan"], 1), (["all", "o", "nan"], 0)):
        code = over_budget.main(argv)
        capsys.readouterr()
        assert (argv, code) == (argv, expected)


def test_main_reads_a_usual_awk_reads_as_a_string_as_zero_inside_the_product(capsys, monkeypatch, over_budget):
    _time_budget(monkeypatch, 0, "10\n1.5\n")
    for argv, expected in ((["all", "160", "abc"], 0), (["all", "0", "abc"], 1)):
        code = over_budget.main(argv)
        capsys.readouterr()
        assert (argv, code) == (argv, expected)


def test_main_reads_a_dot_as_the_decimal_separator_whatever_lc_all_says(capsys, monkeypatch, over_budget):
    _time_budget(monkeypatch, 0, "10\n1.5\n")
    for locale in ("de_DE.UTF-8", "C"):
        monkeypatch.setenv("LC_ALL", locale)
        code = over_budget.main(["all", "1,6", "1"])
        out, _ = capsys.readouterr()
        assert (locale, code, out) == (locale, 1, "")


def test_main_compares_as_macos_awk_does_not_as_python_float_does(capsys, monkeypatch, over_budget):
    _time_budget(monkeypatch, 0, "10\n1.5\n")
    cases = [(["all", seconds, "1"], 0) for seconds in (" 12", "+200", ".5e3", "200.", "2e2", "inf", "0x1A")]
    cases += [(["all", "nan", "1"], 1), (["unit", "abc", "100"], 0), (["all", "160s", "100"], 0),
              (["all", "1000s", "100"], 1), (["all", "1e", "1000"], 0), (["all", "1_000", "1000"], 0),
              (["all", "160", "abc"], 0)]
    for locale in ("C", "de_DE.UTF-8"):
        monkeypatch.setenv("LC_ALL", locale)
        for argv, expected in cases + [(["all", "1,6", "1"], 1)]:
            code = over_budget.main(argv)
            capsys.readouterr()
            assert (locale, argv, code) == (locale, argv, expected)


def test_main_processes_backslash_escapes_in_every_value_as_awk_v_does(capsys, monkeypatch, over_budget):
    _time_budget(monkeypatch, 0, "10\n1.5\n")
    for argv, line in ((["x\\ny", "160", "100"], "⏱ x\ny tier took 160 s (usual 100 s, ratio 1.5, unit budget 10 s)\n"),
                       (["x\\\\y", "160", "100"], "⏱ x\\y tier took 160 s (usual 100 s, ratio 1.5, unit budget 10 s)\n"),
                       (["q\\", "160", "100"], "⏱ q\\ tier took 160 s (usual 100 s, ratio 1.5, unit budget 10 s)\n"),
                       (["unit", "12\\n", "100"], "⏱ unit tier took 12\n s (usual 100 s, ratio 1.5, unit budget 10 s)\n")):
        code = over_budget.main(argv)
        out, _ = capsys.readouterr()
        assert (argv, code, out) == (argv, 0, line)


def test_main_processes_awk_v_s_whole_escape_table_not_only_backslash_and_n(capsys, monkeypatch, over_budget):
    _time_budget(monkeypatch, 0, "10\n1.5\n")
    for tier, printed in (("x\\ty", "x\ty"), ("x\\\"y", "x\"y"), ("x\\ry", "x\ry"), ("x\\by", "x\by"),
                          ("x\\fy", "x\fy"), ("x\\vy", "x\vy"), ("x\\ay", "x\ay"), ("x\\/y", "x/y"),
                          ("x\\101y", "xAy"), ("x\\7y", "x\ay"), ("x\\0123", "x\n3")):
        code = over_budget.main([tier, "160", "100"])
        out, _ = capsys.readouterr()
        assert (tier, code, out) == (tier, 0, "⏱ %s tier took 160 s (usual 100 s, ratio 1.5, unit budget 10 s)\n" % printed)


def test_main_with_stdout_closed_returns_2_with_one_line_on_stderr_when_over_and_1_with_nothing_when_not(capsys, monkeypatch, over_budget):
    _time_budget(monkeypatch, 0, "10\n1.5\n")
    monkeypatch.setattr(sys, "stdout", None)

    code = over_budget.main(["unit", "12", "100"])
    err = capsys.readouterr().err
    assert (code, err.count("\n"), err.endswith("\n"), err.strip() != "") == (2, 1, True, True)

    code = over_budget.main(["unit", "4", "100"])
    err = capsys.readouterr().err
    assert (code, err) == (1, "")

    def failing_run(args, *rest, **kwargs):
        raise OSError("time-budget.sh could not start")

    monkeypatch.setattr(subprocess, "run", failing_run)
    with pytest.raises(OSError):
        over_budget.main(["unit", "12", "100"])
