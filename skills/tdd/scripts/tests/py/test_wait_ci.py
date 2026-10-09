"""In-process cases for veri/wait_ci.py, the module wait-ci.sh is a shim over."""
import importlib
import json
import os
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
