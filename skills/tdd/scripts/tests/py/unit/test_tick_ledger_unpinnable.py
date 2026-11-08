"""tick-ledger.sh --unpinnable: a step verify-pin calls unpinnable is retired, not revised."""
import importlib
import json

import pytest


@pytest.fixture
def tick_ledger():
    return importlib.import_module("veri.tick_ledger")


def test_main_unpinnable_retires_the_matched_step_with_an_unpinnable_step_event_and_no_revise_event_2999(
        tmp_path, run_cli, tick_ledger):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    ledger.write_text("# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n")
    reason = tmp_path / "reason.txt"
    reason.write_text("VERDICT: REJECT\nREASON: the hand mutation stays green\n")

    code, out, err = run_cli(tick_ledger, ["--unpinnable", str(reason), str(ledger), "a one"],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    events_file = ledger.parent / "events.jsonl"
    events = [json.loads(line) for line in events_file.read_text().splitlines()] if events_file.exists() else []
    assert (code, ledger.read_text()) == (
        0, "# Plan for #42\n\n- [x] a one ⟦criterion 1⟧ ⟂ retired unpinnable\n- [ ] b two ⟦criterion 2⟧\n"), err
    names = [event.get("event") for event in events]
    assert names.count("unpinnable-step") == 1 and "revise" not in names
    event = events[names.index("unpinnable-step")]
    assert "a one" in json.dumps(event, ensure_ascii=False) and "stays green" in json.dumps(event)


def test_main_unpinnable_with_any_other_reject_reason_exits_1_and_leaves_ledger_and_events_unchanged_2999(
        tmp_path, run_cli, tick_ledger):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    before = "# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n"
    ledger.write_text(before)
    reason = tmp_path / "reason.txt"
    reason.write_text("VERDICT: REJECT\nREASON: the test is trivial and over-coupled to the wording\n")

    code, out, err = run_cli(tick_ledger, ["--unpinnable", str(reason), str(ledger), "a one"],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, ledger.read_text(), (ledger.parent / "events.jsonl").exists()) == (1, before, False), err


def test_main_unpinnable_drops_the_mutation_record_whose_tests_case_does_not_exist_3289(
        tmp_path, run_cli, tick_ledger):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    ledger.write_text("# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n")
    suite = tmp_path / "tests" / "test_thing.py"
    suite.parent.mkdir()
    suite.write_text("def test_other():\n    pass\n")
    command = "make test TESTS=tests/test_thing.py::test_never_written"
    record = ledger.parent / "issue-42-mutations.md"
    record.write_text(
        "file 8\nthing.py\nold 3\nold\nnew 3\nnew\n"
        f"command {len(command)}\n{command}\n\n")
    reason = tmp_path / "reason.txt"
    reason.write_text("VERDICT: REJECT\nREASON: the hand mutation stays green\n")

    code, out, err = run_cli(tick_ledger, ["--unpinnable", str(reason), str(ledger), "a one"],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, "test_never_written" in record.read_text()) == (0, False), err
