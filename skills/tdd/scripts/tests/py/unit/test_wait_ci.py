"""In-process cases for veri/wait_ci.py, the module wait-ci.sh is a shim over."""
import importlib
import json
import os
import pathlib
import re
import subprocess
import sys

import pytest

USAGE = "usage: wait-ci.sh <pr-url> [slice-seconds] [total-seconds] [head-sha]\n"


@pytest.fixture
def wait_ci():
    return importlib.import_module("veri.wait_ci")


def test_main_refuses_a_missing_or_empty_pr_url_with_its_usage_and_no_process(monkeypatch, capsys, wait_ci, fake_processes):
    calls = fake_processes(lambda line, **_: (0, "", ""))

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
PULL_THRICE = [PULL, "sleep 10", PULL, "sleep 10", PULL]


def one_poll(fake_processes, capsys, wait_ci, pull, conclusions, states):
    """main([PR, 60, 120, SHA]) over <pull> (None: gh fails), one check-run page of completed
    runs concluding <conclusions>, and a /status of <states>; (code, stdout, stderr, calls)."""
    runs = [{"status": "completed", "conclusion": c} for c in conclusions]
    bodies = {
        PAGE_1: json.dumps({"total_count": len(runs), "check_runs": runs}),
        PAGE_2: json.dumps({"total_count": len(runs), "check_runs": []}),
        STATUS: json.dumps({"state": "x", "statuses": [{"state": s} for s in states]}),
    }

    def answer(line, **_):
        if line == PULL:
            return (1, "", "") if pull is None else (0, json.dumps(pull), "")
        if line in bodies:
            return 0, bodies[line], ""
        return 0, "", ""

    calls = fake_processes(answer)
    code = wait_ci.main([PR, "60", "120", SHA])
    captured = capsys.readouterr()
    return code, captured.out, captured.err, calls


def test_main_folds_one_poll_of_completed_runs_to_green_red_or_headless(monkeypatch, capsys, wait_ci, fake_processes):
    head = {"mergeable": True, "head": {"sha": SHA}}
    read_all = [PULL, PAGE_1, PAGE_2, STATUS]
    cases = [
        (head, ["success", "neutral", "skipped"], [], (0, "", "", read_all)),
        (head, ["success"], ["success"], (0, "", "", read_all)),
        (head, ["success", "failure"], [], (1, "", "", read_all)),
        (head, ["SUCCESS"], [], (1, "", "", read_all)),
        (head, ["success"], ["failure"], (1, "", "", read_all)),
        (head, ["success"], ["success", "error"], (1, "", "", read_all)),
        ({"mergeable": True, "head": {"sha": None}}, ["success"], [], (2, "", UNREADABLE, PULL_THRICE)),
        ({"mergeable": True, "head": {"sha": ""}}, ["success"], [], (2, "", UNREADABLE, PULL_THRICE)),
    ]

    observed = [one_poll(fake_processes, capsys, wait_ci, pull, conclusions, states)
                for pull, conclusions, states, _ in cases]

    assert observed == [expected for *_, expected in cases]


def test_main_ends_its_stderr_with_the_unreadable_line_when_gh_cannot_read_the_pull(monkeypatch, capsys, wait_ci, fake_processes):
    code, out, err, calls = one_poll(fake_processes, capsys, wait_ci, None, ["success"], [])

    assert (code, out, err.endswith(UNREADABLE), calls) == (2, "", True, PULL_THRICE)


def test_main_folds_an_absent_or_null_statuses_or_check_runs_key_as_empty(monkeypatch, capsys, wait_ci, fake_processes):
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
        fake_processes(lambda line, **_: (0, bodies.get(line, ""), ""))
        code = wait_ci.main([PR, "60", "120", SHA])
        captured = capsys.readouterr()
        observed.append((code, captured.out, captured.err))

    assert observed == [(0, "", "")] * 3


def test_main_folds_null_unfinished_skipped_absent_conflicting_or_foreign_checks_to_a_verdict(
        monkeypatch, capsys, tmp_path, wait_ci, fake_processes):
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
        calls = fake_processes(lambda line, bodies=bodies, **_: (0, bodies.get(line, ""), ""))
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
    thrice = lambda reads: reads + ["sleep 10"] + reads + ["sleep 10"] + reads
    cases = [
        ({PULL: head, PAGE_1: one_run, PAGE_2: '{"x": [1], "check_runs":  [  ], "total_count": 1}',
          page_3: failed, STATUS: green},
         (0, "", "", [PULL, PAGE_1, PAGE_2, STATUS])),
        ({PULL: head, PAGE_1: one_run, PAGE_2: failed, STATUS: green},
         (2, "", gh_err * 3 + by_sha, thrice([PULL, PAGE_1, PAGE_2]))),
        ({PULL: head, PAGE_1: no_runs, STATUS: failed},
         (2, "", gh_err * 3 + by_sha, thrice([PULL, PAGE_1, STATUS]))),
        ({PULL: failed},
         (2, "", gh_err * 3 + UNREADABLE, PULL_THRICE)),
        ({PULL: head, PAGE_1: '{"check_runs": [{"status": ', PAGE_2: no_runs, STATUS: green},
         (2, "", traced + by_sha, thrice([PULL, PAGE_1, PAGE_2, STATUS]))),
        ({PULL: head, PAGE_1: one_run, PAGE_2: no_runs, STATUS: '[{"state": "success"}]'},
         (2, "", traced + by_sha, thrice([PULL, PAGE_1, PAGE_2, STATUS]))),
        ({PULL: head, PAGE_1: one_run, PAGE_2: no_runs, STATUS: '{"statuses": [{"context": "ci"}]}'},
         (2, "", traced + by_sha, thrice([PULL, PAGE_1, PAGE_2, STATUS]))),
        ({PULL: '{"mergeable": true, "head": '},
         (2, "", traced + UNREADABLE, PULL_THRICE)),
        ({PULL: json.dumps({"mergeable": True, "head": {}})},
         (2, "", traced + UNREADABLE, PULL_THRICE)),
    ]

    observed = []
    for bodies, _ in cases:
        calls = []

        def fake_run(args, bodies=bodies, calls=calls, **kwargs):
            line = " ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]])
            calls.append(line)
            answer = "" if line == "sleep 10" else bodies.get(line, (1, "", f"unexpected: {line}\n"))
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


def test_main_polls_until_its_slice_or_deadline_and_records_the_deadline_in_tdd(
        monkeypatch, capsys, tmp_path, wait_ci):
    past = f"wait-ci.sh: checks of {PR} still pending past the deadline recorded for {SHA}\n"
    bad_sleep = "sleep: invalid time interval 'abc'\n"
    tick = ["date +%s", "sleep 10"]
    cases = [
        ([PR, "20", "100", SHA], None, True, {}, [1000, 1010, 1020],
         (3, "", "", {"ci-deadline-abc123": "1100\n"}, tick * 2 + ["date +%s"])),
        ([PR, "60", "120"], None, True, {"ci-deadline-abc123": "1000\n"}, [1000],
         (2, "", past, {"ci-deadline-abc123": "1000\n"}, ["date +%s"])),
        ([PR, "60", "10", SHA], None, True, {}, [1000, 1010],
         (3, "", "", {"ci-deadline-abc123": "1010\n"}, tick + ["date +%s"])),
        ([PR, "20", "100", SHA], "abc", True, {}, [1000, 1010, 1020],
         (3, "", bad_sleep * 2, {"ci-deadline-abc123": "1100\n"},
          ["date +%s", "sleep abc", "date +%s", "sleep abc", "date +%s"])),
        ([PR, "20", "100", SHA], None, False, {}, [1000, 1010, 1020],
         (3, "", True, None, tick * 2 + ["date +%s"])),
        ([PR, "20", "100", "a/b"], None, True, {}, [1000, 1010, 1020],
         (3, "", True, {}, tick * 2 + ["date +%s"])),
        ([PR, "20", "100", "def456"], None, True, {}, [1000, 1010, 1020],
         (3, "", "", {}, tick * 2 + ["date +%s"])),
        ([PR, "", "10000", SHA], None, True, {}, [1000, 1539, 1540],
         (3, "", "", {"ci-deadline-abc123": "1600\n"}, tick * 2 + ["date +%s"])),
    ]
    bodies = {
        PULL: json.dumps({"mergeable": True, "head": {"sha": SHA}}),
        PAGE_1: json.dumps({"check_runs": [{"status": "completed", "conclusion": None}]}),
        PAGE_2: json.dumps({"check_runs": []}),
        STATUS: json.dumps({"statuses": []}),
    }

    observed = []
    for i, (argv, poll, tdd, marks, clock, expected) in enumerate(cases):
        work = tmp_path / str(i)
        work.mkdir()
        if tdd:
            (work / ".tdd").mkdir()
            for name, text in marks.items():
                (work / ".tdd" / name).write_text(text)
        monkeypatch.chdir(work)
        if poll is None:
            monkeypatch.delenv("VERI_POLL", raising=False)
        else:
            monkeypatch.setenv("VERI_POLL", poll)
        calls = []
        readings = iter(clock)

        def fake_run(args, calls=calls, readings=readings, **kwargs):
            line = " ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]])
            calls.append(line)
            if line == "date +%s":
                code, out, err = 0, f"{next(readings)}\n", ""
            elif line.startswith("sleep "):
                code, out, err = (1, "", bad_sleep) if line == "sleep abc" else (0, "", "")
            else:
                code, out, err = 0, bodies.get(line, ""), ""
            if kwargs.get("stderr") is None:
                sys.stderr.write(err)
                err = None
            return subprocess.CompletedProcess(args, code, out, err)

        monkeypatch.setattr(subprocess, "run", fake_run)
        code = wait_ci.main(argv)
        captured = capsys.readouterr()
        err = captured.err if isinstance(expected[2], str) else bool(captured.err)
        recorded = None if not (work / ".tdd").exists() else {
            str(p.relative_to(work / ".tdd")): p.read_text()
            for p in (work / ".tdd").rglob("*") if p.is_file()}
        observed.append((code, captured.out, err, recorded,
                         [c for c in calls if not c.startswith("gh ")]))

    assert observed == [expected for *_, expected in cases]


def test_main_reads_its_numeric_arguments_with_leading_zeros_as_decimal_and_refuses_a_deadline_file_without_one_issue_776(
        monkeypatch, capsys, tmp_path, wait_ci):
    mark = "ci-deadline-abc123"
    past = f"wait-ci.sh: checks of {PR} still pending past the deadline recorded for {SHA}\n"
    tick = ["date +%s", "sleep 10"]
    raised = "raised"
    locked = "locked"
    refused = f"wait-ci.sh: deadline file .tdd/{mark} is unreadable or not a non-negative whole number\n"
    cases = [
        ([PR, "1000", "700", SHA], {}, [1000, 1540],
         (3, "", "", {mark: "1600\n"}, tick + ["date +%s"])),
        ([PR, "060", "0100", SHA], {}, [1000, 1059, 1060],
         (3, "", "", {mark: "1100\n"}, tick * 2 + ["date +%s"])),
        ([PR, "09", "100", SHA], {}, [1000, 1009], (3, "", "", {mark: "1100\n"}, tick + ["date +%s"])),
        ([PR, "1.5", "100", SHA], {}, [1000],
         (2, "", "wait-ci.sh: slice-seconds '1.5' is not a non-negative whole number\n", {}, [])),
        ([PR, "60", "09", SHA], {}, [1000, 1009], (3, "", "", {mark: "1009\n"}, tick + ["date +%s"])),
        ([PR, "60", "1.5", SHA], {}, [1000],
         (2, "", "wait-ci.sh: total-seconds '1.5' is not a non-negative whole number\n", {}, [])),
        ([PR, "abc", "100", SHA], {}, [1000],
         (2, "", "wait-ci.sh: slice-seconds 'abc' is not a non-negative whole number\n", {}, [])),
        ([PR, "60", "abc", SHA], {}, [1000],
         (2, "", "wait-ci.sh: total-seconds 'abc' is not a non-negative whole number\n", {}, [])),
        ([PR, "-5", "100", SHA], {}, [1000],
         (2, "", "wait-ci.sh: slice-seconds '-5' is not a non-negative whole number\n", {}, [])),
        ([PR, "60", "0", SHA], {}, [1000], (3, "", "", {mark: "1000\n"}, ["date +%s"])),
        ([PR, "60", "-5", SHA], {}, [1000],
         (2, "", "wait-ci.sh: total-seconds '-5' is not a non-negative whole number\n", {}, [])),
        ([PR, "0", "100", SHA], {mark: "1100\n\n\n"}, [1000],
         (3, "", "", {mark: "1100\n\n\n"}, ["date +%s"])),
        ([PR, "0", "100", SHA], {mark: "01100\n"}, [1000],
         (3, "", "", {mark: "01100\n"}, ["date +%s"])),
        ([PR, "60", "100", SHA], {mark: ""}, [1000], (2, "", refused, {mark: ""}, ["date +%s"])),
        ([PR, "60", "100", SHA], {mark: "0x10"}, [1000], (2, "", refused, {mark: "0x10"}, ["date +%s"])),
        ([PR, "60", "100", SHA], {mark: "now\n"}, [1000], (2, "", refused, {mark: "now\n"}, ["date +%s"])),
        ([PR, "60", "100", SHA], {mark: "abc\n"}, [1000], (2, "", refused, {mark: "abc\n"}, ["date +%s"])),
        ([PR, "60", "100", SHA], {mark: "5000 x\n"}, [1000],
         (2, "", refused, {mark: "5000 x\n"}, ["date +%s"])),
        ([PR, "60", "100", SHA], {mark: locked}, [1000], (2, "", refused, {}, ["date +%s"])),
        ([PR, "60", "120", SHA, "extra", "more"], {}, [1000, 1060],
         (3, "", "", {mark: "1120\n"}, tick + ["date +%s"])),
    ]
    bodies = {
        PULL: json.dumps({"mergeable": True, "head": {"sha": SHA}}),
        PAGE_1: json.dumps({"check_runs": [{"status": "completed", "conclusion": None}]}),
        PAGE_2: json.dumps({"check_runs": []}),
        STATUS: json.dumps({"statuses": []}),
    }
    monkeypatch.delenv("VERI_POLL", raising=False)

    observed = []
    for i, (argv, marks, clock, expected) in enumerate(cases):
        work = tmp_path / str(i)
        (work / ".tdd").mkdir(parents=True)
        for name, text in marks.items():
            if text == locked:
                (work / ".tdd" / name).mkdir()
            else:
                (work / ".tdd" / name).write_text(text)
        monkeypatch.chdir(work)
        calls = []
        readings = iter(clock)

        def fake_run(args, calls=calls, readings=readings, **kwargs):
            line = " ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]])
            calls.append(line)
            if line == "date +%s":
                out = f"{next(readings, 99999)}\n"
            else:
                out = bodies.get(line, "")
            return subprocess.CompletedProcess(args, 0, out, "" if kwargs.get("stderr") else None)

        monkeypatch.setattr(subprocess, "run", fake_run)
        try:
            code = wait_ci.main(argv)
        except Exception:
            code = raised
        captured = capsys.readouterr()
        err = None if expected[2] is None else (
            captured.err if isinstance(expected[2], str) else bool(captured.err))
        recorded = {str(p.relative_to(work / ".tdd")): p.read_text()
                    for p in (work / ".tdd").rglob("*") if p.is_file()}
        observed.append((code, captured.out, err, recorded,
                         [c for c in calls if not c.startswith("gh ")]))

    assert observed == [expected for *_, expected in cases]


def test_main_bounds_an_omitted_or_empty_total_by_the_mean_of_the_last_five_ci_runs(
        monkeypatch, capsys, tmp_path, wait_ci):
    mark = "ci-deadline-abc123"
    listing = "gh run list --repo o/r --workflow CI --status %s --limit 5 --json databaseId,conclusion,startedAt,updatedAt"
    success, failure = listing % "success", listing % "failure"
    tick = ["date +%s", "sleep 10", "date +%s"]
    traceback = "traceback"

    def runs(*spans, updated="%02d:%02d:%02dZ"):
        return json.dumps([
            {"databaseId": i, "conclusion": "x", "startedAt": "2026-01-01T00:00:00Z",
             "updatedAt": "2026-01-01T" + updated % (s // 3600, s // 60 % 60, s % 60)}
            for i, s in spans])

    mixed = {success: runs((9, 120), (7, 125), (5, 132)), failure: runs((8, 120), (6, 130), (1, 10000))}
    long = {success: runs((9, 400), (7, 400), (5, 400)), failure: runs((8, 400), (6, 400), (1, 10))}
    instant = {success: runs((9, 0), (7, 0), (5, 0)), failure: runs((8, 0), (6, 0))}
    few = {success: runs((9, 120), (7, 120)), failure: runs((8, 120), (6, 120))}
    fewer = "wait-ci.sh: fewer than 5 success or failure CI runs found; bounding the wait at 540 s\n"
    silent = "wait-ci.sh: gh run list could not answer; bounding the wait at 540 s\n"
    cases = [
        ([PR, "30"], mixed, (3, "", "", {mark: "1251\n"}, [success, failure] + tick)),
        ([PR, "30", "", SHA], mixed, (3, "", "", {mark: "1251\n"}, [success, failure] + tick)),
        ([PR, "30", "", SHA], long, (3, "", "", {mark: "1600\n"}, [success, failure] + tick)),
        ([PR, "30", "", SHA], instant, (3, "", "", {mark: "1000\n"}, [success, failure, "date +%s"])),
        ([PR, "30", "", SHA], few, (3, "", fewer, {mark: "1540\n"}, [success, failure] + tick)),
        ([PR, "30", "", SHA], {success: None}, (3, "", silent, {mark: "1540\n"}, [success] + tick)),
        ([PR, "30", "", SHA], {success: "not json", failure: "[]"},
         (3, "", traceback, {mark: "1030\n"}, [success, failure] + tick)),
        ([PR, "30", "", SHA], {success: runs((9, 120), (7, 120), (5, 120), updated="%02d:%02d:%02d.5Z"),
                               failure: runs((8, 120), (6, 120))},
         (3, "", traceback, {mark: "1030\n"}, [success, failure] + tick)),
        ([PR, "30", "100", SHA], mixed, (3, "", "", {mark: "1100\n"}, tick)),
    ]
    bodies = {
        PULL: json.dumps({"mergeable": True, "head": {"sha": SHA}}),
        PAGE_1: json.dumps({"check_runs": [{"status": "completed", "conclusion": None}]}),
        PAGE_2: json.dumps({"check_runs": []}),
        STATUS: json.dumps({"statuses": []}),
    }
    monkeypatch.delenv("VERI_POLL", raising=False)

    observed = []
    for i, (argv, pages, expected) in enumerate(cases):
        work = tmp_path / str(i)
        (work / ".tdd").mkdir(parents=True)
        monkeypatch.chdir(work)
        calls = []
        readings = iter([1000, 1030])

        def fake_run(args, calls=calls, readings=readings, pages=pages, **kwargs):
            line = " ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]])
            calls.append(line)
            code = 0
            if line == "date +%s":
                out = f"{next(readings, 99999)}\n"
            elif line in pages:
                code, out = (1, "") if pages[line] is None else (0, pages[line])
            else:
                out = bodies.get(line, "")
            return subprocess.CompletedProcess(args, code, out, "" if kwargs.get("stderr") else None)

        monkeypatch.setattr(subprocess, "run", fake_run)
        try:
            code = wait_ci.main(argv)
        except Exception as error:
            code = type(error).__name__
        captured = capsys.readouterr()
        err = captured.err
        if expected[2] == traceback and err.startswith("Traceback") and "bounding" not in err:
            err = traceback
        recorded = {str(p.relative_to(work / ".tdd")): p.read_text()
                    for p in (work / ".tdd").rglob("*") if p.is_file()}
        observed.append((code, captured.out, err, recorded,
                         [c for c in calls if not c.startswith("gh api ")]))

    assert observed == [expected for *_, expected in cases]


def test_main_splits_the_pr_url_at_its_last_pull_and_keys_the_deadline_by_a_head_holding_a_space(
        monkeypatch, capsys, tmp_path, wait_ci, fake_processes):
    pr = "https://github.com/o/r/pull/9/pull/7"
    head = "abc 123"
    commits = f"gh api repos/o/r/pull/9/commits/{head}"
    bodies = {
        "gh api repos/o/r/pull/9/pulls/7": json.dumps({"mergeable": True, "head": {"sha": head}}),
        f"{commits}/check-runs?page=1": json.dumps({"check_runs": [{"status": "completed", "conclusion": None}]}),
        f"{commits}/check-runs?page=2": json.dumps({"check_runs": []}),
        f"{commits}/status": json.dumps({"statuses": []}),
        "date +%s": "1000\n",
    }
    (tmp_path / ".tdd").mkdir()
    monkeypatch.chdir(tmp_path)
    calls = fake_processes(lambda line, **_: (0, bodies.get(line, ""), ""))

    code = wait_ci.main([pr, "0", "100"])
    captured = capsys.readouterr()

    assert (code, captured.out, captured.err, calls,
            {p.name: p.read_text() for p in (tmp_path / ".tdd").iterdir()}) == (
        3, "", "", list(bodies), {f"ci-deadline-{head}": "1100\n"})


PAGE = re.compile(r"gh api repos/o/r/commits/(.+)/check-runs\?page=(\d+)")


def world(fake_processes, heads, runs, statuses=(), tick=60):
    """Fakes gh and the clock: the n-th read of the pull answers heads[n] (None: gh fails),
    its check-run page runs[n], /status <statuses>, and each `date +%s` <tick> more seconds;
    answers the {"reads", "clock"} counts."""
    state = {"reads": 0, "clock": 0}

    def answer(line, **_):
        if line == "date +%s":
            state["clock"] += 1
            return 0, f"{(state['clock'] - 1) * tick}\n", ""
        if line.startswith("sleep "):
            return 0, "", ""
        if line == PULL:
            if heads is None:
                return 1, "", "gh: HTTP 502: Bad Gateway\n"
            head = heads[min(state["reads"], len(heads) - 1)]
            state["reads"] += 1
            return 0, json.dumps({"mergeable": True, "head": {"sha": head}}), ""
        found = PAGE.fullmatch(line)
        if found:
            rows = [] if found.group(2) != "1" else runs[min(state["reads"] - 1, len(runs) - 1)]
            return 0, json.dumps({"check_runs": rows}), ""
        if line.endswith("/status"):
            return 0, json.dumps({"statuses": list(statuses)}), ""
        return 1, "", f"unexpected: {line}\n"

    fake_processes(answer)
    return state


FULL_SHA = "89abcdef0123456789abcdef0123456789abcdef"
COMMITS = f"gh api repos/o/r/commits/{FULL_SHA}"
NOT_FOUND = (1, '{"message":"Not Found"}\n', "gh: Not Found (HTTP 404)\n")
OPEN_PULL = json.dumps({"number": 1, "state": "open", "draft": False, "head": {"sha": FULL_SHA}})


def served(fake_processes, bodies, refused=lambda line: None):
    """Fakes `date +%s` as a clock 60 s on per read, `sleep` as instant, and every other line by
    <refused>'s answer or else <bodies>: a string is stdout of a 0 exit, a tuple (code, stdout,
    stderr); stderr reaches sys.stderr unless the caller captures it. Answers the clock readings it gave."""
    readings = []

    def answer(line, **kwargs):
        if line == "date +%s":
            readings.append(60 * len(readings))
            return 0, f"{readings[-1]}\n", ""
        if line.startswith("sleep "):
            return 0, "", ""
        body = refused(line) or bodies.get(line, (1, "", f"unexpected: {line}\n"))
        code, out, err = (0, body, "") if isinstance(body, str) else body
        if kwargs.get("stderr") is None:
            sys.stderr.write(err)
        return code, out, err

    fake_processes(answer)
    return readings


def check_run(name, sha, status, conclusion=None):
    return {"name": name, "head_sha": sha, "status": status, "conclusion": conclusion}


def legacy(state):
    return {"context": "legacy", "state": state}


def sha_bodies(pages, statuses, state):
    """The open pull, the sha's status document and its check-run pages, a tuple page standing for gh's
    answer, then the empty page that ends them."""
    bodies = {
        PULL: OPEN_PULL,
        f"{COMMITS}/status": json.dumps(
            {"state": state, "sha": FULL_SHA, "total_count": len(statuses), "statuses": list(statuses)}),
    }
    for n, page in enumerate(list(pages) + [[]], start=1):
        bodies[f"{COMMITS}/check-runs?page={n}"] = page if isinstance(page, tuple) else json.dumps(
            {"total_count": sum(len(p) for p in pages if isinstance(p, list)), "check_runs": page})
    return bodies


def test_main_keeps_its_bound_across_reads_calls_and_the_head_sha_it_was_given_and_names_a_pr_it_cannot_read(
        tmp_path, wait_ci, fake_processes, run_cli):
    pending, done = {"status": "in_progress", "conclusion": None}, {"status": "completed", "conclusion": "success"}
    old, new, given = "0123456789abcdef" * 2 + "01234567", "76543210fedcba98" * 2 + "76543210", "89abcdef" * 5
    past = "still pending past the deadline recorded for"

    def calls(name, heads, runs, *argvs):
        work = tmp_path / name
        (work / ".tdd").mkdir(parents=True)
        world(fake_processes, heads, runs)
        answers = []
        for argv in argvs:
            code, out, err = run_cli(wait_ci, [PR, *argv], env={"VERI_POLL": "0"}, cwd=work)
            answers.append((code, UNREADABLE in err, past in err))
        return answers

    skill = (pathlib.Path(__file__).resolve().parents[4] / "SKILL.md").read_text()
    draft_pr_calls = [line for line in skill.splitlines() if "wait-ci.sh <pr-url>" in line]

    observed = {
        "late": calls("late-1800", [SHA], [[pending], [pending], [done]], ["1800"])
                + calls("late-60", [SHA], [[pending], [pending], [done]], ["60"]),
        "gh fails": calls("gh-fails", None, [[pending]], ["1800"]),
        "headless": calls("headless", [None], [[pending]], ["1800"]),
        "across": calls("across", ["fedcba9876543210" * 2 + "fedcba98"], [[pending]], ["120", "120"], ["120", "120"]),
        "total": calls("total", ["00112233445566778899aabbccddeeff00112233"], [[pending]],
                       ["240", "600"], ["240", "600"]),
        "skill passes a slice and an empty total": bool(draft_pr_calls) and all(
            re.search(r'wait-ci\.sh <pr-url> [0-9]+ "" ', line) for line in draft_pr_calls),
        "stale head": calls("stale-head", [old], [[done]], ["60", "60", given]),
        "stale across": calls("stale-across", [old, old, new], [[done]], ["60", "60", given], ["60", "60", given]),
    }

    assert observed == {
        "late": [(0, False, False), (3, False, False)],
        "gh fails": [(2, True, False)],
        "headless": [(2, True, False)],
        "across": [(3, False, False), (2, False, True)],
        "total": [(3, False, False), (3, False, False)],
        "skill passes a slice and an empty total": True,
        "stale head": [(3, False, False)],
        "stale across": [(3, False, False), (3, False, False)],
    }


def test_main_reads_the_rollup_and_legacy_status_contexts_to_pending_green_red_or_unreadable(
        tmp_path, wait_ci, fake_processes, run_cli):
    run = lambda status, conclusion=None: check_run("gates", SHA, status, conclusion)
    success, in_progress = run("completed", "success"), run("in_progress")

    def waited(name, runs, statuses=()):
        work = tmp_path / name
        (work / ".tdd").mkdir(parents=True)
        state = world(fake_processes, [SHA], [runs], statuses, tick=900)
        code, _, _ = run_cli(wait_ci, [PR, "1800", "1800"], env={"VERI_POLL": "0"}, cwd=work)
        return code, state["reads"], state["clock"] <= 3

    observed = {
        "pending": waited("pending", [success, in_progress]),
        "green": waited("green", [success, run("completed", "neutral"), run("completed", "skipped")]),
        "red": waited("red", [success, run("completed", "failure")]),
        "empty is never 0": waited("empty", [])[0] != 0,
        "legacy PENDING": waited("legacy-pending", [success], [legacy("pending")]),
        "legacy EXPECTED": waited("legacy-expected", [success], [legacy("pending")]),
        "legacy FAILURE": waited("legacy-failure", [success], [legacy("failure")]),
        "legacy ERROR": waited("legacy-error", [success], [legacy("error")]),
        "legacy SUCCESS beside a pending run": waited("legacy-success-pending", [in_progress], [legacy("success")]),
        "legacy SUCCESS beside a green run": waited("legacy-success-green", [success], [legacy("success")]),
        "all skipped": waited("all-skipped", [run("completed", "skipped"), run("completed", "skipped")]),
        "legacy with no state": waited("stateless", [success], [{"context": "legacy"}])[:2],
    }

    assert observed == {
        "pending": (3, 2, True),
        "green": (0, 1, True),
        "red": (1, 1, True),
        "empty is never 0": True,
        "legacy PENDING": (3, 2, True),
        "legacy EXPECTED": (3, 2, True),
        "legacy FAILURE": (1, 1, True),
        "legacy ERROR": (1, 1, True),
        "legacy SUCCESS beside a pending run": (3, 2, True),
        "legacy SUCCESS beside a green run": (0, 1, True),
        "all skipped": (3, 2, True),
        "legacy with no state": (2, 3),
    }


def test_main_reads_the_given_shas_own_check_runs_to_pending_unreadable_red_green_or_never_green_on_all_skipped(
        tmp_path, wait_ci, fake_processes, run_cli):
    run = lambda name, status, conclusion=None: check_run(name, FULL_SHA, status, conclusion)
    by_sha = f"wait-ci.sh: could not read the checks of {FULL_SHA}\n"

    def waited(name, pages, statuses=(), state="pending"):
        work = tmp_path / name
        (work / ".tdd").mkdir(parents=True)
        served(fake_processes, sha_bodies(pages, statuses, state))
        return run_cli(wait_ci, [PR, "60", "60", FULL_SHA], env={"VERI_POLL": "0"}, cwd=work)

    success = run("gates", "completed", "success")
    observed = {
        "in progress": waited("race", [[run("gates", "in_progress")]]),
        "unreadable": waited("unread", [NOT_FOUND]),
        "failure": waited("redsha", [[run("gates", "completed", "failure")]]),
        "neutral and skipped beside in progress": waited("quietsha", [[
            run("lint", "completed", "neutral"), run("docs", "completed", "skipped"), run("gates", "in_progress")]]),
        "failure beyond the first page": waited("pagedsha", [
            [run(f"gates-{i}", "completed", "success") for i in range(1, 101)],
            [run("gates-101", "completed", "failure")]]),
        "runs and statuses all succeeded": waited("greensha", [[success]], [legacy("success")], "success"),
        "all skipped": waited("skippedsha", [[run("gates", "completed", "skipped"), run("docs", "completed", "skipped")]]),
    }

    assert observed == {
        "in progress": (3, "", ""),
        "unreadable": (2, "", "gh: Not Found (HTTP 404)\n" * 3 + by_sha),
        "failure": (1, "gates\n", ""),
        "neutral and skipped beside in progress": (3, "", ""),
        "failure beyond the first page": (1, "gates-101\n", ""),
        "runs and statuses all succeeded": (0, "", ""),
        "all skipped": (3, "", ""),
    }


def test_main_reads_the_shas_legacy_statuses_and_with_no_head_sha_the_rest_pull_head_whether_graphql_works_or_is_refused(
        tmp_path, wait_ci, fake_processes, run_cli):
    run = lambda status, conclusion=None: check_run("gates", FULL_SHA, status, conclusion)
    by_sha = "gh: Not Found (HTTP 404)\n" * 3 + f"wait-ci.sh: could not read the checks of {FULL_SHA}\n"
    refusal = ("HTTP 403: GitHub GraphQL is not available from Claude Code sessions; "
               "use the REST API (gh api repos/{owner}/{repo}/...)\n")

    def waited(name, runs, status=None, given=FULL_SHA, graphql="working"):
        work = tmp_path / name
        (work / ".tdd").mkdir(parents=True)
        bodies = {
            PULL: OPEN_PULL,
            f"{COMMITS}/check-runs?page=1": runs if isinstance(runs, tuple) else json.dumps(
                {"total_count": len(runs), "check_runs": runs}),
            f"{COMMITS}/check-runs?page=2": json.dumps({"total_count": 0, "check_runs": []}),
            f"{COMMITS}/status": status if status is not None else json.dumps(
                {"state": "pending", "sha": FULL_SHA, "total_count": 0, "statuses": []}),
        }
        served(fake_processes, bodies, lambda line: graphql == "refused" and (
            line.split(" ")[1] in ("issue", "pr", "repo") or line.startswith("gh api graphql")) and (1, "", refusal))
        return run_cli(wait_ci, [PR, "60", "60"] + ([given] if given else []), env={"VERI_POLL": "0"}, cwd=work)

    def statuses(state, *contexts):
        return json.dumps({"state": state, "sha": FULL_SHA, "total_count": len(contexts), "statuses": list(contexts)})

    success = run("completed", "success")
    observed = {
        "legacy failure": waited("statussha-failure", [success], statuses("failure", legacy("failure"))),
        "legacy error": waited("statussha-error", [success], statuses("error", legacy("error"))),
        "status unreadable": waited("unstatus", [success], NOT_FOUND),
        "status with no statuses key": waited(
            "nostatuses", [success], json.dumps({"state": "pending", "sha": FULL_SHA, "total_count": 0})),
        "legacy pending": waited("pendingstatus", [success], statuses("pending", legacy("pending"))),
        "no runs and no statuses": waited("nonesha", []),
        "no head-sha, own run in progress": waited("nohead", [run("in_progress")], given=None),
    }
    for route in ("working", "refused"):
        for want, runs, status in (
                ("green", [success], statuses("success")),
                ("red", [run("completed", "failure")], None),
                ("pending", [run("in_progress")], None),
                ("unread", NOT_FOUND, None)):
            observed[f"no head-sha, {route} GraphQL, {want}"] = waited(
                f"gql-{route}-{want}", runs, status, given=None, graphql=route)

    assert observed == {
        "legacy failure": (1, "", ""),
        "legacy error": (1, "", ""),
        "status unreadable": (2, "", by_sha),
        "status with no statuses key": (0, "", ""),
        "legacy pending": (3, "", ""),
        "no runs and no statuses": (3, "", ""),
        "no head-sha, own run in progress": (3, "", ""),
        **{f"no head-sha, {route} GraphQL, {want}": answer
           for route in ("working", "refused")
           for want, answer in (("green", (0, "", "")), ("red", (1, "gates\n", "")),
                                ("pending", (3, "", "")), ("unread", (2, "", by_sha)))},
    }


def test_main_reads_the_rest_head_large_documents_and_every_check_run_page_and_names_the_sha_on_a_failed_later_page(
        tmp_path, wait_ci, fake_processes, run_cli):
    run = lambda name, conclusion: check_run(name, FULL_SHA, "completed", conclusion)
    other = "fedcba9876543210fedcba9876543210fedcba98"
    proxy = ("gh: Numeric-ID repository paths (repositories/{id}/...) are not supported through this proxy. "
             "Use repos/{owner}/{repo}/... endpoints instead. (HTTP 403)\n")
    bad_gateway = (1, "", "HTTP 502: Bad Gateway\n")
    sizes = {}

    def waited(name, pages, statuses=(), broken=None):
        work = tmp_path / name
        (work / ".tdd").mkdir(parents=True)
        bodies = sha_bodies([bad_gateway if n == broken else page for n, page in enumerate(pages, start=1)],
                            statuses, "success")
        sizes[name] = [len(bodies[f"{COMMITS}/check-runs?page=1"]), len(bodies[f"{COMMITS}/status"])]
        served(fake_processes, bodies, lambda line: (
            (1, "", proxy) if "repositories/" in line else
            (0, json.dumps({"headRefOid": other, "statusCheckRollup": []}), "") if line.startswith("gh pr view")
            else None))
        return run_cli(wait_ci, [PR, "60", "60", FULL_SHA], env={"VERI_POLL": "0"}, cwd=work)

    def padded(pad):
        return ([dict(run(f"gates-{n}", "success"), output={"summary": pad}) for n in range(40)],
                [{"context": f"legacy-{n}", "state": "success", "description": pad} for n in range(40)])

    short_runs, short_statuses = padded("short")
    long_runs, long_statuses = padded("x" * 8192)
    paged = [[run("gates-1", "success"), run("gates-2", "neutral")],
             [run("gates-3", "success"), run("gates-4", "skipped")],
             [run("gates-5", "failure")]]
    by_sha = "HTTP 502: Bad Gateway\n" * 3 + f"wait-ci.sh: could not read the checks of {FULL_SHA}\n"

    observed = {
        "REST head while pr view reports another": waited("rest-only", [[run("gates", "success")]],
                                                          [legacy("success")]),
        "small documents": waited("large-short", [short_runs], short_statuses),
        "documents over 256 KiB": waited("large-long", [long_runs], long_statuses),
        "both large documents over 256 KiB": all(size > 262144 for size in sizes["large-long"]),
        "five runs on one page": waited("proxy-one", [[r for page in paged for r in page]]),
        "the same runs over three pages": waited("proxy-three", paged),
        "first and only page fails": waited("flaky-1", paged, broken=1),
        "a later page fails": waited("flaky-2", paged, broken=2),
    }

    assert observed == {
        "REST head while pr view reports another": (0, "", ""),
        "small documents": (0, "", ""),
        "documents over 256 KiB": (0, "", ""),
        "both large documents over 256 KiB": True,
        "five runs on one page": (1, "gates-5\n", ""),
        "the same runs over three pages": (1, "gates-5\n", ""),
        "first and only page fails": (2, "", by_sha),
        "a later page fails": (2, "", by_sha),
    }


def test_main_records_a_deadline_from_the_ci_workflows_recent_runs_or_its_capped_total_and_caps_its_slice(
        tmp_path, wait_ci, fake_processes, run_cli):
    paths = {"CI": ".github/workflows/ci.yml", "Pages": ".github/workflows/pages.yml"}

    def ci_runs(rows):
        return [{"databaseId": 1000 - n, "workflowName": wf, "path": paths[wf], "status": status,
                 "conclusion": conclusion, "startedAt": "2026-09-28T10:00:00Z",
                 "updatedAt": "2026-09-28T10:%02d:%02dZ" % divmod(seconds, 60)}
                for n, (wf, status, conclusion, seconds) in enumerate(rows)]

    def listed(line, runs):
        args = line.split(" ")[3:]
        opt = lambda *names: next((args[i + 1] for i, a in enumerate(args[:-1]) if a in names), None)
        workflow, status = opt("--workflow", "-w"), opt("--status", "-s")
        runs = [r for r in runs if workflow is None or workflow in (r["workflowName"], r["path"])]
        runs = [r for r in runs if status is None or status in (r["status"], r["conclusion"])]
        return runs[:int(opt("--limit", "-L") or 20)]

    def waited(name, argv, runs=(), fails=False):
        work = tmp_path / name
        (work / ".tdd").mkdir(parents=True)
        bodies = sha_bodies([[check_run("gates", FULL_SHA, "in_progress")]], [], "pending")
        listings = []

        def run_list(line):
            if not line.startswith("gh run list "):
                return None
            listings.append(line)
            return (1, "", "HTTP 502: Bad Gateway\n") if fails else (0, json.dumps(listed(line, ci_runs(runs))), "")

        readings = served(fake_processes, bodies, run_list)
        code, out, err = run_cli(wait_ci, [PR] + argv, env={"VERI_POLL": "0"}, cwd=work)
        mark = work / ".tdd" / f"ci-deadline-{FULL_SHA}"
        recorded = int(mark.read_text()) - readings[0] if mark.exists() else None
        return code, out, err, recorded, readings[-1] - readings[0], bool(listings)

    done = lambda conclusion, seconds: ("CI", "completed", conclusion, seconds)
    mixed = [("CI", "in_progress", "", 3000), ("Pages", "completed", "success", 3000), done("success", 200),
             done("cancelled", 3000), done("failure", 220), done("skipped", 3000), done("success", 160),
             done("success", 230), done("failure", 190), done("success", 3000)]
    five = lambda *seconds: [done(c, s) for c, s in zip(("success", "failure", "success", "success", "failure"), seconds)]
    few = [done("success", 100), done("cancelled", 3000), done("failure", 120), done("skipped", 3000),
           done("success", 80)]
    fewer = "wait-ci.sh: fewer than 5 success or failure CI runs found; bounding the wait at 540 s\n"
    silent = "HTTP 502: Bad Gateway\nwait-ci.sh: gh run list could not answer; bounding the wait at 540 s\n"

    observed = {
        "omitted total, 2 × mean of 5": waited("computed-omitted", ["60"], mixed),
        "empty total, 2 × mean of 5": waited("computed-empty", ["60", "", FULL_SHA], mixed),
        "25 skipped runs first": waited("computed-deep", ["60"], [done("skipped", 3000)] * 25 + five(100, 120, 80, 110, 90)),
        "60 skipped runs first": waited("computed-deeper", ["60"], [done("skipped", 3000)] * 60 + five(150, 130, 170, 140, 160)),
        "slow runs, capped at 600": waited("computed-slow", ["60"], five(400, 420, 380, 450, 350)),
        "fewer than 5 runs": waited("computed-few", ["60"], few),
        "gh run list fails": waited("computed-gh-fail", ["60"], mixed, fails=True),
        "slice 900, total 600": waited("slice-cap", ["900", "600", FULL_SHA], mixed),
        "explicit total 300": waited("explicit-low", ["60", "300", FULL_SHA], mixed, fails=True),
        "explicit total 1200": waited("explicit-high", ["60", "1200", FULL_SHA], mixed, fails=True),
    }

    assert observed == {
        "omitted total, 2 × mean of 5": (3, "", "", 400, 60, True),
        "empty total, 2 × mean of 5": (3, "", "", 400, 60, True),
        "25 skipped runs first": (3, "", "", 200, 60, True),
        "60 skipped runs first": (3, "", "", 300, 60, True),
        "slow runs, capped at 600": (3, "", "", 600, 60, True),
        "fewer than 5 runs": (3, "", fewer, 540, 60, True),
        "gh run list fails": (3, "", silent, 540, 60, True),
        "slice 900, total 600": (3, "", "", 600, 540, False),
        "explicit total 300": (3, "", "", 300, 60, False),
        "explicit total 1200": (3, "", "", 600, 60, False),
    }


def test_main_names_a_conflicting_pr_at_its_first_read_only_while_its_head_has_no_check_and_otherwise_decides_by_its_checks_issue_688(
        tmp_path, wait_ci, fake_processes, run_cli):
    run = lambda status, conclusion=None: check_run("gates", FULL_SHA, status, conclusion)
    other = "0123456789abcdef" * 2 + "01234567"
    conflict = f"wait-ci.sh: {PR} conflicts with its base branch; no workflow will start until it is rebased\n"
    past = f"wait-ci.sh: checks of {PR} still pending past the deadline recorded for {FULL_SHA}\n"

    def waited(name, mergeable, runs, *argvs):
        work = tmp_path / name
        (work / ".tdd").mkdir(parents=True)
        bodies = sha_bodies([runs] if runs else [], [], "pending")
        bodies[PULL] = json.dumps({"number": 1, "state": "open", "draft": False, "mergeable": mergeable,
                                   "head": {"sha": FULL_SHA}})
        reads = []
        served(fake_processes, bodies, lambda line: reads.append(line) if line == PULL else None)
        answers = []
        for argv in argvs:
            code, out, err = run_cli(wait_ci, [PR, *argv], env={"VERI_POLL": "0"}, cwd=work)
            answers.append((code, out, err))
        return answers, len(reads)

    observed = {
        "conflicting, no check": waited("conflict", False, [], ["540", "600", FULL_SHA]),
        "conflicting, no check, another head given": waited("conflict-stale", False, [], ["540", "600", other]),
        "unknown, no check": waited("unknown", None, [], ["540", "600", FULL_SHA]),
        "conflicting, green": waited("conflict-green", False, [run("completed", "success")],
                                     ["540", "600", FULL_SHA])[0],
        "conflicting, red": waited("conflict-red", False,
                                   [run("completed", "success"), run("completed", "failure")],
                                   ["540", "600", FULL_SHA])[0],
        "conflicting, pending": waited("conflict-pending", False, [run("in_progress")], ["540", "600", FULL_SHA])[0],
        "conflicting, pending across the deadline": waited("conflict-across", False, [run("in_progress")],
                                                           ["120", "120", FULL_SHA], ["120", "120", FULL_SHA])[0],
    }

    assert observed == {
        "conflicting, no check": ([(2, "", conflict)], 1),
        "conflicting, no check, another head given": ([(2, "", conflict)], 1),
        "unknown, no check": ([(3, "", "")], 10),
        "conflicting, green": [(0, "", "")],
        "conflicting, red": [(1, "gates\n", "")],
        "conflicting, pending": [(3, "", "")],
        "conflicting, pending across the deadline": [(3, "", ""), (2, "", past)],
    }


def test_main_names_a_conflicting_pr_at_its_first_read_when_its_head_has_only_skipped_check_runs_issue_2141(
        tmp_path, wait_ci, fake_processes, run_cli):
    conflict = f"wait-ci.sh: {PR} conflicts with its base branch; no workflow will start until it is rebased\n"
    work = tmp_path / "work"
    (work / ".tdd").mkdir(parents=True)
    bodies = sha_bodies([[check_run("gates", FULL_SHA, "completed", "skipped")]], [], "pending")
    bodies[PULL] = json.dumps({"number": 1, "state": "open", "draft": False, "mergeable": False,
                               "head": {"sha": FULL_SHA}})
    reads = []
    served(fake_processes, bodies, lambda line: reads.append(line) if line == PULL else None)

    answer = run_cli(wait_ci, [PR, "540", "600", FULL_SHA], env={"VERI_POLL": "0"}, cwd=work)

    assert (answer, len(reads)) == ((2, "", conflict), 1)


def test_main_ends_its_slice_with_3_when_mergeability_is_unknown_and_its_head_has_only_skipped_check_runs_issue_2141(
        tmp_path, wait_ci, fake_processes, run_cli):
    work = tmp_path / "work"
    (work / ".tdd").mkdir(parents=True)
    bodies = sha_bodies([[check_run("gates", FULL_SHA, "completed", "skipped")]], [], "pending")
    bodies[PULL] = json.dumps({"number": 1, "state": "open", "draft": False, "mergeable": None,
                               "head": {"sha": FULL_SHA}})
    served(fake_processes, bodies)

    answer = run_cli(wait_ci, [PR, "540", "600", FULL_SHA], env={"VERI_POLL": "0"}, cwd=work)

    assert answer == (3, "", "")


def test_main_refuses_a_missing_pr_url_or_a_bad_number_and_records_the_deadline_in_its_own_working_directory_issue_775_776(
        tmp_path, wait_ci, fake_processes, run_cli):
    bad = lambda which, value: f"wait-ci.sh: {which} '{value}' is not a non-negative whole number\n"
    mark = f"ci-deadline-{FULL_SHA}"

    def waited(name, argv, status="in_progress", conclusion=None):
        work = tmp_path / name
        (work / ".tdd").mkdir(parents=True)
        bodies = sha_bodies([[check_run("gates", FULL_SHA, status, conclusion)]], [], "pending")
        reads = []
        served(fake_processes, bodies, lambda line: reads.append(line) if line.startswith("gh ") else None)
        code, out, err = run_cli(wait_ci, argv, env={"VERI_POLL": "0"}, cwd=work)
        recorded = {p.name: p.read_text() for p in (work / ".tdd").iterdir()}
        return code, out, err, recorded, bool(reads)

    observed = {
        "no argument": waited("none", []),
        "empty pr-url, slice 60": waited("empty", ["", "60"]),
        "slice abc": waited("slice-abc", [PR, "abc", "100"]),
        "total xyz": waited("total-xyz", [PR, "60", "xyz"]),
        "slice 1.5": waited("slice-fraction", [PR, "1.5", "100"]),
        "total 1.5": waited("total-fraction", [PR, "60", "1.5"]),
        "total abc": waited("total-abc", [PR, "60", "abc"]),
        "pending, from another working directory": waited("elsewhere-pending", [PR, "540", "600"]),
        "green, from another working directory": waited("elsewhere-green", [PR, "540", "600"],
                                                        "completed", "success"),
    }

    assert observed == {
        "no argument": (2, "", USAGE, {}, False),
        "empty pr-url, slice 60": (2, "", USAGE, {}, False),
        "slice abc": (2, "", bad("slice-seconds", "abc"), {}, False),
        "total xyz": (2, "", bad("total-seconds", "xyz"), {}, False),
        "slice 1.5": (2, "", bad("slice-seconds", "1.5"), {}, False),
        "total 1.5": (2, "", bad("total-seconds", "1.5"), {}, False),
        "total abc": (2, "", bad("total-seconds", "abc"), {}, False),
        "pending, from another working directory": (3, "", "", {mark: "600\n"}, True),
        "green, from another working directory": (0, "", "", {}, True),
    }


def test_main_records_no_deadline_on_a_draft_pr_and_counts_one_from_its_first_ready_call_issue_894(
        tmp_path, wait_ci, fake_processes, run_cli):
    pending, green = [check_run("gates", FULL_SHA, "in_progress")], [check_run("gates", FULL_SHA, "completed", "success")]
    mark = f"ci-deadline-{FULL_SHA}"
    past = f"wait-ci.sh: checks of {PR} still pending past the deadline recorded for {FULL_SHA}\n"

    def waited(name, reads, *argvs):
        """<reads>[n] is (draft, runs) for the n-th read of the pull, its last repeating."""
        work = tmp_path / name
        (work / ".tdd").mkdir(parents=True)
        state = {"reads": 0}

        def answer(line):
            draft, runs = reads[min(state["reads"] - (line != PULL), len(reads) - 1)]
            if line == PULL:
                state["reads"] += 1
                return json.dumps({"number": 1, "state": "open", "draft": draft, "head": {"sha": FULL_SHA}})
            return sha_bodies([runs] if runs else [], [], "pending").get(line)

        served(fake_processes, {}, answer)
        answers = [run_cli(wait_ci, [PR, *argv], env={"VERI_POLL": "0"}, cwd=work) for argv in argvs]
        return answers, {p.name: p.read_text() for p in (work / ".tdd").iterdir()}

    draft, ready = (True, pending), (False, pending)
    observed = {
        "draft, pending": waited("draft", [draft], ["120", "600", FULL_SHA]),
        "draft, then ready and green": waited("readied", [draft, draft, draft, ready, (False, green)],
                                              ["120", "120", FULL_SHA], ["120", "120", FULL_SHA]),
        "draft, then ready and stalled": waited("stalled", [draft, draft, draft, ready],
                                                ["120", "120", FULL_SHA], ["120", "120", FULL_SHA],
                                                ["120", "120", FULL_SHA]),
    }

    assert observed == {
        "draft, pending": ([(3, "", "")], {}),
        "draft, then ready and green": ([(3, "", ""), (0, "", "")], {mark: "300\n"}),
        "draft, then ready and stalled": ([(3, "", ""), (3, "", ""), (2, "", past)], {mark: "300\n"}),
    }


def test_main_counts_a_failed_read_of_the_checks_as_one_pending_poll_and_reads_again_issue_1553(
        tmp_path, wait_ci, fake_processes, run_cli):
    work = tmp_path / "work"
    (work / ".tdd").mkdir(parents=True)
    bodies = sha_bodies([[check_run("gates", FULL_SHA, "completed", "success")]], [], "success")
    status_reads = []

    def refused(line):
        if line == f"{COMMITS}/status":
            status_reads.append(line)
            if len(status_reads) <= 2:
                return (1, "", "gh: HTTP 500: Internal Server Error\n")

    served(fake_processes, bodies, refused)
    code, _, _ = run_cli(wait_ci, [PR, "1800", "1800", FULL_SHA], env={"VERI_POLL": "0"}, cwd=work)

    assert (code, len(status_reads)) == (0, 3)


def test_main_exits_2_naming_the_checks_only_after_three_consecutive_failed_reads_issue_1553(
        tmp_path, wait_ci, fake_processes, run_cli):
    work = tmp_path / "work"
    (work / ".tdd").mkdir(parents=True)
    bodies = sha_bodies([[check_run("gates", FULL_SHA, "completed", "success")]], [], "success")
    status_reads = []

    def refused(line):
        if line == f"{COMMITS}/status":
            status_reads.append(line)
            return (1, "", "")

    served(fake_processes, bodies, refused)
    code, _, err = run_cli(wait_ci, [PR, "1800", "1800", FULL_SHA], env={"VERI_POLL": "0"}, cwd=work)

    assert (code, len(status_reads), err) == (
        2, 3, f"wait-ci.sh: could not read the checks of {FULL_SHA}\n")


def test_main_resets_the_failed_read_count_on_a_successful_poll_so_alternating_failures_never_end_the_wait_issue_1553(
        tmp_path, wait_ci, fake_processes, run_cli):
    work = tmp_path / "work"
    (work / ".tdd").mkdir(parents=True)
    pending = sha_bodies([[check_run("gates", FULL_SHA, "in_progress")]], [], "pending")
    green = sha_bodies([[check_run("gates", FULL_SHA, "completed", "success")]], [], "success")
    polls = []

    def alternating(line):
        if line == f"{COMMITS}/check-runs?page=1":
            polls.append(line)
        body = (green if len(polls) >= 7 else pending).get(line)
        if line == f"{COMMITS}/status" and len(polls) in (1, 3, 5):
            return (1, "", "gh: HTTP 500: Internal Server Error\n")
        return body

    served(fake_processes, {}, alternating)
    code, _, _ = run_cli(wait_ci, [PR, "1800", "1800", FULL_SHA], env={"VERI_POLL": "0"}, cwd=work)

    assert (code, len(polls)) == (0, 7)


def test_main_records_no_deadline_and_ends_its_slice_with_3_while_the_pull_head_differs_from_the_given_sha_issue_1896(
        tmp_path, wait_ci, fake_processes, run_cli):
    other = "fedcba9876543210fedcba9876543210fedcba98"
    work = tmp_path / "work"
    (work / ".tdd").mkdir(parents=True)
    behind = f"gh api repos/o/r/commits/{other}"
    bodies = {
        PULL: json.dumps({"number": 1, "state": "open", "draft": False, "head": {"sha": other}}),
        f"{behind}/status": json.dumps({"state": "pending", "sha": other, "total_count": 0, "statuses": []}),
        f"{behind}/check-runs?page=1": json.dumps({"total_count": 1, "check_runs": [check_run("gates", other, "in_progress")]}),
        f"{behind}/check-runs?page=2": json.dumps({"total_count": 1, "check_runs": []}),
    }

    served(fake_processes, bodies)
    code, _, _ = run_cli(wait_ci, [PR, "120", "600", FULL_SHA], env={"VERI_POLL": "0"}, cwd=work)

    assert (code, sorted(p.name for p in (work / ".tdd").iterdir())) == (3, [])


def test_main_records_the_deadline_at_the_first_call_that_sees_the_given_head_and_a_later_call_inherits_it_issue_1896(
        tmp_path, wait_ci, fake_processes, run_cli):
    other = "fedcba9876543210fedcba9876543210fedcba98"
    work = tmp_path / "work"
    (work / ".tdd").mkdir(parents=True)
    mark = work / ".tdd" / f"ci-deadline-{FULL_SHA}"
    head = {"sha": other}
    argv = [PR, "120", "600", FULL_SHA]
    bodies = {
        PULL: lambda: json.dumps({"number": 1, "state": "open", "draft": False, "head": {"sha": head["sha"]}}),
    }
    for sha in (other, FULL_SHA):
        base = f"gh api repos/o/r/commits/{sha}"
        bodies.update({
            f"{base}/status": json.dumps({"state": "pending", "sha": sha, "total_count": 0, "statuses": []}),
            f"{base}/check-runs?page=1": json.dumps({"total_count": 1, "check_runs": [check_run("gates", sha, "in_progress")]}),
            f"{base}/check-runs?page=2": json.dumps({"total_count": 1, "check_runs": []}),
        })

    readings = served(fake_processes, {}, lambda line: bodies[line]() if line == PULL else bodies.get(line))
    behind = run_cli(wait_ci, argv, env={"VERI_POLL": "0"}, cwd=work)
    recorded_behind = mark.exists()
    head["sha"] = FULL_SHA
    first_seen = len(readings)
    at_head = run_cli(wait_ci, argv, env={"VERI_POLL": "0"}, cwd=work)
    recorded = mark.read_text()
    later = run_cli(wait_ci, argv, env={"VERI_POLL": "0"}, cwd=work)

    assert (behind, recorded_behind, at_head, recorded, later, mark.read_text()) == (
        (3, "", ""), False, (3, "", ""), f"{60 * first_seen + 600}\n", (3, "", ""), f"{60 * first_seen + 600}\n")


def test_main_with_no_head_sha_records_the_deadline_for_the_pull_head_on_its_first_pending_call_issue_1896(
        tmp_path, wait_ci, fake_processes, run_cli):
    work = tmp_path / "work"
    (work / ".tdd").mkdir(parents=True)
    base = f"gh api repos/o/r/commits/{FULL_SHA}"
    bodies = {
        PULL: json.dumps({"number": 1, "state": "open", "draft": False, "head": {"sha": FULL_SHA}}),
        f"{base}/status": json.dumps({"state": "pending", "sha": FULL_SHA, "total_count": 0, "statuses": []}),
        f"{base}/check-runs?page=1": json.dumps({"total_count": 1, "check_runs": [check_run("gates", FULL_SHA, "in_progress")]}),
        f"{base}/check-runs?page=2": json.dumps({"total_count": 1, "check_runs": []}),
    }

    served(fake_processes, bodies)
    code, _, _ = run_cli(wait_ci, [PR, "120", "600"], env={"VERI_POLL": "0"}, cwd=work)

    assert (code, (work / ".tdd" / f"ci-deadline-{FULL_SHA}").read_text()) == (3, "600\n")


def test_main_prints_the_names_of_the_failed_check_runs_as_one_comma_joined_line_on_exit_1_issue_1904(
        monkeypatch, capsys, wait_ci, fake_processes):
    def named(name, conclusion, status="completed"):
        return {"name": name, "status": status, "conclusion": conclusion}

    runs = [named("build", "failure"), named("lint", "success"), named("docs", "SKIPPED"),
            named("Test", "TIMED_OUT"), named("soft", "Neutral"), named("slow", None, "in_progress")]
    bodies = {
        PULL: json.dumps({"mergeable": True, "head": {"sha": SHA}}),
        PAGE_1: json.dumps({"total_count": len(runs), "check_runs": runs}),
        PAGE_2: json.dumps({"total_count": len(runs), "check_runs": []}),
        STATUS: json.dumps({"state": "x", "statuses": []}),
    }
    fake_processes(lambda line, **_: (0, bodies.get(line, ""), ""))

    code = wait_ci.main([PR, "60", "120", SHA])
    captured = capsys.readouterr()

    assert (code, captured.out) == (1, "build,Test\n")


def test_main_prints_nothing_on_stdout_on_exit_0_2_or_3_issue_1904(
        monkeypatch, capsys, tmp_path, wait_ci, fake_processes):
    def named(name, conclusion, status="completed"):
        return {"name": name, "status": status, "conclusion": conclusion}

    cases = [
        (True, [named("build", "success"), named("docs", "skipped")], 0),
        (False, [], 2),
        (True, [named("build", "failure", "queued"), named("lint", "success")], 3),
    ]

    observed = []
    for i, (mergeable, runs, _) in enumerate(cases):
        work = tmp_path / str(i)
        (work / ".tdd").mkdir(parents=True)
        monkeypatch.chdir(work)
        monkeypatch.setenv("VERI_POLL", "0")
        bodies = {
            PULL: json.dumps({"mergeable": mergeable, "head": {"sha": SHA}}),
            PAGE_1: json.dumps({"total_count": len(runs), "check_runs": runs}),
            PAGE_2: json.dumps({"total_count": len(runs), "check_runs": []}),
            STATUS: json.dumps({"state": "x", "statuses": []}),
                    "date +%s": "1000\n",
        }
        fake_processes(lambda line, **_: (0, bodies.get(line, ""), ""))
        code = wait_ci.main([PR, "0", "0", SHA])
        observed.append((code, capsys.readouterr().out))

    assert observed == [(code, "") for *_, code in cases]
