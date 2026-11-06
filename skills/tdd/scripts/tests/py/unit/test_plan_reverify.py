"""In-process cases for veri/plan_reverify.py, the module plan-reverify.sh is a shim over."""
import importlib


def test_main_called_with_no_argument_exits_2_printing_the_usage_line_on_stderr(run_cli):
    plan_reverify = importlib.import_module("veri.plan_reverify")

    code, out, err = run_cli(plan_reverify, [])

    assert (code, out, err) == (2, "", "usage: plan-reverify.sh <ledger-file>\n")


def test_main_exits_0_when_the_events_file_beside_the_ledger_is_absent(run_cli, tmp_path):
    plan_reverify = importlib.import_module("veri.plan_reverify")
    ledger = tmp_path / "issue-7-ledger.md"
    ledger.write_text("- [ ] 1. a step\n")

    code, out, err = run_cli(plan_reverify, [str(ledger)])

    assert code == 0


def test_main_exits_3_when_the_newest_plan_commit_is_older_than_the_newest_verify_plan_pass(run_cli, tmp_path, monkeypatch):
    import json
    import subprocess
    plan_reverify = importlib.import_module("veri.plan_reverify")
    ledger = tmp_path / "issue-7-ledger.md"
    ledger.write_text("- [ ] 1. a step\n")
    (tmp_path / "events.jsonl").write_text(json.dumps(
        {"ts": 2000, "actor": "verifier", "phase": "plan", "event": "verdict", "verdict": "PASS"}) + "\n")
    monkeypatch.setattr(plan_reverify, "git",
                        lambda *args, **kwargs: subprocess.CompletedProcess(args, 0, stdout="1000\n"), raising=False)

    code, out, err = run_cli(plan_reverify, [str(ledger)])

    assert code == 3


def test_main_exits_0_when_a_plan_commit_is_newer_than_the_newest_verify_plan_pass(run_cli, tmp_path, monkeypatch):
    import json
    import subprocess
    plan_reverify = importlib.import_module("veri.plan_reverify")
    ledger = tmp_path / "issue-7-ledger.md"
    ledger.write_text("- [ ] 1. a step\n")
    (tmp_path / "events.jsonl").write_text(json.dumps(
        {"ts": 2000, "actor": "verifier", "phase": "plan", "event": "verdict", "verdict": "PASS"}) + "\n")
    monkeypatch.setattr(plan_reverify, "git",
                        lambda *args, **kwargs: subprocess.CompletedProcess(args, 0, stdout="3000\n"), raising=False)

    code, out, err = run_cli(plan_reverify, [str(ledger)])

    assert code == 0


def test_main_exits_3_when_only_a_non_plan_commit_is_newer_than_the_newest_verify_plan_pass(run_cli, tmp_path, monkeypatch):
    import json
    import re
    import subprocess
    plan_reverify = importlib.import_module("veri.plan_reverify")
    ledger = tmp_path / "issue-7-ledger.md"
    ledger.write_text("- [ ] 1. a step\n")
    (tmp_path / "events.jsonl").write_text(json.dumps(
        {"ts": 2000, "actor": "verifier", "phase": "plan", "event": "verdict", "verdict": "PASS"}) + "\n")
    commits = [(3000, "fix: tidy the ledger"), (1000, "plan: write the steps")]

    def fake_git(*args, **kwargs):
        argv = list(args)
        pattern = None
        for i, a in enumerate(argv):
            if a.startswith("--grep="):
                pattern = a.split("=", 1)[1]
            elif a == "--grep":
                pattern = argv[i + 1]
        fmt = next((a for a in argv if a.startswith("--format=") or a.startswith("--pretty=")), "")
        kept = [c for c in commits if pattern is None or re.search(pattern, c[1])]
        if "-1" in argv or "-n1" in argv:
            kept = kept[:1]
        lines = [f"{ts} {subject}" if "%s" in fmt else str(ts) for ts, subject in kept]
        return subprocess.CompletedProcess(args, 0, stdout="".join(line + "\n" for line in lines))

    monkeypatch.setattr(plan_reverify, "git", fake_git, raising=False)

    code, out, err = run_cli(plan_reverify, [str(ledger)])

    assert code == 3


def test_main_exits_0_when_only_other_phase_passes_and_non_verdict_plan_events_are_newer_than_the_plan_commit(run_cli, tmp_path, monkeypatch):
    import json
    import subprocess
    plan_reverify = importlib.import_module("veri.plan_reverify")
    ledger = tmp_path / "issue-7-ledger.md"
    ledger.write_text("- [ ] 1. a step\n")
    events = [
        {"ts": 1000, "actor": "verifier", "phase": "plan", "event": "verdict", "verdict": "PASS"},
        {"ts": 5000, "actor": "verifier", "phase": "green", "event": "verdict", "verdict": "PASS"},
        {"ts": 6000, "actor": "conductor", "phase": "plan", "event": "launch"},
    ]
    (tmp_path / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))
    monkeypatch.setattr(plan_reverify, "git",
                        lambda *args, **kwargs: subprocess.CompletedProcess(args, 0, stdout="3000\n"), raising=False)

    code, out, err = run_cli(plan_reverify, [str(ledger)])

    assert code == 0


def test_main_exits_0_when_a_non_verdict_plan_event_carrying_pass_is_newer_than_the_plan_commit(run_cli, tmp_path, monkeypatch):
    import json
    import subprocess
    plan_reverify = importlib.import_module("veri.plan_reverify")
    ledger = tmp_path / "issue-7-ledger.md"
    ledger.write_text("- [ ] 1. a step\n")
    events = [
        {"ts": 1000, "actor": "verifier", "phase": "plan", "event": "verdict", "verdict": "PASS"},
        {"ts": 6000, "actor": "conductor", "phase": "plan", "event": "launch", "verdict": "PASS"},
    ]
    (tmp_path / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))
    monkeypatch.setattr(plan_reverify, "git",
                        lambda *args, **kwargs: subprocess.CompletedProcess(args, 0, stdout="3000\n"), raising=False)

    code, out, err = run_cli(plan_reverify, [str(ledger)])

    assert code == 0


def test_main_exits_0_when_a_verify_plan_reject_is_newer_than_the_plan_commit(run_cli, tmp_path, monkeypatch):
    import json
    import subprocess
    plan_reverify = importlib.import_module("veri.plan_reverify")
    ledger = tmp_path / "issue-7-ledger.md"
    ledger.write_text("- [ ] 1. a step\n")
    events = [
        {"ts": 1000, "actor": "verifier", "phase": "plan", "event": "verdict", "verdict": "PASS"},
        {"ts": 5000, "actor": "verifier", "phase": "plan", "event": "verdict", "verdict": "REJECT"},
    ]
    (tmp_path / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))
    monkeypatch.setattr(plan_reverify, "git",
                        lambda *args, **kwargs: subprocess.CompletedProcess(args, 0, stdout="3000\n"), raising=False)

    code, out, err = run_cli(plan_reverify, [str(ledger)])

    assert code == 0


def test_main_exits_3_when_a_plan_commit_authored_before_the_pass_was_rebased_to_a_committer_date_after_it(run_cli, tmp_path, monkeypatch):
    import json
    import subprocess
    plan_reverify = importlib.import_module("veri.plan_reverify")
    ledger = tmp_path / "issue-7-ledger.md"
    ledger.write_text("- [ ] 1. a step\n")
    (tmp_path / "events.jsonl").write_text(json.dumps(
        {"ts": 2000, "actor": "verifier", "phase": "plan", "event": "verdict", "verdict": "PASS"}) + "\n")

    def fake_git(*args, **kwargs):
        fmt = next((a for a in args if a.startswith("--format=") or a.startswith("--pretty=")), "")
        stdout = "1000\n" if "%at" in fmt or "%ad" in fmt else "3000\n"
        return subprocess.CompletedProcess(args, 0, stdout=stdout)

    monkeypatch.setattr(plan_reverify, "git", fake_git, raising=False)

    code, out, err = run_cli(plan_reverify, [str(ledger)])

    assert code == 3


def test_main_exits_0_when_two_verify_plan_rejects_newer_than_the_plan_commit_follow_an_older_pass(run_cli, tmp_path, monkeypatch):
    import json
    import subprocess
    plan_reverify = importlib.import_module("veri.plan_reverify")
    ledger = tmp_path / "issue-7-ledger.md"
    ledger.write_text("- [ ] 1. a step\n")
    events = [
        {"ts": 1000, "actor": "verifier", "phase": "plan", "event": "verdict", "verdict": "PASS"},
        {"ts": 4000, "actor": "verifier", "phase": "plan", "event": "verdict", "verdict": "REJECT"},
        {"ts": 8000, "actor": "verifier", "phase": "plan", "event": "verdict", "verdict": "REJECT"},
    ]
    (tmp_path / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))
    monkeypatch.setattr(plan_reverify, "git",
                        lambda *args, **kwargs: subprocess.CompletedProcess(args, 0, stdout="3000\n"), raising=False)

    code, out, err = run_cli(plan_reverify, [str(ledger)])

    assert code == 0


def test_main_exits_0_when_another_issues_newer_verify_plan_pass_sits_in_the_shared_events_file(run_cli, tmp_path, monkeypatch):
    import json
    import subprocess
    plan_reverify = importlib.import_module("veri.plan_reverify")
    ledger = tmp_path / "issue-7-ledger.md"
    ledger.write_text("- [ ] 1. a step\n")
    events = [
        {"ts": 1000, "issue": 7, "actor": "verifier", "phase": "plan", "event": "verdict", "verdict": "PASS"},
        {"ts": 9000, "issue": 8, "actor": "verifier", "phase": "plan", "event": "verdict", "verdict": "PASS"},
    ]
    (tmp_path / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))
    monkeypatch.setattr(plan_reverify, "git",
                        lambda *args, **kwargs: subprocess.CompletedProcess(args, 0, stdout="3000\n"), raising=False)

    code, out, err = run_cli(plan_reverify, [str(ledger)])

    assert code == 0
