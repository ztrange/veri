"""In-process cases for veri/suite_red_resume.py, the module suite-red-resume.sh is a shim over."""
import importlib
import json


def test_check_lets_a_resume_after_a_suite_red_bail_go_on_unless_a_suite_is_red_on_the_default_branch_too_2226(run_cli, tmp_path):
    module = importlib.import_module("veri.suite_red_resume")
    ledger = tmp_path / "issue-7-ledger.md"
    ledger.write_text("- [ ] step\n")
    events = [{"ts": 1, "issue": "7", "event": "bail", "cause": "suite-red", "phase": ""}]
    (tmp_path / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))
    branch = tmp_path / "branch-red"
    branch.write_text("test_a.py — FAIL a\ntest_b.py\n")
    default = tmp_path / "default-red"
    default.write_text("test_c.py — FAIL c\n")
    overlap = tmp_path / "default-overlap"
    overlap.write_text("test_b.py — FAIL other text\n")

    clean = run_cli(module, ["check", str(ledger), str(branch), str(default)])
    shared = run_cli(module, ["check", str(ledger), str(branch), str(overlap)])

    assert clean == (0, "test_a.py — FAIL a\ntest_b.py\n", "")
    assert shared[0] == 1 and "test_b.py" in shared[2] and "test_a.py" not in shared[2]


def test_check_refuses_when_the_last_bail_is_not_suite_red_or_absent_and_exits_2_on_bad_usage_or_an_unreadable_file_2226(run_cli, tmp_path):
    module = importlib.import_module("veri.suite_red_resume")
    ledger = tmp_path / "issue-7-ledger.md"
    ledger.write_text("- [ ] step\n")
    branch = tmp_path / "branch-red"
    branch.write_text("test_a.py — FAIL a\n")
    default = tmp_path / "default-red"
    default.write_text("")
    events = tmp_path / "events.jsonl"

    events.write_text("".join(json.dumps(e) + "\n" for e in [
        {"event": "bail", "cause": "suite-red"},
        {"event": "bail", "cause": "stuck"},
    ]))
    other_cause = run_cli(module, ["check", str(ledger), str(branch), str(default)])
    events.write_text(json.dumps({"event": "step-done"}) + "\n")
    no_bail = run_cli(module, ["check", str(ledger), str(branch), str(default)])
    events.write_text(json.dumps({"event": "bail", "cause": "suite-red"}) + "\n")
    unreadable = run_cli(module, ["check", str(ledger), str(tmp_path / "missing"), str(default)])
    no_args = run_cli(module, [])

    assert other_cause[0] == 1 and other_cause[1] == ""
    assert no_bail[0] == 1 and no_bail[1] == ""
    assert unreadable[0] == 2 and unreadable[1] == ""
    assert no_args[0] == 2 and "usage" in no_args[2]
