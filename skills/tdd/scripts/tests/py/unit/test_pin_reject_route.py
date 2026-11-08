"""pin-reject-route.sh: a verify-pin REJECT saying the mutation stays green is retired by script."""
import importlib
import json

import pytest


@pytest.fixture
def pin_reject_route():
    return importlib.import_module("veri.pin_reject_route")


def test_main_stays_green_reject_retires_the_step_unpinnable_with_no_revise_event_3300(
        tmp_path, run_cli, pin_reject_route):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    ledger.write_text("# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n")
    reason = tmp_path / "reason.txt"
    reason.write_text("VERDICT: REJECT\nREASON: the mutation (< 2 to < 1) stays green\n")

    code, out, err = run_cli(pin_reject_route, [str(reason), str(ledger), "a one"],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    events_file = ledger.parent / "events.jsonl"
    events = [json.loads(line) for line in events_file.read_text().splitlines()] if events_file.exists() else []
    names = [e.get("event") for e in events]
    assert (code, out.strip(), ledger.read_text(), names.count("unpinnable-step"), "revise" in names) == (
        0, "retired",
        "# Plan for #42\n\n- [x] a one ⟦criterion 1⟧ ⟂ retired unpinnable\n- [ ] b two ⟦criterion 2⟧\n",
        1, False), err


def test_main_usage_on_too_few_arguments_and_nonzero_unpinnable_exit_passes_through_without_retired_3300(
        tmp_path, run_cli, pin_reject_route):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    ledger.write_text("# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n")
    reason = tmp_path / "reason.txt"
    reason.write_text("VERDICT: REJECT\nREASON: the mutation (< 2 to < 1) stays green\n")

    few = run_cli(pin_reject_route, [str(reason), str(ledger)], env={"VERI_ISSUE": "42"}, cwd=tmp_path)
    none = run_cli(pin_reject_route, [str(reason), str(ledger), "no such step"],
                   env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (few[0], few[1], "usage" in few[2].lower(), none[0], "retired" in none[1]) == (
        2, "", True, 3, False), (few, none)


def test_main_reject_not_saying_stays_green_prints_revise_and_leaves_ledger_and_events_untouched_3300(
        tmp_path, run_cli, pin_reject_route):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    body = "# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n"
    ledger.write_text(body)
    reason = tmp_path / "reason.txt"
    reason.write_text("VERDICT: REJECT\nREASON: the test is over-coupled to the implementation\n")

    code, out, err = run_cli(pin_reject_route, [str(reason), str(ledger), "a one"],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, out.strip(), ledger.read_text(), (ledger.parent / "events.jsonl").exists()) == (
        1, "revise", body, False), err
