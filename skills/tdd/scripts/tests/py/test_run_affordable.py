"""In-process cases for veri/run_affordable.py, the module run-affordable.sh is a shim over."""
import importlib
import io
import os
import pathlib
import re
import subprocess
import sys

import pytest


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
        (0, 1, 2, both),
        (0, 5, 2, both),
    ):
        calls = answer("12\n50\n", budget_status, cost_status)
        code = run_affordable.main(["4"])
        out, _ = capsys.readouterr()
        assert ((budget_status, cost_status), code, out, calls) == ((budget_status, cost_status), expected, "", ran)


def test_main_reads_steps_remaining_first_refusing_all_but_whole_numbers_and_echoing_them_byte_for_byte(monkeypatch, run_affordable):
    usage = b"usage: run-affordable.sh <steps-remaining> (a whole number)\n"
    monkeypatch.setenv("VERI_RUN_BUDGET", "fifty")
    calls = _siblings(monkeypatch, "12\n40\n", "5.25 6\n7.50 6\n9.75 6\n")

    def run(argv):
        out, err = io.BytesIO(), io.BytesIO()
        monkeypatch.setattr(sys, "stdout", io.TextIOWrapper(out, encoding="utf-8", errors="backslashreplace",
                                                            write_through=True))
        monkeypatch.setattr(sys, "stderr", io.TextIOWrapper(err, encoding="utf-8", errors="backslashreplace",
                                                            write_through=True))
        code = run_affordable.main(argv)
        sys.stdout.flush()
        sys.stderr.flush()
        return (code, out.getvalue(), err.getvalue())

    bad = {" 3": b" 3", "--": b"--", "1.5": b"1.5", "-1": b"-1", "3\n": b"3\n", os.fsdecode(b"\xff"): b"\xff"}
    seen = {arg: run([arg]) for arg in bad}
    wanted = {arg: (2, b"", b"run-affordable.sh: <steps-remaining> is not a whole number: '" + shown + b"'\n" + usage)
              for arg, shown in bad.items()}
    assert (seen, calls) == (wanted, [])

    monkeypatch.delenv("VERI_RUN_BUDGET")
    seen = {"007": run(["007"]), "3 extra": run(["3", "extra"]), "3": run(["3"])}
    assert seen == {
        "007": (1, b"spent 22.50, steps remaining 7, median 7.50, projection 75.00\n", b""),
        "3 extra": (1, b"spent 22.50, steps remaining 3, median 7.50, projection 45.00\n", b""),
        "3": (1, b"spent 22.50, steps remaining 3, median 7.50, projection 45.00\n", b""),
    }


def test_main_projects_from_the_median_full_step_counting_every_step_toward_spent_and_comparing_strictly(capsys, monkeypatch, run_affordable):
    def run(remaining, ceiling, steps):
        _siblings(monkeypatch, "12\n%s\n" % ceiling, steps)
        code = run_affordable.main([remaining])
        out, err = capsys.readouterr()
        return (code, out, err)

    seen = {
        "odd": run("1", "0", "5.00 6\n1.00 6\n2.00 2\n3.00 3\n"),
        "even": run("2", "0", "3.00 6\n1.00 6\n2.00 2\n4.00 6\n2.00 6\n"),
        "pins only": run("4", "1", "100 2\n100 2\n"),
        "at the ceiling": run("0", "9", "9.00 6\n"),
        "over the ceiling": run("0", "8.98", "8.99 6\n"),
    }
    assert seen == {
        "odd": (1, "spent 11.00, steps remaining 1, median 3.00, projection 14.00\n", ""),
        "even": (1, "spent 12.00, steps remaining 2, median 2.50, projection 17.00\n", ""),
        "pins only": (3, "", ""),
        "at the ceiling": (0, "", ""),
        "over the ceiling": (1, "spent 8.99, steps remaining 0, median 8.99, projection 8.99\n", ""),
    }


def test_main_sums_in_sort_order_formats_unlocalised_wraps_the_count_and_returns_2_when_stdout_is_closed(capsys, monkeypatch, run_affordable):
    def run(remaining, ceiling, steps):
        _siblings(monkeypatch, "12\n%s\n" % ceiling, steps)
        code = run_affordable.main([remaining])
        out, err = capsys.readouterr()
        return (code, out, err)

    seen = {"sort order": run("0", "0", "62867166030098.60 6\n0.08 2\n0.69 2\n"),
            "half-cent median": run("1", "0", "1.02 6\n1.01 6\n")}
    monkeypatch.setenv("LC_ALL", "de_DE.UTF-8")
    seen["de_DE locale"] = run("1", "0", "3.00 6\n")
    monkeypatch.delenv("LC_ALL")
    seen["past 2^63"] = run("99999999999999999999", "0", "4.50 6\n")
    monkeypatch.setattr(sys, "stdout", None)
    seen["stdout closed, over"] = run("1", "0", "3.00 6\n")[0]
    seen["stdout closed, within"] = run("1", "100", "3.00 6\n")[0]
    assert seen == {
        "sort order": (1, "spent 62867166030099.38, steps remaining 0, median 62867166030098.60, "
                          "projection 62867166030099.38\n", ""),
        "half-cent median": (1, "spent 2.03, steps remaining 1, median 1.02, projection 3.05\n", ""),
        "de_DE locale": (1, "spent 3.00, steps remaining 1, median 3.00, projection 6.00\n", ""),
        "past 2^63": (1, "spent 4.50, steps remaining -9223372036854775808, median 4.50, "
                         "projection 450000000000000000000.00\n", ""),
        "stdout closed, over": 2,
        "stdout closed, within": 0,
    }


def test_main_answers_the_contract_cases_from_step_budget_and_step_cost_as_run_affordable_sh_did(capsys, monkeypatch, tmp_path, run_affordable):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".tdd").mkdir()
    monkeypatch.delenv("VERI_STEP_BUDGET", raising=False)
    state = {}

    def fake_run(args, *rest, **kwargs):
        name = pathlib.Path(args[0]).name
        if name == "step-budget.sh":
            budget = os.environ.get("VERI_RUN_BUDGET", "40")
            if not re.fullmatch(r"[0-9]+(\.[0-9]+)?", budget):
                return subprocess.CompletedProcess(args, 2, "", "")
            return subprocess.CompletedProcess(args, 0, "12\n%s\n" % budget, "")
        if name == "step-cost.sh" and list(args[1:]) == ["--steps"]:
            if not (pathlib.Path.cwd() / ".tdd" / "events.jsonl").exists():
                return subprocess.CompletedProcess(args, 2, "", "")
            return subprocess.CompletedProcess(args, 0, state["steps"], "")
        raise AssertionError("unexpected subprocess call: %r" % (args,))

    def fake_popen(args, *rest, **kwargs):
        raise AssertionError("unexpected subprocess.Popen: %r" % (args,))

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", fake_popen)

    def run(budget, argv, steps, log=True):
        state["steps"] = steps
        log_file = tmp_path / ".tdd" / "events.jsonl"
        if log:
            log_file.write_text("")
        elif log_file.exists():
            log_file.unlink()
        monkeypatch.setenv("VERI_RUN_BUDGET", budget)
        code = run_affordable.main(argv)
        out, _ = capsys.readouterr()
        return (code, out)

    three_full = "1.50 6\n2.25 6\n3.75 6\n"
    seen = {
        "even count out of order": run("50", ["5"], "9.00 6\n3.00 6\n7.00 6\n5.00 6\n"),
        "mostly pins": run("50", ["3"], "0.50 2\n6.00 6\n0.50 2\n0.50 2\n8.00 6\n0.50 2\n10.00 6\n0.50 2\n"),
        "argument missing": run("50", [], three_full),
        "argument ''": run("50", [""], three_full),
        "argument two": run("50", ["two"], three_full),
        "argument 1.5": run("50", ["1.5"], three_full),
        "no event log": run("50", ["3"], three_full, log=False),
        "VERI_RUN_BUDGET fifty": run("fifty", ["3"], three_full),
        "VERI_RUN_BUDGET -5": run("-5", ["3"], three_full),
        "VERI_RUN_BUDGET ''": run("", ["3"], three_full),
        "8 of 9 steps": run("60", ["1"], "5.50 6\n5.80 6\n6.00 6\n6.10 6\n6.20 6\n6.40 6\n6.56 6\n6.80 6\n"),
        "early in a long plan": run("50", ["10"], "7.00 6\n8.00 6\n"),
    }
    assert seen == {
        "even count out of order": (1, "spent 24.00, steps remaining 5, median 6.00, projection 54.00\n"),
        "mostly pins": (1, "spent 26.50, steps remaining 3, median 8.00, projection 50.50\n"),
        "argument missing": (2, ""),
        "argument ''": (2, ""),
        "argument two": (2, ""),
        "argument 1.5": (2, ""),
        "no event log": (2, ""),
        "VERI_RUN_BUDGET fifty": (2, ""),
        "VERI_RUN_BUDGET -5": (2, ""),
        "VERI_RUN_BUDGET ''": (2, ""),
        "8 of 9 steps": (0, ""),
        "early in a long plan": (1, "spent 15.00, steps remaining 10, median 7.50, projection 90.00\n"),
    }
