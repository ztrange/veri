"""In-process cases for veri/wait_ci.py, the module wait-ci.sh is a shim over."""
import importlib
import json
import os
import pathlib
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

USAGE = "usage: wait-ci.sh <pr-url> [slice-seconds] [total-seconds] [head-sha]\n"


@pytest.fixture
def wait_ci():
    return importlib.import_module("veri.wait_ci")


def fake_processes(monkeypatch, answer):
    """subprocess.run and subprocess.Popen recording each command as one line, its program
    by basename; <answer>(line) -> (exit code, stdout, stderr)."""
    calls = []

    def line_of(args):
        return " ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]])

    def fake_run(args, **kwargs):
        line = line_of(args)
        calls.append(line)
        code, out, err = answer(line)
        return subprocess.CompletedProcess(args, code, out, err)

    def fake_popen(args, *rest, **kwargs):
        calls.append(line_of(args))
        raise AssertionError(f"unexpected Popen: {line_of(args)}")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    return calls


def test_main_refuses_a_missing_or_empty_pr_url_with_its_usage_and_no_process(monkeypatch, capsys, wait_ci):
    calls = fake_processes(monkeypatch, lambda line: (0, "", ""))

    observed = []
    for argv in ([], ["", "60"]):
        code = wait_ci.main(argv)
        captured = capsys.readouterr()
        observed.append((code, captured.out, captured.err))

    assert calls == []
    assert observed == [(2, "", USAGE), (2, "", USAGE)]


PR = "https://github.com/o/r/pull/1"
SHA = "abc123"
PULL = "gh api repos/o/r/pulls/1"
PAGE_1 = f"gh api repos/o/r/commits/{SHA}/check-runs?page=1"
PAGE_2 = f"gh api repos/o/r/commits/{SHA}/check-runs?page=2"
STATUS = f"gh api repos/o/r/commits/{SHA}/status"
UNREADABLE = f"wait-ci.sh: could not read the checks of {PR}\n"


def one_poll(monkeypatch, capsys, wait_ci, pull, conclusions, states):
    """main([PR, 60, 120, SHA]) over <pull> (None: gh fails), one check-run page of completed
    runs concluding <conclusions>, and a /status of <states>; (code, stdout, stderr, calls)."""
    runs = [{"status": "completed", "conclusion": c} for c in conclusions]
    bodies = {
        PAGE_1: json.dumps({"total_count": len(runs), "check_runs": runs}),
        PAGE_2: json.dumps({"total_count": len(runs), "check_runs": []}),
        STATUS: json.dumps({"state": "x", "statuses": [{"state": s} for s in states]}),
    }

    def answer(line):
        if line == PULL:
            return (1, "", "") if pull is None else (0, json.dumps(pull), "")
        if line in bodies:
            return 0, bodies[line], ""
        return 0, "", ""

    calls = fake_processes(monkeypatch, answer)
    code = wait_ci.main([PR, "60", "120", SHA])
    captured = capsys.readouterr()
    return code, captured.out, captured.err, calls


def test_main_folds_one_poll_of_completed_runs_to_green_red_or_headless(monkeypatch, capsys, wait_ci):
    head = {"mergeable": True, "head": {"sha": SHA}}
    read_all = [PULL, PAGE_1, PAGE_2, STATUS]
    cases = [
        (head, ["success", "neutral", "skipped"], [], (0, "", "", read_all)),
        (head, ["success"], ["success"], (0, "", "", read_all)),
        (head, ["success", "failure"], [], (1, "", "", read_all)),
        (head, ["SUCCESS"], [], (1, "", "", read_all)),
        (head, ["success"], ["failure"], (1, "", "", read_all)),
        (head, ["success"], ["success", "error"], (1, "", "", read_all)),
        ({"mergeable": True, "head": {"sha": None}}, ["success"], [], (2, "", UNREADABLE, [PULL])),
        ({"mergeable": True, "head": {"sha": ""}}, ["success"], [], (2, "", UNREADABLE, [PULL])),
    ]

    observed = [one_poll(monkeypatch, capsys, wait_ci, pull, conclusions, states)
                for pull, conclusions, states, _ in cases]

    assert observed == [expected for *_, expected in cases]


def test_main_ends_its_stderr_with_the_unreadable_line_when_gh_cannot_read_the_pull(monkeypatch, capsys, wait_ci):
    code, out, err, calls = one_poll(monkeypatch, capsys, wait_ci, None, ["success"], [])

    assert (code, out, err.endswith(UNREADABLE), calls) == (2, "", True, [PULL])


def test_main_folds_an_absent_or_null_statuses_or_check_runs_key_as_empty(monkeypatch, capsys, wait_ci):
    head = json.dumps({"mergeable": True, "head": {"sha": SHA}})
    run = {"status": "completed", "conclusion": "success"}
    page_3 = f"gh api repos/o/r/commits/{SHA}/check-runs?page=3"
    one_run = json.dumps({"total_count": 1, "check_runs": [run]})
    no_runs = json.dumps({"check_runs": []})
    scenarios = [
        {PAGE_1: one_run, PAGE_2: no_runs, STATUS: json.dumps({"state": "x"})},
        {PAGE_1: one_run, PAGE_2: no_runs, STATUS: json.dumps({"state": "x", "statuses": None})},
        {PAGE_1: json.dumps({"total_count": 1}), PAGE_2: one_run, page_3: no_runs,
         STATUS: json.dumps({"state": "x", "statuses": [{"state": "success"}]})},
    ]

    observed = []
    for bodies in scenarios:
        bodies = {PULL: head, **bodies}
        fake_processes(monkeypatch, lambda line: (0, bodies.get(line, ""), ""))
        code = wait_ci.main([PR, "60", "120", SHA])
        captured = capsys.readouterr()
        observed.append((code, captured.out, captured.err))

    assert observed == [(0, "", "")] * 3
