"""In-process cases for veri/run_affordable.py, the module run-affordable.sh is a shim over."""
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
def run_affordable():
    return importlib.import_module("veri.run_affordable")


def _siblings(monkeypatch, budget, steps):
    """subprocess.run answering step-budget.sh with <budget> and step-cost.sh --steps with <steps>; returns the calls made."""
    calls = []

    def fake_run(args, *rest, **kwargs):
        calls.append(list(args))
        name = pathlib.Path(args[0]).name
        if name == "step-budget.sh":
            return subprocess.CompletedProcess(args, 0, budget, "")
        if name == "step-cost.sh" and list(args[1:]) == ["--steps"]:
            return subprocess.CompletedProcess(args, 0, steps, "")
        raise AssertionError("unexpected subprocess call: %r" % (args,))

    def fake_popen(args, *rest, **kwargs):
        raise AssertionError("unexpected subprocess.Popen: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    return calls


def test_main_refuses_a_bad_argument_with_2_and_answers_1_or_3_from_the_siblings(capsys, monkeypatch, run_affordable):
    usage = "usage: run-affordable.sh <steps-remaining> (a whole number)\n"
    calls = _siblings(monkeypatch, "12\n50\n", "5.25 6\n7.50 6\n9.75 6\n")
    for argv, shown in (([], ""), ([""], ""), (["two"], "two")):
        code = run_affordable.main(argv)
        out, err = capsys.readouterr()
        assert (argv, code, out, err) == (
            argv, 2, "",
            "run-affordable.sh: <steps-remaining> is not a whole number: '%s'\n" % shown + usage,
        )
    assert calls == []

    code = run_affordable.main(["4"])
    out, _ = capsys.readouterr()
    assert (code, out) == (1, "spent 22.50, steps remaining 4, median 7.50, projection 52.50\n")

    _siblings(monkeypatch, "12\n50\n", "100.00 2\n100.00 2\n")
    code = run_affordable.main(["4"])
    out, _ = capsys.readouterr()
    assert (code, out) == (3, "")
