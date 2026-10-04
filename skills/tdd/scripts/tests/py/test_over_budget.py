"""In-process cases for veri/over_budget.py, the module over-budget.sh is a shim over."""
import importlib
import os
import pathlib
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


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
