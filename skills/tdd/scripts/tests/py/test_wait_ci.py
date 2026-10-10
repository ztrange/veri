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
        ({"mergeable": True, "head": {"sha": None}}, ["success"], [], (2, "", UNREADABLE, [PULL])),
        ({"mergeable": True, "head": {"sha": ""}}, ["success"], [], (2, "", UNREADABLE, [PULL])),
    ]

    observed = [one_poll(fake_processes, capsys, wait_ci, pull, conclusions, states)
                for pull, conclusions, states, _ in cases]

    assert observed == [expected for *_, expected in cases]


def test_main_ends_its_stderr_with_the_unreadable_line_when_gh_cannot_read_the_pull(monkeypatch, capsys, wait_ci, fake_processes):
    code, out, err, calls = one_poll(fake_processes, capsys, wait_ci, None, ["success"], [])

    assert (code, out, err.endswith(UNREADABLE), calls) == (2, "", True, [PULL])


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
    stderr); stderr reaches sys.stderr unless the caller captures it."""
    clock = iter(range(0, 6000, 60))

    def answer(line, **kwargs):
        if line == "date +%s":
            return 0, f"{next(clock)}\n", ""
        if line.startswith("sleep "):
            return 0, "", ""
        body = refused(line) or bodies.get(line, (1, "", f"unexpected: {line}\n"))
        code, out, err = (0, body, "") if isinstance(body, str) else body
        if kwargs.get("stderr") is None:
            sys.stderr.write(err)
        return code, out, err

    fake_processes(answer)


def check_run(name, sha, status, conclusion=None):
    return {"name": name, "head_sha": sha, "status": status, "conclusion": conclusion}


def legacy(state):
    return {"context": "legacy", "state": state}


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

    skill = (pathlib.Path(__file__).resolve().parents[3] / "SKILL.md").read_text()
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
        "stale across": [(3, False, False), (2, False, True)],
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
        "legacy with no state": (2, 1),
    }


def test_main_reads_the_given_shas_own_check_runs_to_pending_unreadable_red_green_or_never_green_on_all_skipped(
        tmp_path, wait_ci, fake_processes, run_cli):
    run = lambda name, status, conclusion=None: check_run(name, FULL_SHA, status, conclusion)
    by_sha = f"wait-ci.sh: could not read the checks of {FULL_SHA}\n"

    def waited(name, pages, statuses=(), state="pending"):
        work = tmp_path / name
        (work / ".tdd").mkdir(parents=True)
        bodies = {
            PULL: OPEN_PULL,
            f"{COMMITS}/status": json.dumps(
                {"state": state, "sha": FULL_SHA, "total_count": len(statuses), "statuses": list(statuses)}),
        }
        for n, page in enumerate(list(pages) + [[]], start=1):
            bodies[f"{COMMITS}/check-runs?page={n}"] = page if isinstance(page, tuple) else json.dumps(
                {"total_count": sum(len(p) for p in pages if isinstance(p, list)), "check_runs": page})
        served(fake_processes, bodies)
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
        "unreadable": (2, "", "gh: Not Found (HTTP 404)\n" + by_sha),
        "failure": (1, "", ""),
        "neutral and skipped beside in progress": (3, "", ""),
        "failure beyond the first page": (1, "", ""),
        "runs and statuses all succeeded": (0, "", ""),
        "all skipped": (3, "", ""),
    }


def test_main_reads_the_shas_legacy_statuses_and_with_no_head_sha_the_rest_pull_head_whether_graphql_works_or_is_refused(
        tmp_path, wait_ci, fake_processes, run_cli):
    run = lambda status, conclusion=None: check_run("gates", FULL_SHA, status, conclusion)
    by_sha = "gh: Not Found (HTTP 404)\n" + f"wait-ci.sh: could not read the checks of {FULL_SHA}\n"
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
           for want, answer in (("green", (0, "", "")), ("red", (1, "", "")),
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
        total = sum(len(page) for page in pages)
        bodies = {
            PULL: OPEN_PULL,
            f"{COMMITS}/status": json.dumps(
                {"state": "success", "sha": FULL_SHA, "total_count": len(statuses), "statuses": list(statuses)}),
        }
        for n, page in enumerate(list(pages) + [[]], start=1):
            bodies[f"{COMMITS}/check-runs?page={n}"] = bad_gateway if n == broken else json.dumps(
                {"total_count": total, "check_runs": page})
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
    by_sha = "HTTP 502: Bad Gateway\n" + f"wait-ci.sh: could not read the checks of {FULL_SHA}\n"

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
        "five runs on one page": (1, "", ""),
        "the same runs over three pages": (1, "", ""),
        "first and only page fails": (2, "", by_sha),
        "a later page fails": (2, "", by_sha),
    }
