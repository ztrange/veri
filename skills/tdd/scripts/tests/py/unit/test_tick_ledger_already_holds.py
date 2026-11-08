"""tick-ledger.sh --already-holds: a step whose behaviour already holds is retired without a mutation claim."""
import importlib
import json

import pytest


@pytest.fixture
def tick_ledger():
    return importlib.import_module("veri.tick_ledger")


def test_main_already_holds_retires_the_step_with_an_already_holds_step_event_and_no_mutation_claim_3100(
        tmp_path, run_cli, tick_ledger, monkeypatch):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    ledger.write_text("# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n")
    reason = tmp_path / "reason.txt"
    reason.write_text("REASON: already holds; rerouted to pin step 4\n")

    monkeypatch.setattr(tick_ledger, "run_case", lambda case, *rest, **kw: 0, raising=False)

    code, out, err = run_cli(tick_ledger, ["--already-holds", str(reason), "--case", "tests/py/test_x.py::test_holds",
                              str(ledger), "a one"],
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


def test_main_unpinnable_refuses_an_already_holds_reason_file_and_leaves_ledger_and_events_untouched_3100(
        tmp_path, run_cli, tick_ledger, monkeypatch):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    original = "# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n"
    ledger.write_text(original)
    reason = tmp_path / "reason.txt"
    reason.write_text("REASON: already holds; rerouted to pin step 4\n")

    monkeypatch.setattr(tick_ledger, "run_case", lambda case, *rest, **kw: 0, raising=False)

    code, out, err = run_cli(tick_ledger, ["--unpinnable", str(reason), "--case", "tests/py/test_x.py::test_holds",
                              str(ledger), "a one"],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, ledger.read_text(), (ledger.parent / "events.jsonl").exists()) == (1, original, False), err


def test_main_already_holds_refuses_a_reason_file_with_no_reason_text_and_leaves_ledger_and_events_untouched_3116(
        tmp_path, run_cli, tick_ledger, monkeypatch):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    original = "# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n"
    ledger.write_text(original)
    reason = tmp_path / "reason.txt"
    reason.write_text("REASON:   \n\n")

    monkeypatch.setattr(tick_ledger, "run_case", lambda case, *rest, **kw: 0, raising=False)

    code, out, err = run_cli(tick_ledger, ["--already-holds", str(reason), "--case", "tests/py/test_x.py::test_holds",
                              str(ledger), "a one"],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, ledger.read_text(), (ledger.parent / "events.jsonl").exists()) == (1, original, False), err


def test_main_already_holds_refuses_an_empty_reason_file_and_leaves_ledger_and_events_untouched_3116(
        tmp_path, run_cli, tick_ledger, monkeypatch):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    original = "# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n"
    ledger.write_text(original)
    reason = tmp_path / "reason.txt"
    reason.write_text("")

    monkeypatch.setattr(tick_ledger, "run_case", lambda case, *rest, **kw: 0, raising=False)

    code, out, err = run_cli(tick_ledger, ["--already-holds", str(reason), "--case", "tests/py/test_x.py::test_holds",
                              str(ledger), "a one"],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, ledger.read_text(), (ledger.parent / "events.jsonl").exists()) == (1, original, False), err


def test_main_already_holds_refuses_a_reason_file_with_text_but_no_reason_line_and_leaves_ledger_and_events_untouched_3116(
        tmp_path, run_cli, tick_ledger, monkeypatch):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    original = "# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n"
    ledger.write_text(original)
    reason = tmp_path / "reason.txt"
    reason.write_text("already holds; rerouted to pin step 4\n")

    monkeypatch.setattr(tick_ledger, "run_case", lambda case, *rest, **kw: 0, raising=False)

    code, out, err = run_cli(tick_ledger, ["--already-holds", str(reason), "--case", "tests/py/test_x.py::test_holds",
                              str(ledger), "a one"],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, ledger.read_text(), (ledger.parent / "events.jsonl").exists()) == (1, original, False), err


def test_main_already_holds_event_records_the_first_reason_line_with_text_when_the_first_is_blank_3116(
        tmp_path, run_cli, tick_ledger, monkeypatch):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    ledger.write_text("# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n")
    reason = tmp_path / "reason.txt"
    reason.write_text("REASON:   \nREASON: already holds; rerouted to pin step 4\n")

    monkeypatch.setattr(tick_ledger, "run_case", lambda case, *rest, **kw: 0, raising=False)

    code, out, err = run_cli(tick_ledger, ["--already-holds", str(reason), "--case", "tests/py/test_x.py::test_holds",
                              str(ledger), "a one"],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    events = [json.loads(line) for line in (ledger.parent / "events.jsonl").read_text().splitlines()]
    event = next(e for e in events if e.get("event") == "already-holds-step")
    assert code == 0, err
    assert "- [x] a one" in ledger.read_text()
    assert event["reason"] == "already holds; rerouted to pin step 4", event


def test_main_already_holds_drops_the_mutation_record_whose_tests_case_does_not_exist_3289(
        tmp_path, run_cli, tick_ledger, monkeypatch):
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
    reason.write_text("REASON: already holds; rerouted to pin step 4\n")

    monkeypatch.setattr(tick_ledger, "run_case", lambda case, *rest, **kw: 0, raising=False)

    code, out, err = run_cli(tick_ledger, ["--already-holds", str(reason), "--case", "tests/py/test_x.py::test_holds", str(ledger), "a one"],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, "test_never_written" in record.read_text()) == (0, False), err


def test_main_already_holds_retire_that_drops_a_mutation_record_still_appends_its_already_holds_step_event_3289(
        tmp_path, run_cli, tick_ledger, monkeypatch):
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
    reason.write_text("REASON: already holds; rerouted to pin step 4\n")

    monkeypatch.setattr(tick_ledger, "run_case", lambda case, *rest, **kw: 0, raising=False)

    code, out, err = run_cli(tick_ledger, ["--already-holds", str(reason), "--case", "tests/py/test_x.py::test_holds", str(ledger), "a one"],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    events_file = ledger.parent / "events.jsonl"
    events = [json.loads(line) for line in events_file.read_text().splitlines()] if events_file.exists() else []
    names = [event.get("event") for event in events]
    assert (code, "test_never_written" in record.read_text(), names.count("already-holds-step")) == (0, False, 1), err


def test_main_already_holds_with_a_failing_case_exits_1_leaves_ledger_and_events_and_names_step_and_case_3305(
        tmp_path, run_cli, tick_ledger, monkeypatch):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    before = "# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n"
    ledger.write_text(before)
    reason = tmp_path / "reason.txt"
    reason.write_text("REASON: already holds; rerouted to pin step 4\n")
    ran = []
    monkeypatch.setattr(tick_ledger, "run_case", lambda case, *rest, **kw: ran.append(case) or 1, raising=False)

    code, out, err = run_cli(tick_ledger,
                             ["--already-holds", str(reason), "--case", "tests/py/test_x.py::test_gone",
                              str(ledger), "a one"],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, ledger.read_text(), (ledger.parent / "events.jsonl").exists()) == (1, before, False), err
    assert "a one" in err and "tests/py/test_x.py::test_gone" in err
    assert ran == ["tests/py/test_x.py::test_gone"]


def test_main_already_holds_with_a_passing_case_retires_the_step_with_one_already_holds_step_event_3305(
        tmp_path, run_cli, tick_ledger, monkeypatch):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    ledger.write_text("# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n")
    reason = tmp_path / "reason.txt"
    reason.write_text("REASON: already holds; rerouted to pin step 4\n")
    ran = []
    monkeypatch.setattr(tick_ledger, "run_case", lambda case, *rest, **kw: ran.append(case) or 0, raising=False)

    code, out, err = run_cli(tick_ledger,
                             ["--already-holds", str(reason), "--case", "tests/py/test_x.py::test_holds",
                              str(ledger), "a one"],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    events = [json.loads(line) for line in (ledger.parent / "events.jsonl").read_text().splitlines()]
    assert (code, ledger.read_text()) == (
        0, "# Plan for #42\n\n- [x] a one ⟦criterion 1⟧ ⟂ retired already holds\n- [ ] b two ⟦criterion 2⟧\n"), err
    assert [e.get("event") for e in events].count("already-holds-step") == 1
    assert ran == ["tests/py/test_x.py::test_holds"]


def test_main_already_holds_with_no_case_exits_1_leaves_ledger_and_events_and_says_no_case_is_named_3305(
        tmp_path, run_cli, tick_ledger):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    before = "# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n"
    ledger.write_text(before)
    reason = tmp_path / "reason.txt"
    reason.write_text("REASON: already holds; rerouted to pin step 4\n")

    code, out, err = run_cli(tick_ledger, ["--already-holds", str(reason), str(ledger), "a one"],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, ledger.read_text(), (ledger.parent / "events.jsonl").exists()) == (1, before, False), err
    assert "a one" in err and "no case" in err
