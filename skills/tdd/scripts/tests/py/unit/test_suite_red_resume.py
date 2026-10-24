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


def test_insert_adds_one_suite_repair_step_before_the_first_unchecked_step_through_add_ledger_step_2226(run_cli, tmp_path):
    module = importlib.import_module("veri.suite_red_resume")
    ledger = tmp_path / "issue-7.md"
    ledger.write_text("# Plan for #7\n\n- [x] a ⟦criterion 1⟧\n- [ ] b ⟦criterion 2⟧\n- [ ] c ⟦criterion 3⟧\n")
    (tmp_path / "events.jsonl").write_text(json.dumps({"event": "bail", "cause": "suite-red"}) + "\n")
    branch = tmp_path / "branch-red"
    branch.write_text("test_a.py — FAIL a\ntest_b.py\n")
    step = "- [ ] fix the full-suite failure: test_a.py — FAIL a; test_b.py ⟦suite-repair⟧ ⟦criterion 2⟧"

    code, _, _ = run_cli(module, ["insert", str(ledger), str(branch)])

    assert code == 0
    assert ledger.read_text().split("\n")[2:6] == ["- [x] a ⟦criterion 1⟧", step, "- [ ] b ⟦criterion 2⟧", "- [ ] c ⟦criterion 3⟧"]
    assert (tmp_path / "issue-7-added.md").read_text() == step + "\n"
    logged = [json.loads(line) for line in (tmp_path / "events.jsonl").read_text().splitlines()]
    assert [e["step"] for e in logged if e["event"] == "step-added"] == [step]


def test_insert_with_no_unchecked_step_adds_the_suite_repair_step_after_the_last_done_step_2226(run_cli, tmp_path):
    module = importlib.import_module("veri.suite_red_resume")
    ledger = tmp_path / "issue-7.md"
    ledger.write_text("# Plan for #7\n\n- [x] a ⟦criterion 1⟧\n- [x] b ⟦criterion 2⟧\n")
    (tmp_path / "events.jsonl").write_text(json.dumps({"event": "bail", "cause": "suite-red"}) + "\n")
    branch = tmp_path / "branch-red"
    branch.write_text("test_a.py\n")
    step = "- [ ] fix the full-suite failure: test_a.py ⟦suite-repair⟧ ⟦criterion 2⟧"

    code, _, _ = run_cli(module, ["insert", str(ledger), str(branch)])

    assert code == 0
    assert ledger.read_text().split("\n")[2:5] == ["- [x] a ⟦criterion 1⟧", "- [x] b ⟦criterion 2⟧", step]
    assert (tmp_path / "issue-7-added.md").read_text() == step + "\n"
    logged = [json.loads(line) for line in (tmp_path / "events.jsonl").read_text().splitlines()]
    assert [e["step"] for e in logged if e["event"] == "step-added"] == [step]


def test_check_on_an_empty_branch_red_file_exits_2_naming_that_file_2226(run_cli, tmp_path):
    module = importlib.import_module("veri.suite_red_resume")
    ledger = tmp_path / "issue-7-ledger.md"
    ledger.write_text("- [ ] step\n")
    (tmp_path / "events.jsonl").write_text(json.dumps({"event": "bail", "cause": "suite-red"}) + "\n")
    branch = tmp_path / "branch-red"
    branch.write_text("")
    default = tmp_path / "default-red"
    default.write_text("test_c.py — FAIL c\n")

    code, out, err = run_cli(module, ["check", str(ledger), str(branch), str(default)])

    assert (code, out) == (2, "")
    assert str(branch) in err


def test_insert_on_an_empty_or_unreadable_branch_red_file_exits_2_naming_it_and_adds_no_step_2226(run_cli, tmp_path):
    module = importlib.import_module("veri.suite_red_resume")
    ledger = tmp_path / "issue-7.md"
    ledger.write_text("# Plan for #7\n\n- [x] a ⟦criterion 1⟧\n- [ ] b ⟦criterion 2⟧\n")
    (tmp_path / "events.jsonl").write_text(json.dumps({"event": "bail", "cause": "suite-red"}) + "\n")
    (tmp_path / "issue-7-added.md").write_text("- [ ] earlier ⟦suite-repair⟧\n")
    before = (ledger.read_bytes(), (tmp_path / "issue-7-added.md").read_bytes())
    empty = tmp_path / "branch-red"
    empty.write_text("")
    missing = tmp_path / "no-such-branch-red"

    for branch in (empty, missing):
        code, _, err = run_cli(module, ["insert", str(ledger), str(branch)])

        assert code == 2
        assert str(branch) in err
        assert (ledger.read_bytes(), (tmp_path / "issue-7-added.md").read_bytes()) == before


def test_check_with_an_empty_branch_red_file_and_an_unreadable_default_red_file_exits_2_naming_the_branch_file_2226(run_cli, tmp_path):
    module = importlib.import_module("veri.suite_red_resume")
    ledger = tmp_path / "issue-7-ledger.md"
    ledger.write_text("- [ ] step\n")
    (tmp_path / "events.jsonl").write_text(json.dumps({"event": "bail", "cause": "suite-red"}) + "\n")
    branch = tmp_path / "branch-red"
    branch.write_text("")
    missing = tmp_path / "no-such-default-red"

    code, out, err = run_cli(module, ["check", str(ledger), str(branch), str(missing)])

    assert (code, out) == (2, "")
    assert str(branch) in err
    assert str(missing) not in err
