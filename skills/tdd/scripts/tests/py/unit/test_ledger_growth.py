"""In-process cases for veri/ledger_growth.py, the module ledger-growth.sh is a shim over."""
import importlib

import pytest


@pytest.fixture
def ledger_growth():
    return importlib.import_module("veri.ledger_growth")


def test_2130_a_hand_added_step_line_without_the_added_mark_exits_1_naming_the_line(tmp_path, run_cli, ledger_growth):
    plan = tmp_path / "plan.md"
    ledger = tmp_path / "issue-42.md"
    plan.write_text("# Plan for #42\n\n- [ ] a cog exists ⟦criterion 1⟧\n")
    ledger.write_text(
        "# Plan for #42\n\n"
        "- [x] a cog exists ⟦criterion 1⟧ ⟂ refactor pending\n"
        "- [ ] a sneaked in step ⟦criterion 1⟧\n"
    )
    code, out, err = run_cli(ledger_growth, [str(plan), str(ledger)])
    assert (code, out, "a sneaked in step" in err) == (1, "", True)


def test_2130_ticks_refactor_pending_and_phase_marks_on_planned_lines_exit_0_and_a_missing_argument_or_file_exits_2(
        tmp_path, run_cli, ledger_growth):
    plan = tmp_path / "plan.md"
    ledger = tmp_path / "issue-42.md"
    plan.write_text(
        "# Plan for #42\n\n- [ ] a cog exists ⟦criterion 1⟧\n"
        "- [ ] a wheel turns ⟦phases: expand, migrate⟧ ⟦criterion 2⟧\n")
    ledger.write_text(
        "# Plan for #42\n\n- [x] a cog exists ⟦criterion 1⟧ ⟂ refactor pending\n"
        "- [ ] a wheel turns ⟦phases: expand, migrate⟧ ⟦criterion 2⟧ ⟂ expand done\n")
    unchanged = run_cli(ledger_growth, [str(plan), str(ledger)])
    no_arguments = run_cli(ledger_growth, [])
    unreadable = run_cli(ledger_growth, [str(plan), str(tmp_path / "missing.md")])
    assert (unchanged, no_arguments[0], "usage" in no_arguments[2], unreadable[0]) == (
        (0, "", ""), 2, True, 2)


def test_2130_a_hand_added_step_line_with_the_added_mark_but_no_add_ledger_step_record_exits_1_naming_the_line(
        tmp_path, run_cli, ledger_growth):
    plan = tmp_path / "plan.md"
    ledger = tmp_path / "issue-42.md"
    plan.write_text("# Plan for #42\n\n- [ ] a cog exists ⟦criterion 1⟧\n")
    ledger.write_text(
        "# Plan for #42\n\n"
        "- [x] a cog exists ⟦criterion 1⟧ ⟂ refactor pending\n"
        "- [ ] a hand written step ⟦added⟧ ⟦criterion 1⟧\n"
    )
    (tmp_path / "events.jsonl").write_text(
        '{"ts": 1, "issue": "42", "event": "step-added", "anchor": "a hand written step", "added": "1"}\n')
    code, out, err = run_cli(ledger_growth, [str(plan), str(ledger)])
    assert (code, out, "a hand written step" in err) == (1, "", True)


def test_2130_an_added_step_line_with_its_add_ledger_step_record_exits_0_silently(tmp_path, run_cli, ledger_growth):
    plan = tmp_path / "plan.md"
    ledger = tmp_path / "issue-42.md"
    plan.write_text("# Plan for #42\n\n- [ ] a cog exists ⟦criterion 1⟧\n")
    line = "- [ ] a inserted step ⟦added⟧ ⟦criterion 1⟧"
    ledger.write_text(
        "# Plan for #42\n\n- [x] a cog exists ⟦criterion 1⟧ ⟂ refactor pending\n" + line + "\n")
    (tmp_path / "events.jsonl").write_text(
        '{"event": "step-added", "actor": "add-ledger-step", "step": "' + line + '"}\n')
    assert run_cli(ledger_growth, [str(plan), str(ledger)]) == (0, "", "")
