"""Small cases for veri.status --recover: the recovery report."""
import importlib
import json
import os
import subprocess


HEADINGS = ["Runs", "Bailed", "PRs", "Merge lock", "State", "Pending decisions", "Pending messages"]


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

    def run(args, *a, **k):
        out = json.dumps(pulls) if args and args[0] == "gh" else ""
        return subprocess.CompletedProcess(args, 0, stdout=out, stderr="")
    monkeypatch.setattr(status.subprocess, "run", run)

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

    def run(args, *a, **k):
        out = json.dumps(pulls) if args and args[0] == "gh" else ""
        return subprocess.CompletedProcess(args, 0, stdout=out, stderr="")
    monkeypatch.setattr(status.subprocess, "run", run)

    code, out, _ = run_cli(status, ["--recover", "coord"])

    lines = [line.strip() for line in out.splitlines() if line.strip()]
    prs = lines[lines.index("PRs") + 1:lines.index("Merge lock")]
    words = " ".join(prs).replace("#", "").split()
    assert code == 0 and "ready" in words and "draft" not in words and all(w in words for w in ("4722", "3601", "clean")), (code, prs)
