"""Small cases for veri.status --recover: the recovery report."""
import importlib
import io
import json
import os
import re

HEADINGS = ["Runs", "Bailed", "PRs", "Merge lock", "State", "Pending decisions", "Pending messages", "Questions",
            "Unasked questions", "Answered questions"]


def _serve(fake_processes, run):
    fake = fake_processes.answers({}, default=lambda line, **k: run(fake.argvs[-1]))
    return fake


def _fake_gh_serving(pulls, states):
    def run(args, *a, **k):
        out = ""
        if args and args[0] == "gh":
            singles = {str(pr["number"]): dict(pr, mergeable_state=states[pr["number"]]) for pr in pulls}
            single = singles.get(args[-1].rsplit("pulls/", 1)[-1]) if "pulls/" in args[-1] else None
            out = json.dumps(single if single is not None else pulls)
        return 0, out, ""
    return run


def test_3224_recover_with_nothing_taken_prints_every_heading_in_order_with_none_under_each_empty_one_and_free_for_the_lock(tmp_path, monkeypatch, run_cli, fake_processes):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "role-dev.state").write_text("")

    def run(args, *a, **k):
        out = "[]" if args and args[0] == "gh" else ""
        return 0, out, ""
    _serve(fake_processes, run)

    code, out, _ = run_cli(status, ["--recover", "dev"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    expected = []
    for heading in HEADINGS:
        expected += [heading, "free" if heading == "Merge lock" else "none"]
    assert (code, lines) == (0, expected)


def test_3224_recover_lists_under_runs_a_taken_run_held_by_a_live_conductor_with_its_issue_title_and_pid(tmp_path, monkeypatch, run_cli, fake_processes):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    state = tmp_path / ".tdd" / "wt" / "3300" / ".tdd"
    state.mkdir(parents=True)
    (state / "issue-3300.md").write_text("# Plan for #3300 — Teach the widget to sing\n\n- [ ] one\n")
    (state / "conductor.pid").write_text("%d\n" % os.getpid())

    def run(args, *a, **k):
        out = "[]" if args and args[0] == "gh" else ""
        return 0, out, ""
    _serve(fake_processes, run)

    code, out, _ = run_cli(status, ["--recover", "dev"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    runs = lines[lines.index("Runs") + 1:lines.index("Bailed")]
    assert code == 0 and len(runs) == 1, runs
    assert all(word in runs[0] for word in ("3300", "Teach the widget to sing", str(os.getpid()))), runs


def test_3224_recover_runs_line_carries_the_issue_title_without_the_ledger_heading_prefix(tmp_path, monkeypatch, run_cli, fake_processes):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    state = tmp_path / ".tdd" / "wt" / "3301" / ".tdd"
    state.mkdir(parents=True)
    (state / "issue-3301.md").write_text("# Plan for #3301 — Teach the widget to sing\n\n- [ ] one\n")
    (state / "conductor.pid").write_text("%d\n" % os.getpid())

    def run(args, *a, **k):
        out = "[]" if args and args[0] == "gh" else ""
        return 0, out, ""
    _serve(fake_processes, run)

    code, out, _ = run_cli(status, ["--recover", "dev"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    runs = lines[lines.index("Runs") + 1:lines.index("Bailed")]
    assert code == 0 and len(runs) == 1, runs
    assert "Plan for" not in runs[0] and "—" not in runs[0] and "Teach the widget to sing" in runs[0], runs


def test_3224_recover_lists_under_runs_a_taken_run_no_live_conductor_holds_with_issue_title_and_dead_in_place_of_a_pid(tmp_path, monkeypatch, run_cli, fake_processes):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    state = tmp_path / ".tdd" / "wt" / "3302" / ".tdd"
    state.mkdir(parents=True)
    (state / "issue-3302.md").write_text("# Plan for #3302 — Teach the widget to dance\n\n- [ ] one\n")

    def run(args, *a, **k):
        out = "[]" if args and args[0] == "gh" else ""
        return 0, out, ""
    _serve(fake_processes, run)

    code, out, _ = run_cli(status, ["--recover", "dev"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    runs = lines[lines.index("Runs") + 1:lines.index("Bailed")]
    assert code == 0 and len(runs) == 1, runs
    assert all(word in runs[0] for word in ("3302", "Teach the widget to dance", "dead")), runs


def test_3224_recover_lists_under_bailed_each_bailed_run_with_its_issue_and_its_bail_class(tmp_path, monkeypatch, run_cli, fake_processes):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
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
        return 0, out, ""
    _serve(fake_processes, run)

    code, out, _ = run_cli(status, ["--recover", "dev"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    bailed = lines[lines.index("Bailed") + 1:lines.index("PRs")]
    assert code == 0, out
    assert [line.replace("#", "").split()[:1] + [line.split()[-1]] for line in bailed] == [["3400", "system"], ["3401", "process"]], bailed


def test_3224_recover_bailed_shows_an_unknown_cause_raw_skips_an_empty_journal_and_lists_a_bail_with_no_cause(tmp_path, monkeypatch, run_cli, fake_processes):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
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
        return 0, out, ""
    _serve(fake_processes, run)

    code, out, _ = run_cli(status, ["--recover", "dev"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    bailed = lines[lines.index("Bailed") + 1:lines.index("PRs")]
    assert code == 0, out
    assert [line.split()[0] for line in bailed] == ["#3500", "#3502"], bailed
    assert bailed[0].split()[-1] == "moon-phase-wrong", bailed


def test_3224_recover_lists_under_prs_an_open_draft_pr_with_its_number_the_issue_it_closes_draft_and_its_mergeable_state(tmp_path, monkeypatch, run_cli, fake_processes):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    (tmp_path / ".tdd").mkdir()
    pulls = [{"number": 4721, "draft": True, "state": "open",
              "title": "Teach the widget to sing", "body": "Closes #3600\n",
              "head": {"ref": "tdd/3600-teach-the-widget"}}]

    _serve(fake_processes, _fake_gh_serving(pulls, {4721: "blocked"}))

    code, out, _ = run_cli(status, ["--recover", "dev"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    prs = lines[lines.index("PRs") + 1:lines.index("Merge lock")]
    words = " ".join(prs).replace("#", "").split()
    assert code == 0 and all(w in words for w in ("4721", "3600", "draft", "blocked")), (code, prs)


def test_3224_recover_lists_under_prs_an_open_pr_that_is_not_a_draft_as_ready(tmp_path, monkeypatch, run_cli, fake_processes):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    (tmp_path / ".tdd").mkdir()
    pulls = [{"number": 4722, "draft": False, "state": "open",
              "title": "Teach the widget to dance", "body": "Closes #3601\n",
              "head": {"ref": "tdd/3601-teach-the-widget"}}]

    _serve(fake_processes, _fake_gh_serving(pulls, {4722: "clean"}))

    code, out, _ = run_cli(status, ["--recover", "dev"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    prs = lines[lines.index("PRs") + 1:lines.index("Merge lock")]
    words = " ".join(prs).replace("#", "").split()
    assert code == 0 and "ready" in words and "draft" not in words and all(w in words for w in ("4722", "3601", "clean")), (code, prs)


def test_3577_recover_prints_each_open_pr_line_with_the_mergeable_state_from_the_single_pr_read_when_the_list_carries_none(tmp_path, monkeypatch, run_cli, fake_processes):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    (tmp_path / ".tdd").mkdir()
    listed = [{"number": 4730, "draft": False, "state": "open", "title": "Teach the widget to hum",
               "body": "Closes #3602\n", "head": {"ref": "tdd/3602-teach-the-widget"}}]
    single = dict(listed[0], mergeable_state="behind")

    def run(args, *a, **k):
        out = ""
        if args and args[0] == "gh":
            out = json.dumps(single if args[-1].endswith("pulls/4730") else listed)
        return 0, out, ""
    _serve(fake_processes, run)

    code, out, err = run_cli(status, ["--recover", "dev"])

    assert code == 0, (code, err)
    lines = [line.strip() for line in out.splitlines() if line.strip()]
    prs = lines[lines.index("PRs") + 1:lines.index("Merge lock")]
    words = " ".join(prs).replace("#", "").split()
    assert len(prs) == 1 and all(w in words for w in ("4730", "3602", "ready", "behind")), (code, prs)


def test_3224_recover_prints_under_merge_lock_the_live_holders_pid_when_merge_lock_holder_names_one(tmp_path, monkeypatch, run_cli, fake_processes):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    (tmp_path / ".tdd").mkdir()

    def run(args, *a, **k):
        if args and os.path.basename(args[0]) == "merge-lock.sh" and "holder" in args:
            return 0, "48213", ""
        out = "[]" if args and args[0] == "gh" else ""
        return 0, out, ""
    _serve(fake_processes, run)

    code, out, _ = run_cli(status, ["--recover", "dev"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    lock = lines[lines.index("Merge lock") + 1:lines.index("State")]
    assert code == 0 and lock == ["48213"], (code, lock)


def test_3224_recover_lists_under_prs_an_open_pr_whose_body_is_null_or_names_no_issue_and_exits_0(tmp_path, monkeypatch, run_cli, fake_processes):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    (tmp_path / ".tdd").mkdir()
    pulls = [{"number": 4723, "draft": True, "state": "open",
              "title": "No body", "body": None, "head": {"ref": "feature/no-body"}},
             {"number": 4724, "draft": False, "state": "open",
              "title": "No issue", "body": "Just a tidy-up.\n", "head": {"ref": "feature/tidy"}}]

    _serve(fake_processes, _fake_gh_serving(pulls, {4723: "unstable", 4724: "clean"}))

    code, out, _ = run_cli(status, ["--recover", "dev"])

    assert code == 0, (code, out, _)
    lines = [line.strip() for line in out.splitlines() if line.strip()]
    prs = lines[lines.index("PRs") + 1:lines.index("Merge lock")]
    words = [" ".join(line.replace("#", "").split()) for line in prs]
    assert code == 0 and len(prs) == 2, (code, prs)
    assert all(w in words[0].split() for w in ("4723", "draft", "unstable")), prs
    assert all(w in words[1].split() for w in ("4724", "ready", "clean")), prs


def test_3224_recover_prints_stale_under_merge_lock_when_merge_lock_holder_answers_stale(tmp_path, monkeypatch, run_cli, fake_processes):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    (tmp_path / ".tdd").mkdir()

    def run(args, *a, **k):
        if args and os.path.basename(args[0]) == "merge-lock.sh" and "holder" in args:
            return 1, "stale lock: 48213 1700000000 issue-9", ""
        out = "[]" if args and args[0] == "gh" else ""
        return 0, out, ""
    _serve(fake_processes, run)

    code, out, _ = run_cli(status, ["--recover", "dev"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    lock = lines[lines.index("Merge lock") + 1:lines.index("State")]
    assert code == 0 and lock == ["stale"], (code, lock)


def test_3224_recover_prints_under_state_the_roles_n_and_lane_read_from_its_state_file(tmp_path, monkeypatch, run_cli, fake_processes):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "role-dev.state").write_text("n=7\nlane=default\n")

    def run(args, *a, **k):
        out = "[]" if args and args[0] == "gh" else ""
        return 0, out, ""
    _serve(fake_processes, run)

    code, out, _ = run_cli(status, ["--recover", "dev"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    state = lines[lines.index("State") + 1:lines.index("Pending decisions")]
    words = " ".join(state).split()
    assert code == 0 and "7" in words and "default" in words, (code, state)


def test_4100_recover_prints_under_state_the_last_recorded_auto_value_and_no_auto_line_when_none_was_recorded(tmp_path, monkeypatch, run_cli, fake_processes):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "role-dev-mu.state").write_text("n=2\nauto=on\nauto=off\n")
    (tmp_path / ".tdd" / "role-dev.state").write_text("n=1\n")

    def run(args, *a, **k):
        out = "[]" if args and args[0] == "gh" else ""
        return 0, out, ""
    _serve(fake_processes, run)

    def state(argv):
        lines = [line.strip() for line in run_cli(status, argv)[1].splitlines() if line.strip()]
        return lines[lines.index("State") + 1:lines.index("Pending decisions")]

    assert (state(["--recover", "dev", "--lane", "mu"]), state(["--recover", "dev"])) == (["n 2", "auto off"], ["n 1"])


def test_3224_recover_prints_under_state_each_timed_n_change_from_the_roles_state_file_with_its_id_and_time(tmp_path, monkeypatch, run_cli, fake_processes):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "role-dev.state").write_text(
        "n=2\ntimed-n 1 2026-11-08T14:30:00 raise N to 4\ntimed-n 2 2026-11-08T18:45:10 drop N to 1\n")

    def run(args, *a, **k):
        out = "[]" if args and args[0] == "gh" else ""
        return 0, out, ""
    _serve(fake_processes, run)

    code, out, _ = run_cli(status, ["--recover", "dev"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    state = lines[lines.index("State") + 1:lines.index("Pending decisions")]
    first = [line for line in state if "raise N to 4" in line]
    second = [line for line in state if "drop N to 1" in line]
    assert code == 0 and len(first) == 1 and len(second) == 1, (code, state)
    assert "1" in first[0].split() and "2026-11-08T14:30:00" in first[0], first
    assert "2" in second[0].split() and "2026-11-08T18:45:10" in second[0], second


def test_3224_recover_prints_under_state_each_order_override_from_the_roles_state_file_with_its_id_and_time(tmp_path, monkeypatch, run_cli, fake_processes):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "role-dev.state").write_text(
        "n=2\noverride 1 2026-11-08T14:30:00 take 12 before 9\noverride 2 2026-11-08T18:45:10 skip 7\n")

    def run(args, *a, **k):
        out = "[]" if args and args[0] == "gh" else ""
        return 0, out, ""
    _serve(fake_processes, run)

    code, out, _ = run_cli(status, ["--recover", "dev"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    state = lines[lines.index("State") + 1:lines.index("Pending decisions")]
    first = [line for line in state if "take 12 before 9" in line]
    second = [line for line in state if "skip 7" in line]
    assert code == 0 and len(first) == 1 and len(second) == 1, (code, state)
    assert "1" in first[0].split() and "2026-11-08T14:30:00" in first[0], first
    assert "2" in second[0].split() and "2026-11-08T18:45:10" in second[0], second


def test_3224_recover_with_lane_reads_the_named_lanes_state_file_not_the_default_lanes(tmp_path, monkeypatch, run_cli, fake_processes):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "role-dev.state").write_text(
        "n=3\noverride 1 2026-11-08T14:30:00 default-lane-order\n")
    (tmp_path / ".tdd" / "role-dev-mu.state").write_text(
        "n=8\noverride 1 2026-11-08T15:00:00 mu-lane-order\n")

    def run(args, *a, **k):
        out = "[]" if args and args[0] == "gh" else ""
        return 0, out, ""
    _serve(fake_processes, run)

    code, out, _ = run_cli(status, ["--recover", "dev", "--lane", "mu"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    state = lines[lines.index("State") + 1:lines.index("Pending decisions")]
    text = " ".join(state)
    assert code == 0 and "mu-lane-order" in text and "8" in text.split(), (code, state)
    assert "default-lane-order" not in text, state


def test_3224_recover_prints_under_pending_decisions_each_decision_from_the_roles_state_file_in_full_with_its_id_and_time(tmp_path, monkeypatch, run_cli, fake_processes):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "role-dev.state").write_text(
        "n=2\ndecision 1 2026-11-08T14:30:00 merge 4721 before 4722 or hold both for review?\n"
        "decision 2 2026-11-08T18:45:10 park the flaky issue 3300 until Monday\n")

    def run(args, *a, **k):
        out = "[]" if args and args[0] == "gh" else ""
        return 0, out, ""
    _serve(fake_processes, run)

    code, out, _ = run_cli(status, ["--recover", "dev"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    pending = lines[lines.index("Pending decisions") + 1:lines.index("Pending messages")]
    first = [line for line in pending if "merge 4721 before 4722 or hold both for review?" in line]
    second = [line for line in pending if "park the flaky issue 3300 until Monday" in line]
    assert code == 0 and len(first) == 1 and len(second) == 1, (code, pending)
    assert "1" in first[0].split() and "2026-11-08T14:30:00" in first[0], first
    assert "2" in second[0].split() and "2026-11-08T18:45:10" in second[0], second


def test_3224_recover_pending_decisions_holds_exactly_the_decisions_and_none_of_the_other_state_lines(tmp_path, monkeypatch, run_cli, fake_processes):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "role-dev.state").write_text(
        "n=6\nlane=mu\n"
        "timed-n 1 2026-11-08T09:00:00 drop to 2 at nightfall\n"
        "override 2 2026-11-08T10:00:00 run 5150 first\n"
        "decision 3 2026-11-08T11:00:00 hold the release for review?\n"
        "message 4 2026-11-08T12:00:00 told the dev to rebase\n")

    def run(args, *a, **k):
        out = "[]" if args and args[0] == "gh" else ""
        return 0, out, ""
    _serve(fake_processes, run)

    code, out, _ = run_cli(status, ["--recover", "dev"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    pending = lines[lines.index("Pending decisions") + 1:lines.index("Pending messages")]
    assert code == 0 and len(pending) == 1, (code, pending)
    assert "hold the release for review?" in pending[0], pending


def test_3224_recover_prints_under_pending_messages_each_message_from_the_roles_state_file_in_full_with_its_id_and_time(tmp_path, monkeypatch, run_cli, fake_processes):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "role-dev.state").write_text(
        "n=2\nmessage 1 2026-11-08T14:30:00 told the dev of 4721 to rebase; confirmed by a force-push\n"
        "message 2 2026-11-08T18:45:10 asked the reviewer to look at 4722\n")

    def run(args, *a, **k):
        out = "[]" if args and args[0] == "gh" else ""
        return 0, out, ""
    _serve(fake_processes, run)

    code, out, _ = run_cli(status, ["--recover", "dev"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    pending = lines[lines.index("Pending messages") + 1:]
    first = [line for line in pending if "told the dev of 4721 to rebase; confirmed by a force-push" in line]
    second = [line for line in pending if "asked the reviewer to look at 4722" in line]
    assert code == 0 and len(first) == 1 and len(second) == 1, (code, pending)
    assert "1" in first[0].split() and "2026-11-08T14:30:00" in first[0], first
    assert "2" in second[0].split() and "2026-11-08T18:45:10" in second[0], second


def test_3577_recover_exits_2_with_a_clean_refusal_naming_the_single_pr_read_when_github_refuses_it(tmp_path, monkeypatch, run_cli, fake_processes):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    (tmp_path / ".tdd").mkdir()
    listed = [{"number": 4730, "draft": False, "state": "open", "title": "Teach the widget to hum",
               "body": "Closes #3602\n", "head": {"ref": "tdd/3602-teach-the-widget"}}]

    def run(args, *a, **k):
        if args and args[0] == "gh" and args[-1].endswith("pulls/4730"):
            return 1, "", "gh: HTTP 502: bad gateway"
        out = json.dumps(listed) if args and args[0] == "gh" else ""
        return 0, out, ""
    _serve(fake_processes, run)

    code, _out, err = run_cli(status, ["--recover", "dev"])

    assert code == 2, (code, err)
    assert err.startswith("status.sh --recover:") and "4730" in err and "Traceback" not in err, err


def test_3577_recover_exits_2_with_a_clean_refusal_when_the_single_pr_read_exits_0_with_empty_stdout(tmp_path, monkeypatch, run_cli, fake_processes):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    (tmp_path / ".tdd").mkdir()
    listed = [{"number": 4730, "draft": False, "state": "open", "title": "Teach the widget to hum",
               "body": "Closes #3602\n", "head": {"ref": "tdd/3602-teach-the-widget"}}]

    def run(args, *a, **k):
        if args and args[0] == "gh" and args[-1].endswith("pulls/4730"):
            return 0, "", ""
        out = json.dumps(listed) if args and args[0] == "gh" else ""
        return 0, out, ""
    _serve(fake_processes, run)

    code, _out, err = run_cli(status, ["--recover", "dev"])

    assert code == 2, (code, err)
    assert err.startswith("status.sh --recover:") and "4730" in err and "Traceback" not in err, err


def test_3577_recover_prints_unknown_for_a_pr_whose_single_read_has_a_null_mergeable_state_and_exits_0(tmp_path, monkeypatch, run_cli, fake_processes):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    (tmp_path / ".tdd").mkdir()
    listed = [{"number": 4730, "draft": False, "state": "open", "title": "Teach the widget to hum",
               "body": "Closes #3602\n", "head": {"ref": "tdd/3602-teach-the-widget"}}]
    single = dict(listed[0], mergeable_state=None)

    def run(args, *a, **k):
        out = ""
        if args and args[0] == "gh":
            out = json.dumps(single if args[-1].endswith("pulls/4730") else listed)
        return 0, out, ""
    _serve(fake_processes, run)

    code, out, err = run_cli(status, ["--recover", "dev"])

    assert code == 0, (code, err)
    lines = [line.strip() for line in out.splitlines() if line.strip()]
    prs = lines[lines.index("PRs") + 1:lines.index("Merge lock")]
    words = " ".join(prs).replace("#", "").split()
    assert len(prs) == 1 and all(w in words for w in ("4730", "3602", "ready", "unknown")) and "clean" not in words, (code, prs)


def test_3577_recover_exits_2_with_a_clean_refusal_when_the_single_pr_read_is_an_object_with_no_mergeable_state(tmp_path, monkeypatch, run_cli, fake_processes):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    (tmp_path / ".tdd").mkdir()
    listed = [{"number": 4730, "draft": False, "state": "open", "title": "Teach the widget to hum",
               "body": "Closes #3602\n", "head": {"ref": "tdd/3602-teach-the-widget"}}]

    def run(args, *a, **k):
        if args and args[0] == "gh" and args[-1].endswith("pulls/4730"):
            return 0, json.dumps({"number": 4730}), ""
        out = json.dumps(listed) if args and args[0] == "gh" else ""
        return 0, out, ""
    _serve(fake_processes, run)

    code, _out, err = run_cli(status, ["--recover", "dev"])

    assert code == 2, (code, err)
    assert err.startswith("status.sh --recover:") and "Traceback" not in err, err


def test_3224_recover_exits_2_when_github_refuses_the_open_pr_read_with_stderr_naming_that_read(tmp_path, monkeypatch, run_cli, fake_processes):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    (tmp_path / ".tdd").mkdir()

    def run(args, *a, **k):
        if args and args[0] == "gh":
            return 1, "", "gh: HTTP 403: rate limit exceeded"
        return 0, "", ""
    _serve(fake_processes, run)

    code, _out, err = run_cli(status, ["--recover", "dev"])

    assert code == 2, (code, err)
    assert "pull" in err.lower() or "PR" in err, err


def test_3224_recover_given_a_role_other_than_dev_or_dev_exits_2_and_prints_no_report(tmp_path, monkeypatch, run_cli, fake_processes):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    (tmp_path / ".tdd").mkdir()

    def run(args, *a, **k):
        out = "[]" if args and args[0] == "gh" else ""
        return 0, out, ""
    _serve(fake_processes, run)

    code, out, err = run_cli(status, ["--recover", "ops"])

    assert (code, out) == (2, ""), (code, out, err)


def test_3224_recover_round_trip_reports_every_value_role_state_wrote_verbatim_and_a_second_report_from_the_files_alone_is_identical(tmp_path, monkeypatch, run_cli, fake_processes):
    status = importlib.import_module("veri.status")
    role_state = importlib.import_module("veri.role_state")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    monkeypatch.setattr(role_state.run_dir, "main_tree_from_files", lambda _cwd: str(tmp_path))
    (tmp_path / ".tdd").mkdir()

    def run(args, *a, **k):
        out = "[]" if args and args[0] == "gh" else ""
        return 0, out, ""
    _serve(fake_processes, run)

    values = {"n": "9", "lane": "roundtrip-lane"}
    items = {"decision": "hold the roundtrip release?", "message": "told the roundtrip dev to rebase",
             "override": "take roundtrip 12 first", "timed-n": "4 until 2026-11-10T20:00:00"}
    codes = [run_cli(role_state, ["dev", "set", field, value])[0] for field, value in values.items()]
    codes += [run_cli(role_state, ["dev", "add", lst, text])[0] for lst, text in items.items()]
    assert codes == [0] * 6, codes

    first_code, first, _ = run_cli(status, ["--recover", "dev"])
    second_code, second, _ = run_cli(status, ["--recover", "dev"])

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
    assert "--recover dev [--lane <lane>]" in status.USAGE


def test_3578_recover_skips_a_wt_directory_with_no_ledger_and_still_renders_every_section_with_exit_0(tmp_path, monkeypatch, run_cli, fake_processes):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    (tmp_path / ".tdd" / "wt" / "fix-2898-pin").mkdir(parents=True)

    def run(args, *a, **k):
        out = "[]" if args and args[0] == "gh" else ""
        return 0, out, ""
    _serve(fake_processes, run)

    code, out, err = run_cli(status, ["--recover", "dev"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    assert code == 0, (code, err)
    assert [line for line in lines if line in HEADINGS] == HEADINGS, lines
    assert lines[lines.index("Runs") + 1:lines.index("Bailed")] == ["none"], lines


def test_3578_recover_with_no_role_state_file_prints_a_state_line_distinct_from_the_none_of_an_empty_state_file(tmp_path, monkeypatch, run_cli, fake_processes):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    (tmp_path / ".tdd").mkdir()

    def run(args, *a, **k):
        out = "[]" if args and args[0] == "gh" else ""
        return 0, out, ""
    _serve(fake_processes, run)

    code, out, err = run_cli(status, ["--recover", "dev", "--lane", "main"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    state = lines[lines.index("State") + 1:lines.index("Pending decisions")]
    assert code == 0, (code, err)
    assert state and state != ["none"], state


def test_3604_recover_reads_every_whole_event_of_every_journal_when_one_journal_holds_a_torn_line(tmp_path, monkeypatch, run_cli, fake_processes):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    monkeypatch.setenv("VERI_HOME", str(tmp_path / "home"))
    runs = tmp_path / "home" / "runs" / "acme-widgets"
    runs.mkdir(parents=True)
    (tmp_path / ".tdd").mkdir()
    start = {"ts": 1793700000, "awake": 0, "event": "conductor-start", "pid": 2 ** 22 + 7, "started": "x"}

    def bail(cause):
        return {"ts": 1793700050, "awake": 50, "event": "bail", "cause": cause}
    torn = 'okens": "2", "output_tokens": "1242"}'
    (runs / "3600.jsonl").write_text("\n".join([json.dumps(start), torn, json.dumps(bail("killed-stuck"))]) + "\n")
    (runs / "3601.jsonl").write_text("\n".join([json.dumps(start), json.dumps(bail("ci-red"))]) + "\n")

    def run(args, *a, **k):
        out = "[]" if args and args[0] == "gh" else ""
        return 0, out, ""
    _serve(fake_processes, run)

    code, out, err = run_cli(status, ["--recover", "dev"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    bailed = lines[lines.index("Bailed") + 1:lines.index("PRs")] if "Bailed" in lines else []
    assert (code, [line.replace("#", "").split()[:1] + [line.split()[-1]] for line in bailed]) == (0, [["3600", "system"], ["3601", "process"]]), (err, bailed)


def test_3604_recover_names_the_journal_file_and_line_number_of_a_torn_line_on_stderr(tmp_path, monkeypatch, run_cli, fake_processes):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('[remote "origin"]\n\turl = git@github.com:acme/widgets.git\n')
    monkeypatch.setenv("VERI_HOME", str(tmp_path / "home"))
    runs = tmp_path / "home" / "runs" / "acme-widgets"
    runs.mkdir(parents=True)
    (tmp_path / ".tdd").mkdir()
    start = {"ts": 1793700000, "awake": 0, "event": "conductor-start", "pid": 2 ** 22 + 7, "started": "x"}
    bail = {"ts": 1793700050, "awake": 50, "event": "bail", "cause": "killed-stuck"}
    torn = 'okens": "2", "output_tokens": "1242"}'
    (runs / "3600.jsonl").write_text("\n".join([json.dumps(start), torn, json.dumps(bail)]) + "\n")

    def run(args, *a, **k):
        out = "[]" if args and args[0] == "gh" else ""
        return 0, out, ""
    _serve(fake_processes, run)

    code, out, err = run_cli(status, ["--recover", "dev"])

    named = [line for line in err.splitlines() if re.search(r"3600\.jsonl\D+2\b", line)]
    assert (code, len(named)) == (0, 1), (code, err)


def test_recover_prs_raises_the_single_pr_refusal_with_its_stderr_when_the_single_read_fails(monkeypatch, fake_processes):
    import pytest
    status = importlib.import_module("veri.status")
    listed = [{"number": 4730, "draft": False, "body": "Closes #3602\n"}]

    def run(args, *a, **k):
        if args and args[0] == "gh" and args[-1].endswith("pulls/4730"):
            return 1, "", "boom\n"
        return 0, json.dumps(listed), ""
    _serve(fake_processes, run)

    with pytest.raises(OSError) as raised:
        status.recover_prs()

    assert str(raised.value) == "status.sh --recover: GitHub refused the single pull request read for #4730: boom"


def test_recover_prs_raises_the_open_pr_refusal_with_its_stderr_when_the_list_read_fails(monkeypatch, fake_processes):
    import pytest
    status = importlib.import_module("veri.status")

    def run(args, *a, **k):
        return 1, "", "boom\n"
    _serve(fake_processes, run)

    with pytest.raises(OSError) as raised:
        status.recover_prs()

    assert str(raised.value) == "status.sh --recover: GitHub refused the open pull request read: boom"


def _questions(out, heading="Questions"):
    """The lines of the recovery report's <heading> section, up to the next heading."""
    lines = [line.strip() for line in out.splitlines() if line.strip()]
    start = lines.index(heading) + 1
    ends = [i for i, line in enumerate(lines) if i >= start and line in HEADINGS]
    return lines[start:ends[0] if ends else len(lines)]


def test_4094_recover_lists_under_questions_each_of_the_lanes_question_files_with_no_answer_heading(tmp_path, monkeypatch, run_cli, fake_processes):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    questions = tmp_path / ".tdd" / "questions"
    questions.mkdir(parents=True)
    (questions / "mu-12.md").write_text("#### Question\nmerge 12 first?\n## Asked s-12\n#### Options\n#### Found\n#### Recommendation\n")
    (questions / "mu-rebase-order.md").write_text("#### Question\nwhich order?\n## Asked s-ro\n")
    (questions / "mu-13.md").write_text("#### Question\nhold 13?\n\n## Answer\nhold it\n")
    (questions / "main-14.md").write_text("#### Question\nanother lane's question\n")
    (questions / "mu.md").write_text("#### Question\nnot a question id of lane mu\n")

    def run(args, *a, **k):
        out = "[]" if args and args[0] == "gh" else ""
        return 0, out, ""
    _serve(fake_processes, run)

    code, out, err = run_cli(status, ["--recover", "dev", "--lane", "mu"])

    assert (code, _questions(out)) == (0, [".tdd/questions/mu-12.md", ".tdd/questions/mu-rebase-order.md"]), (out, err)


def test_4094_recover_with_no_lane_lists_only_the_main_lanes_question_files(tmp_path, monkeypatch, run_cli, fake_processes):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    questions = tmp_path / ".tdd" / "questions"
    questions.mkdir(parents=True)
    (questions / "main-21.md").write_text("#### Question\nopen\n## Asked s-21\n")
    (questions / "mu-22.md").write_text("#### Question\nanother lane\n")

    def run(args, *a, **k):
        out = "[]" if args and args[0] == "gh" else ""
        return 0, out, ""
    _serve(fake_processes, run)

    code, out, err = run_cli(status, ["--recover", "dev"])

    assert (code, _questions(out)) == (0, [".tdd/questions/main-21.md"]), (out, err)


def test_4094_recover_prints_none_under_questions_when_every_question_file_holds_an_answer(tmp_path, monkeypatch, run_cli, fake_processes):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    questions = tmp_path / ".tdd" / "questions"
    questions.mkdir(parents=True)
    (questions / "main-31.md").write_text("#### Question\nanswered\n## Answer\nyes\n")

    def run(args, *a, **k):
        out = "[]" if args and args[0] == "gh" else ""
        return 0, out, ""
    _serve(fake_processes, run)

    code, out, err = run_cli(status, ["--recover", "dev"])

    assert (code, _questions(out)) == (0, ["none"]), (out, err)


def _recover_questions_with(tmp_path, monkeypatch, run_cli, fake_processes, make):
    status = importlib.import_module("veri.status")
    monkeypatch.setattr(status.run_dir, "main_tree", lambda **_: str(tmp_path))
    questions = tmp_path / ".tdd" / "questions"
    questions.mkdir(parents=True)
    (questions / "main-41.md").write_text("#### Question\nopen\n## Asked s-41\n")
    make(questions)

    def run(args, *a, **k):
        out = "[]" if args and args[0] == "gh" else ""
        return 0, out, ""
    _serve(fake_processes, run)
    return run_cli(status, ["--recover", "dev"])


def test_4094_recover_skips_a_question_path_that_is_a_directory_and_still_exits_0(tmp_path, monkeypatch, run_cli, fake_processes):
    code, out, err = _recover_questions_with(tmp_path, monkeypatch, run_cli, fake_processes,
                                             lambda q: (q / "main-42.md").mkdir())
    assert (code, _questions(out), str(tmp_path) in out + err) == (0, [".tdd/questions/main-41.md"], False), (out, err)


def test_4094_recover_skips_a_dangling_question_symlink_and_still_exits_0(tmp_path, monkeypatch, run_cli, fake_processes):
    code, out, err = _recover_questions_with(tmp_path, monkeypatch, run_cli, fake_processes,
                                             lambda q: (q / "main-43.md").symlink_to(q / "gone.md"))
    assert (code, _questions(out), str(tmp_path) in out + err) == (0, [".tdd/questions/main-41.md"], False), (out, err)


def test_4094_recover_lists_a_question_file_that_is_not_utf8_as_open_and_reads_its_answer_heading(tmp_path, monkeypatch, run_cli, fake_processes):
    def make(q):
        (q / "main-44.md").write_bytes(b"#### Question\n\xff\xfe caf\xe9\n## Asked s-44\n")
        (q / "main-45.md").write_bytes(b"#### Question\n\xff\n## Answer\nyes\n")
    code, out, err = _recover_questions_with(tmp_path, monkeypatch, run_cli, fake_processes, make)
    assert (code, _questions(out)) == (0, [".tdd/questions/main-41.md", ".tdd/questions/main-44.md"]), (out, err)


SECTIONS = ("Questions", "Unasked questions", "Answered questions")


def test_4253_recover_lists_each_question_file_in_exactly_one_of_asked_unasked_and_answered_sorted_by_name(tmp_path, monkeypatch, run_cli, fake_processes):
    def make(q):
        (q / "main-50.md").write_text("#### Question\nasked\n\n## Asked 9f2c-session\n")
        (q / "main-51.md").write_text("#### Question\nwritten, never asked\n")
        (q / "main-52.md").write_text("#### Question\nanswered\n\n## Asked s-52\n\n## Answer\nyes\n")
        (q / "main-53.md").write_text("#### Question\nanswered with no session line\n\n## Answer\nyes\n")
        (q / "main-54.md").write_text("#### Question\nan Asked line with no id\n\n## Asked\n## Asked \n")
        (q / "main-55.md").write_text("#### Question\nnot the line itself\n\n## Asked about it later\nsee ## Asked x\n")
        (q / "main-40.md").write_text("#### Question\nsorted first\n")
    code, out, err = _recover_questions_with(tmp_path, monkeypatch, run_cli, fake_processes, make)

    assert code == 0, (out, err)
    assert {heading: _questions(out, heading) for heading in SECTIONS} == {
        "Questions": [".tdd/questions/main-41.md", ".tdd/questions/main-50.md"],
        "Unasked questions": [".tdd/questions/main-40.md", ".tdd/questions/main-51.md", ".tdd/questions/main-54.md",
                              ".tdd/questions/main-55.md"],
        "Answered questions": [".tdd/questions/main-52.md", ".tdd/questions/main-53.md"]}


def test_4253_recover_lists_a_question_file_that_changes_while_it_is_read_in_exactly_one_section(tmp_path, monkeypatch, run_cli, fake_processes):
    status = importlib.import_module("veri.status")
    real_open = open
    texts = iter(["#### Question\nq\n", "#### Question\nq\n## Asked s-70\n", "#### Question\nq\n## Asked s-70\n"])

    def shifting_open(path, *a, **k):
        if str(path).endswith("main-70.md"):
            return io.StringIO(next(texts, "#### Question\nq\n## Asked s-70\n"))
        return real_open(path, *a, **k)
    monkeypatch.setattr(status, "open", shifting_open, raising=False)

    code, out, err = _recover_questions_with(tmp_path, monkeypatch, run_cli, fake_processes,
                                             lambda q: (q / "main-70.md").write_text("#### Question\nq\n"))

    listed = [path for heading in SECTIONS for path in _questions(out, heading)]
    assert (code, listed.count(".tdd/questions/main-70.md")) == (0, 1), (out, err)


def test_4253_recover_ignores_answer_and_asked_lines_inside_a_code_fence(tmp_path, monkeypatch, run_cli, fake_processes):
    def make(q):
        (q / "main-80.md").write_text("#### Question\nq\n\n## Asked s-80\n\n```\n## Answer\n```\n")
        (q / "main-81.md").write_text("#### Question\nq\n\n~~~\n## Asked s-81\n~~~\n")
    code, out, err = _recover_questions_with(tmp_path, monkeypatch, run_cli, fake_processes, make)

    assert (code, [_questions(out, heading) for heading in SECTIONS]) == (
        0, [[".tdd/questions/main-41.md", ".tdd/questions/main-80.md"], [".tdd/questions/main-81.md"], ["none"]]), (out, err)


def test_4253_recover_lists_a_question_file_it_cannot_read_under_questions_only(tmp_path, monkeypatch, run_cli, fake_processes):
    status = importlib.import_module("veri.status")
    real_open = open

    def refusing_open(path, *a, **k):
        if str(path).endswith("main-60.md"):
            raise PermissionError(13, "Permission denied")
        return real_open(path, *a, **k)
    monkeypatch.setattr(status, "open", refusing_open, raising=False)

    def make(q):
        (q / "main-60.md").write_text("#### Question\nunreadable\n\n## Answer\nyes\n")
    code, out, err = _recover_questions_with(tmp_path, monkeypatch, run_cli, fake_processes, make)

    assert (code, [_questions(out, heading) for heading in SECTIONS]) == (
        0, [[".tdd/questions/main-41.md", ".tdd/questions/main-60.md"], ["none"], ["none"]]), (out, err)
