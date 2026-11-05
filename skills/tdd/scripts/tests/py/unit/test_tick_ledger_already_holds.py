"""tick-ledger.sh --already-holds: a step whose behaviour already holds is retired without a mutation claim."""
import importlib
import json

import pytest


@pytest.fixture
def tick_ledger():
    return importlib.import_module("veri.tick_ledger")


def test_main_already_holds_retires_the_step_with_an_already_holds_step_event_and_no_mutation_claim_3100(
        tmp_path, run_cli, tick_ledger):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    ledger.write_text("# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n")
    reason = tmp_path / "reason.txt"
    reason.write_text("REASON: already holds; rerouted to pin step 4\n")

    code, out, err = run_cli(tick_ledger, ["--already-holds", str(reason), str(ledger), "a one"],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    events_file = ledger.parent / "events.jsonl"
    events = [json.loads(line) for line in events_file.read_text().splitlines()] if events_file.exists() else []
    assert (code, ledger.read_text()) == (
        0, "# Plan for #42\n\n- [x] a one ⟦criterion 1⟧ ⟂ retired already holds\n- [ ] b two ⟦criterion 2⟧\n"), err
    names = [event.get("event") for event in events]
    assert names.count("already-holds-step") == 1
    assert "unpinnable-step" not in names and "revise" not in names
    event = events[names.index("already-holds-step")]
    dumped = json.dumps(event, ensure_ascii=False)
    assert "a one" in dumped and "already holds; rerouted to pin step 4" in dumped
    assert "stays green" not in dumped and "mutation" not in dumped
