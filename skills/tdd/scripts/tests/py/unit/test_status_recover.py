"""Small cases for veri.status --recover: the recovery report."""
import importlib
import json
import os
import subprocess


HEADINGS = ["Runs", "Bailed", "PRs", "Merge lock", "State", "Pending decisions", "Pending messages"]


def _fake_gh_serving(pulls):
    def run(args, *a, **k):
        out = ""
        if args and args[0] == "gh":
            single = {str(pr["number"]): pr for pr in pulls}.get(args[-1].rsplit("pulls/", 1)[-1]) if "pulls/" in args[-1] else None
            out = json.dumps(single if single is not None else pulls)
        return subprocess.CompletedProcess(args, 0, stdout=out, stderr="")
    return run


def test_3224_recover_with_nothing_taken_prints_the_seven_headings_in_order_with_none_under_each_empty_one_and_free_for_the_lock(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".tdd").mkdir()

    def run(args, *a, **k):
        out = "[]" if args and args[0] == "gh" else ""
        return subprocess.CompletedProcess(args, 0, stdout=out, stderr="")
    monkeypatch.setattr(status.subprocess, "run", run)

    code, out, _ = run_cli(status, ["--recover", "coord"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    expected = []
    for heading in HEADINGS:
        expected += [heading, "free" if heading == "Merge lock" else "none"]
    assert (code, lines) == (0, expected)


def test_3224_recover_lists_under_runs_a_taken_run_held_by_a_live_conductor_with_its_issue_title_and_pid(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    state = tmp_path / ".tdd" / "wt" / "3300" / ".tdd"
    state.mkdir(parents=True)
    (state / "issue-3300.md").write_text("# Plan for #3300 — Teach the widget to sing\n\n- [ ] one\n")
    (state / "conductor.pid").write_text("%d\n" % os.getpid())

    def run(args, *a, **k):
        out = "[]" if args and args[0] == "gh" else ""
        return subprocess.CompletedProcess(args, 0, stdout=out, stderr="")
    monkeypatch.setattr(status.subprocess, "run", run)

    code, out, _ = run_cli(status, ["--recover", "coord"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    runs = lines[lines.index("Runs") + 1:lines.index("Bailed")]
    assert code == 0 and len(runs) == 1, runs
    assert all(word in runs[0] for word in ("3300", "Teach the widget to sing", str(os.getpid()))), runs


def test_3224_recover_runs_line_carries_the_issue_title_without_the_ledger_heading_prefix(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    state = tmp_path / ".tdd" / "wt" / "3301" / ".tdd"
    state.mkdir(parents=True)
    (state / "issue-3301.md").write_text("# Plan for #3301 — Teach the widget to sing\n\n- [ ] one\n")
    (state / "conductor.pid").write_text("%d\n" % os.getpid())

    def run(args, *a, **k):
        out = "[]" if args and args[0] == "gh" else ""
        return subprocess.CompletedProcess(args, 0, stdout=out, stderr="")
    monkeypatch.setattr(status.subprocess, "run", run)

    code, out, _ = run_cli(status, ["--recover", "coord"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    runs = lines[lines.index("Runs") + 1:lines.index("Bailed")]
    assert code == 0 and len(runs) == 1, runs
    assert "Plan for" not in runs[0] and "—" not in runs[0] and "Teach the widget to sing" in runs[0], runs


def test_3224_recover_lists_under_runs_a_taken_run_no_live_conductor_holds_with_issue_title_and_dead_in_place_of_a_pid(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    state = tmp_path / ".tdd" / "wt" / "3302" / ".tdd"
    state.mkdir(parents=True)
    (state / "issue-3302.md").write_text("# Plan for #3302 — Teach the widget to dance\n\n- [ ] one\n")

    def run(args, *a, **k):
        out = "[]" if args and args[0] == "gh" else ""
        return subprocess.CompletedProcess(args, 0, stdout=out, stderr="")
    monkeypatch.setattr(status.subprocess, "run", run)

    code, out, _ = run_cli(status, ["--recover", "coord"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    runs = lines[lines.index("Runs") + 1:lines.index("Bailed")]
    assert code == 0 and len(runs) == 1, runs
    assert all(word in runs[0] for word in ("3302", "Teach the widget to dance", "dead")), runs


def test_3224_recover_lists_under_bailed_each_bailed_run_with_its_issue_and_its_bail_class(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    monkeypatch.setenv("VERI_HOME", str(tmp_path / "home"))
    runs = tmp_path / "home" / "runs" / "acme-widgets"
    runs.mkdir(parents=True)
    (tmp_path / ".tdd").mkdir()

    def journal(number, cause):
        events = [{"ts": 1793700000, "awake": 0, "event": "conductor-start", "pid": 2 ** 22 + 7, "started": "x"},
                  {"ts": 1793700050, "awake": 50, "event": "bail", "cause": cause}]
        (runs / ("%d.jsonl" % number)).write_text("".join(json.dumps(e) + "\n" for e in events))
    journal(3400, "killed-stuck")
    journal(3401, "ci-red")

    def run(args, *a, **k):
        out = "[]" if args and args[0] == "gh" else ""
        return subprocess.CompletedProcess(args, 0, stdout=out, stderr="")
    monkeypatch.setattr(status.subprocess, "run", run)

    code, out, _ = run_cli(status, ["--recover", "coord"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    bailed = lines[lines.index("Bailed") + 1:lines.index("PRs")]
    assert code == 0, out
    assert [l.replace("#", "").split()[:1] + [l.split()[-1]] for l in bailed] == [["3400", "system"], ["3401", "process"]], bailed


def test_3224_recover_bailed_shows_an_unknown_cause_raw_skips_an_empty_journal_and_lists_a_bail_with_no_cause(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    monkeypatch.setenv("VERI_HOME", str(tmp_path / "home"))
    runs = tmp_path / "home" / "runs" / "acme-widgets"
    runs.mkdir(parents=True)
    (tmp_path / ".tdd").mkdir()

    def journal(number, bail):
        events = [{"ts": 1793700000, "awake": 0, "event": "conductor-start", "pid": 2 ** 22 + 7, "started": "x"}, bail]
        (runs / ("%d.jsonl" % number)).write_text("".join(json.dumps(e) + "\n" for e in events))
    journal(3500, {"ts": 1793700050, "awake": 50, "event": "bail", "cause": "moon-phase-wrong"})
    (runs / "3501.jsonl").write_text("")
    journal(3502, {"ts": 1793700050, "awake": 50, "event": "bail"})

    def run(args, *a, **k):
        out = "[]" if args and args[0] == "gh" else ""
        return subprocess.CompletedProcess(args, 0, stdout=out, stderr="")
    monkeypatch.setattr(status.subprocess, "run", run)

    code, out, _ = run_cli(status, ["--recover", "coord"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    bailed = lines[lines.index("Bailed") + 1:lines.index("PRs")]
    assert code == 0, out
    assert [l.split()[0] for l in bailed] == ["#3500", "#3502"], bailed
    assert bailed[0].split()[-1] == "moon-phase-wrong", bailed


def test_3224_recover_lists_under_prs_an_open_draft_pr_with_its_number_the_issue_it_closes_draft_and_its_mergeable_state(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".tdd").mkdir()
    pulls = [{"number": 4721, "draft": True, "state": "open", "mergeable_state": "blocked",
              "title": "Teach the widget to sing", "body": "Closes #3600\n",
              "head": {"ref": "tdd/3600-teach-the-widget"}}]

    monkeypatch.setattr(status.subprocess, "run", _fake_gh_serving(pulls))

    code, out, _ = run_cli(status, ["--recover", "coord"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    prs = lines[lines.index("PRs") + 1:lines.index("Merge lock")]
    words = " ".join(prs).replace("#", "").split()
    assert code == 0 and all(w in words for w in ("4721", "3600", "draft", "blocked")), (code, prs)


def test_3224_recover_lists_under_prs_an_open_pr_that_is_not_a_draft_as_ready(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".tdd").mkdir()
    pulls = [{"number": 4722, "draft": False, "state": "open", "mergeable_state": "clean",
              "title": "Teach the widget to dance", "body": "Closes #3601\n",
              "head": {"ref": "tdd/3601-teach-the-widget"}}]

    monkeypatch.setattr(status.subprocess, "run", _fake_gh_serving(pulls))

    code, out, _ = run_cli(status, ["--recover", "coord"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    prs = lines[lines.index("PRs") + 1:lines.index("Merge lock")]
    words = " ".join(prs).replace("#", "").split()
    assert code == 0 and "ready" in words and "draft" not in words and all(w in words for w in ("4722", "3601", "clean")), (code, prs)


def test_3577_recover_prints_each_open_pr_line_with_the_mergeable_state_from_the_single_pr_read_when_the_list_carries_none(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".tdd").mkdir()
    listed = [{"number": 4730, "draft": False, "state": "open", "title": "Teach the widget to hum",
               "body": "Closes #3602\n", "head": {"ref": "tdd/3602-teach-the-widget"}}]
    single = dict(listed[0], mergeable_state="behind")

    def run(args, *a, **k):
        out = ""
        if args and args[0] == "gh":
            out = json.dumps(single if args[-1].endswith("pulls/4730") else listed)
        return subprocess.CompletedProcess(args, 0, stdout=out, stderr="")
    monkeypatch.setattr(status.subprocess, "run", run)

    code, out, err = run_cli(status, ["--recover", "coord"])

    assert code == 0, (code, err)
    lines = [line.strip() for line in out.splitlines() if line.strip()]
    prs = lines[lines.index("PRs") + 1:lines.index("Merge lock")]
    words = " ".join(prs).replace("#", "").split()
    assert len(prs) == 1 and all(w in words for w in ("4730", "3602", "ready", "behind")), (code, prs)


def test_3224_recover_prints_under_merge_lock_the_live_holders_pid_when_merge_lock_holder_names_one(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".tdd").mkdir()

    def run(args, *a, **k):
        if args and os.path.basename(args[0]) == "merge-lock.sh" and "holder" in args:
            return subprocess.CompletedProcess(args, 0, stdout="48213", stderr="")
        out = "[]" if args and args[0] == "gh" else ""
        return subprocess.CompletedProcess(args, 0, stdout=out, stderr="")
    monkeypatch.setattr(status.subprocess, "run", run)

    code, out, _ = run_cli(status, ["--recover", "coord"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    lock = lines[lines.index("Merge lock") + 1:lines.index("State")]
    assert code == 0 and lock == ["48213"], (code, lock)


def test_3224_recover_lists_under_prs_an_open_pr_whose_body_is_null_or_names_no_issue_and_exits_0(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".tdd").mkdir()
    pulls = [{"number": 4723, "draft": True, "state": "open", "mergeable_state": "unstable",
              "title": "No body", "body": None, "head": {"ref": "feature/no-body"}},
             {"number": 4724, "draft": False, "state": "open", "mergeable_state": "clean",
              "title": "No issue", "body": "Just a tidy-up.\n", "head": {"ref": "feature/tidy"}}]

    monkeypatch.setattr(status.subprocess, "run", _fake_gh_serving(pulls))

    code, out, _ = run_cli(status, ["--recover", "coord"])

    assert code == 0, (code, out, _)
    lines = [line.strip() for line in out.splitlines() if line.strip()]
    prs = lines[lines.index("PRs") + 1:lines.index("Merge lock")]
    words = [" ".join(l.replace("#", "").split()) for l in prs]
    assert code == 0 and len(prs) == 2, (code, prs)
    assert all(w in words[0].split() for w in ("4723", "draft", "unstable")), prs
    assert all(w in words[1].split() for w in ("4724", "ready", "clean")), prs


def test_3224_recover_prints_stale_under_merge_lock_when_merge_lock_holder_answers_stale(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".tdd").mkdir()

    def run(args, *a, **k):
        if args and os.path.basename(args[0]) == "merge-lock.sh" and "holder" in args:
            return subprocess.CompletedProcess(args, 1, stdout="stale lock: 48213 1700000000 issue-9", stderr="")
        out = "[]" if args and args[0] == "gh" else ""
        return subprocess.CompletedProcess(args, 0, stdout=out, stderr="")
    monkeypatch.setattr(status.subprocess, "run", run)

    code, out, _ = run_cli(status, ["--recover", "coord"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    lock = lines[lines.index("Merge lock") + 1:lines.index("State")]
    assert code == 0 and lock == ["stale"], (code, lock)


def test_3224_recover_prints_under_state_the_roles_n_and_lane_read_from_its_state_file(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "role-coord.state").write_text("n=7\nlane=default\n")

    def run(args, *a, **k):
        out = "[]" if args and args[0] == "gh" else ""
        return subprocess.CompletedProcess(args, 0, stdout=out, stderr="")
    monkeypatch.setattr(status.subprocess, "run", run)

    code, out, _ = run_cli(status, ["--recover", "coord"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    state = lines[lines.index("State") + 1:lines.index("Pending decisions")]
    words = " ".join(state).split()
    assert code == 0 and "7" in words and "default" in words, (code, state)


def test_3224_recover_prints_under_state_each_timed_n_change_from_the_roles_state_file_with_its_id_and_time(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "role-coord.state").write_text(
        "n=2\ntimed-n 1 2026-11-08T14:30:00 raise N to 4\ntimed-n 2 2026-11-08T18:45:10 drop N to 1\n")

    def run(args, *a, **k):
        out = "[]" if args and args[0] == "gh" else ""
        return subprocess.CompletedProcess(args, 0, stdout=out, stderr="")
    monkeypatch.setattr(status.subprocess, "run", run)

    code, out, _ = run_cli(status, ["--recover", "coord"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    state = lines[lines.index("State") + 1:lines.index("Pending decisions")]
    first = [l for l in state if "raise N to 4" in l]
    second = [l for l in state if "drop N to 1" in l]
    assert code == 0 and len(first) == 1 and len(second) == 1, (code, state)
    assert "1" in first[0].split() and "2026-11-08T14:30:00" in first[0], first
    assert "2" in second[0].split() and "2026-11-08T18:45:10" in second[0], second


def test_3224_recover_prints_under_state_each_order_override_from_the_roles_state_file_with_its_id_and_time(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "role-coord.state").write_text(
        "n=2\noverride 1 2026-11-08T14:30:00 take 12 before 9\noverride 2 2026-11-08T18:45:10 skip 7\n")

    def run(args, *a, **k):
        out = "[]" if args and args[0] == "gh" else ""
        return subprocess.CompletedProcess(args, 0, stdout=out, stderr="")
    monkeypatch.setattr(status.subprocess, "run", run)

    code, out, _ = run_cli(status, ["--recover", "coord"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    state = lines[lines.index("State") + 1:lines.index("Pending decisions")]
    first = [l for l in state if "take 12 before 9" in l]
    second = [l for l in state if "skip 7" in l]
    assert code == 0 and len(first) == 1 and len(second) == 1, (code, state)
    assert "1" in first[0].split() and "2026-11-08T14:30:00" in first[0], first
    assert "2" in second[0].split() and "2026-11-08T18:45:10" in second[0], second


def test_3224_recover_with_lane_reads_the_named_lanes_state_file_not_the_default_lanes(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "role-coord.state").write_text(
        "n=3\noverride 1 2026-11-08T14:30:00 default-lane-order\n")
    (tmp_path / ".tdd" / "role-coord-mu.state").write_text(
        "n=8\noverride 1 2026-11-08T15:00:00 mu-lane-order\n")

    def run(args, *a, **k):
        out = "[]" if args and args[0] == "gh" else ""
        return subprocess.CompletedProcess(args, 0, stdout=out, stderr="")
    monkeypatch.setattr(status.subprocess, "run", run)

    code, out, _ = run_cli(status, ["--recover", "coord", "--lane", "mu"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    state = lines[lines.index("State") + 1:lines.index("Pending decisions")]
    text = " ".join(state)
    assert code == 0 and "mu-lane-order" in text and "8" in text.split(), (code, state)
    assert "default-lane-order" not in text, state


def test_3224_recover_prints_under_pending_decisions_each_decision_from_the_roles_state_file_in_full_with_its_id_and_time(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "role-coord.state").write_text(
        "n=2\ndecision 1 2026-11-08T14:30:00 merge 4721 before 4722 or hold both for review?\n"
        "decision 2 2026-11-08T18:45:10 park the flaky issue 3300 until Monday\n")

    def run(args, *a, **k):
        out = "[]" if args and args[0] == "gh" else ""
        return subprocess.CompletedProcess(args, 0, stdout=out, stderr="")
    monkeypatch.setattr(status.subprocess, "run", run)

    code, out, _ = run_cli(status, ["--recover", "coord"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    pending = lines[lines.index("Pending decisions") + 1:lines.index("Pending messages")]
    first = [l for l in pending if "merge 4721 before 4722 or hold both for review?" in l]
    second = [l for l in pending if "park the flaky issue 3300 until Monday" in l]
    assert code == 0 and len(first) == 1 and len(second) == 1, (code, pending)
    assert "1" in first[0].split() and "2026-11-08T14:30:00" in first[0], first
    assert "2" in second[0].split() and "2026-11-08T18:45:10" in second[0], second


def test_3224_recover_pending_decisions_holds_exactly_the_decisions_and_none_of_the_other_state_lines(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "role-coord.state").write_text(
        "n=6\nlane=mu\n"
        "timed-n 1 2026-11-08T09:00:00 drop to 2 at nightfall\n"
        "override 2 2026-11-08T10:00:00 run 5150 first\n"
        "decision 3 2026-11-08T11:00:00 hold the release for review?\n"
        "message 4 2026-11-08T12:00:00 told the dev to rebase\n")

    def run(args, *a, **k):
        out = "[]" if args and args[0] == "gh" else ""
        return subprocess.CompletedProcess(args, 0, stdout=out, stderr="")
    monkeypatch.setattr(status.subprocess, "run", run)

    code, out, _ = run_cli(status, ["--recover", "coord"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    pending = lines[lines.index("Pending decisions") + 1:lines.index("Pending messages")]
    assert code == 0 and len(pending) == 1, (code, pending)
    assert "hold the release for review?" in pending[0], pending


def test_3224_recover_prints_under_pending_messages_each_message_from_the_roles_state_file_in_full_with_its_id_and_time(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "role-coord.state").write_text(
        "n=2\nmessage 1 2026-11-08T14:30:00 told the dev of 4721 to rebase; confirmed by a force-push\n"
        "message 2 2026-11-08T18:45:10 asked the reviewer to look at 4722\n")

    def run(args, *a, **k):
        out = "[]" if args and args[0] == "gh" else ""
        return subprocess.CompletedProcess(args, 0, stdout=out, stderr="")
    monkeypatch.setattr(status.subprocess, "run", run)

    code, out, _ = run_cli(status, ["--recover", "coord"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    pending = lines[lines.index("Pending messages") + 1:]
    first = [l for l in pending if "told the dev of 4721 to rebase; confirmed by a force-push" in l]
    second = [l for l in pending if "asked the reviewer to look at 4722" in l]
    assert code == 0 and len(first) == 1 and len(second) == 1, (code, pending)
    assert "1" in first[0].split() and "2026-11-08T14:30:00" in first[0], first
    assert "2" in second[0].split() and "2026-11-08T18:45:10" in second[0], second


def test_3224_recover_exits_2_when_github_refuses_the_open_pr_read_with_stderr_naming_that_read(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".tdd").mkdir()

    def run(args, *a, **k):
        if args and args[0] == "gh":
            return subprocess.CompletedProcess(args, 1, stdout="", stderr="gh: HTTP 403: rate limit exceeded")
        return subprocess.CompletedProcess(args, 0, stdout="", stderr="")
    monkeypatch.setattr(status.subprocess, "run", run)

    code, _out, err = run_cli(status, ["--recover", "coord"])

    assert code == 2, (code, err)
    assert "pull" in err.lower() or "PR" in err, err


def test_3224_recover_given_a_role_other_than_coord_or_dev_exits_2_and_prints_no_report(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    (tmp_path / ".tdd").mkdir()

    def run(args, *a, **k):
        out = "[]" if args and args[0] == "gh" else ""
        return subprocess.CompletedProcess(args, 0, stdout=out, stderr="")
    monkeypatch.setattr(status.subprocess, "run", run)

    code, out, err = run_cli(status, ["--recover", "ops"])

    assert (code, out) == (2, ""), (code, out, err)


def test_3224_recover_round_trip_reports_every_value_role_state_wrote_verbatim_and_a_second_report_from_the_files_alone_is_identical(tmp_path, monkeypatch, run_cli):
    status = importlib.import_module("veri.status")
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(status, "main_working_tree", lambda: str(tmp_path))
    monkeypatch.setattr(role_state, "main_tree", lambda _cwd: str(tmp_path))
    (tmp_path / ".tdd").mkdir()

    def run(args, *a, **k):
        out = "[]" if args and args[0] == "gh" else ""
        return subprocess.CompletedProcess(args, 0, stdout=out, stderr="")
    monkeypatch.setattr(status.subprocess, "run", run)

    values = {"n": "9", "lane": "roundtrip-lane"}
    items = {"decision": "hold the roundtrip release?", "message": "told the roundtrip dev to rebase",
             "override": "take roundtrip 12 first", "timed-n": "raise roundtrip N to 4"}
    codes = [run_cli(role_state, ["coord", "set", field, value])[0] for field, value in values.items()]
    codes += [run_cli(role_state, ["coord", "add", lst, text])[0] for lst, text in items.items()]
    assert codes == [0] * 6, codes

    first_code, first, _ = run_cli(status, ["--recover", "coord"])
    second_code, second, _ = run_cli(status, ["--recover", "coord"])

    assert (first_code, second_code) == (0, 0)
    for value in list(values.values()) + list(items.values()):
        assert value in first, (value, first)
    assert second == first


def test_3224_usage_strings_name_every_verb_and_flag(run_cli):
    role_state = importlib.import_module("veri.role_state")
    status = importlib.import_module("veri.status")
    code, _, err = run_cli(role_state, [])
    for word in ["--lane", "set", "add", "drop", "show", "recovered", "decision", "message", "override", "timed-n"]:
        assert word in err, word
    assert code == 2
    assert "--recover <coord|dev> [--lane <lane>]" in status.USAGE
