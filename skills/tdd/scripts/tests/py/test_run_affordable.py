"""In-process cases for veri/run_affordable.py, the module run-affordable.sh is a shim over."""
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


def test_main_runs_step_budget_then_step_cost_beside_its_scripts_and_passes_their_statuses_through(capsys, monkeypatch, run_affordable):
    scripts = pathlib.Path(run_affordable.__file__).resolve().parent.parent
    budget_sh, cost_sh = str(scripts / "step-budget.sh"), str(scripts / "step-cost.sh")
    steps = "5.25 6\n7.50 6\n9.75 6\n"

    def answer(budget, budget_status=0, cost_status=0):
        calls = []

        def fake_run(args, *rest, **kwargs):
            env = kwargs.get("env")
            calls.append((list(args), kwargs.get("cwd"), env is None or dict(env) == dict(os.environ)))
            if args[0] == budget_sh:
                status, out = budget_status, budget
            elif args[0] == cost_sh:
                status, out = cost_status, steps if cost_status == 0 else ""
            else:
                raise AssertionError("unexpected subprocess call: %r" % (args,))
            if not (kwargs.get("text") or kwargs.get("universal_newlines") or kwargs.get("encoding")):
                out = out.encode()
            if kwargs.get("check") and status:
                raise subprocess.CalledProcessError(status, args, out, "")
            return subprocess.CompletedProcess(args, status, out, "")

        def fake_popen(args, *rest, **kwargs):
            raise AssertionError("unexpected subprocess.Popen: %r" % (args,))

        monkeypatch.setattr(subprocess, "run", fake_run)
        monkeypatch.setattr(subprocess, "Popen", fake_popen)
        return calls

    both = [([budget_sh], None, True), ([cost_sh, "--steps"], None, True)]

    for budget, expected in (("12\n60\n", 0), ("99\n50\n", 1)):
        calls = answer(budget)
        code = run_affordable.main(["4"])
        out, _ = capsys.readouterr()
        assert (budget, code, out if code == 0 else "", calls) == (budget, expected, "", both)

    for budget_status, cost_status, expected, ran in (
        (2, 0, 2, both[:1]),
        (5, 0, 2, both[:1]),
        (0, 3, 3, both),
        (0, 2, 2, both),
        (0, 1, 1, both),
        (0, 5, 2, both),
    ):
        calls = answer("12\n50\n", budget_status, cost_status)
        code = run_affordable.main(["4"])
        out, _ = capsys.readouterr()
        assert ((budget_status, cost_status), code, out, calls) == ((budget_status, cost_status), expected, "", ran)
