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


def test_main_folds_null_unfinished_skipped_absent_conflicting_or_foreign_checks_to_a_verdict(
        monkeypatch, capsys, tmp_path, wait_ci):
    other = "def456"
    done = lambda c: {"status": "completed", "conclusion": c}
    conflict = f"wait-ci.sh: {PR} conflicts with its base branch; no workflow will start until it is rebased\n"
    pending = (3, "", "", True)
    cases = [
        (True, SHA, [done(None)], ["success"], pending),
        (True, SHA, [{"status": "queued", "conclusion": "failure"}, done("success")], [], pending),
        (True, SHA, [done("success")], ["whatever"], (0, "", "", False)),
        (True, SHA, [done("success")], ["pending"], pending),
        (True, SHA, [done("skipped"), done("skipped")], ["success"], pending),
        (True, SHA, [], ["success"], pending),
        (False, SHA, [], [], (2, "", conflict, False)),
        (False, SHA, [done("success")], [], (0, "", "", False)),
        (False, SHA, [], ["success"], pending),
        (None, SHA, [], [], pending),
        (True, SHA, [], [], pending),
        (True, other, [done("success")], ["success"], pending),
    ]

    observed = []
    for i, (mergeable, head, runs, states, _) in enumerate(cases):
        work = tmp_path / str(i)
        (work / ".tdd").mkdir(parents=True)
        monkeypatch.chdir(work)
        bodies = {
            PULL: json.dumps({"mergeable": mergeable, "head": {"sha": head}}),
            f"gh api repos/o/r/commits/{head}/check-runs?page=1": json.dumps({"check_runs": runs}),
            f"gh api repos/o/r/commits/{head}/check-runs?page=2": json.dumps({"check_runs": []}),
            f"gh api repos/o/r/commits/{head}/status": json.dumps({"statuses": [{"state": s} for s in states]}),
            "date +%s": "1000\n",
        }
        calls = fake_processes(monkeypatch, lambda line, bodies=bodies: (0, bodies.get(line, ""), ""))
        code = wait_ci.main([PR, "0", "120", SHA])
        captured = capsys.readouterr()
        observed.append((code, captured.out, captured.err, "date +%s" in calls))

    assert observed == [expected for *_, expected in cases]


def test_main_reads_check_run_pages_to_the_empty_one_and_answers_2_when_gh_or_a_body_fails(
        monkeypatch, capsys, wait_ci):
    page_3 = f"gh api repos/o/r/commits/{SHA}/check-runs?page=3"
    head = json.dumps({"mergeable": True, "head": {"sha": SHA}})
    one_run = json.dumps({"check_runs": [{"status": "completed", "conclusion": "success"}]})
    no_runs = json.dumps({"check_runs": []})
    green = json.dumps({"statuses": [{"state": "success"}]})
    gh_err = "gh: HTTP 502: Bad Gateway\n"
    failed = (1, "", gh_err)
    by_sha = f"wait-ci.sh: could not read the checks of {SHA}\n"
    traced = "Traceback (most recent call last):\n"
    cases = [
        ({PULL: head, PAGE_1: one_run, PAGE_2: '{"x": [1], "check_runs":  [  ], "total_count": 1}',
          page_3: failed, STATUS: green},
         (0, "", "", [PULL, PAGE_1, PAGE_2, STATUS])),
        ({PULL: head, PAGE_1: one_run, PAGE_2: failed, STATUS: green},
         (2, "", gh_err + by_sha, [PULL, PAGE_1, PAGE_2])),
        ({PULL: head, PAGE_1: no_runs, STATUS: failed},
         (2, "", gh_err + by_sha, [PULL, PAGE_1, STATUS])),
        ({PULL: failed},
         (2, "", gh_err + UNREADABLE, [PULL])),
        ({PULL: head, PAGE_1: '{"check_runs": [{"status": ', PAGE_2: no_runs, STATUS: green},
         (2, "", traced + by_sha, [PULL, PAGE_1, PAGE_2, STATUS])),
        ({PULL: head, PAGE_1: one_run, PAGE_2: no_runs, STATUS: '[{"state": "success"}]'},
         (2, "", traced + by_sha, [PULL, PAGE_1, PAGE_2, STATUS])),
        ({PULL: head, PAGE_1: one_run, PAGE_2: no_runs, STATUS: '{"statuses": [{"context": "ci"}]}'},
         (2, "", traced + by_sha, [PULL, PAGE_1, PAGE_2, STATUS])),
        ({PULL: '{"mergeable": true, "head": '},
         (2, "", traced + UNREADABLE, [PULL])),
        ({PULL: json.dumps({"mergeable": True, "head": {}})},
         (2, "", traced + UNREADABLE, [PULL])),
    ]

    observed = []
    for bodies, _ in cases:
        calls = []

        def fake_run(args, bodies=bodies, calls=calls, **kwargs):
            line = " ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]])
            calls.append(line)
            answer = bodies.get(line, (1, "", f"unexpected: {line}\n"))
            code, out, err = (0, answer, "") if isinstance(answer, str) else answer
            if kwargs.get("stderr") is None:
                sys.stderr.write(err)
                err = None
            return subprocess.CompletedProcess(args, code, out, err)

        monkeypatch.setattr(subprocess, "run", fake_run)
        try:
            code = wait_ci.main([PR, "60", "120", SHA])
        except Exception as e:
            code = f"raised {type(e).__name__}"
        captured = capsys.readouterr()
        err = captured.err
        if err.startswith(traced):
            err = traced + err.splitlines(keepends=True)[-1]
        observed.append((code, captured.out, err, calls))

    assert observed == [expected for _, expected in cases]
