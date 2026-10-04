"""In-process cases for veri/over_budget.py, the module over-budget.sh is a shim over."""
import importlib
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
