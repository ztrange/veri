"""pin-reject-route.sh: a verify-pin REJECT saying the mutation stays green is retired by script."""
import importlib
import json

import pytest


@pytest.fixture
def pin_reject_route():
    return importlib.import_module("veri.pin_reject_route")


TARGET = "tests/py/test_x.py::test_holds"


@pytest.fixture(autouse=True)
def passing_case(pin_reject_route, monkeypatch):
    monkeypatch.setattr(pin_reject_route.tick_ledger, "run_case", lambda case, *rest, **kw: 0)


def test_main_stays_green_reject_retires_the_step_unpinnable_with_no_revise_event_3300(
        tmp_path, run_cli, pin_reject_route):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    ledger.write_text("# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n")
    reason = tmp_path / "reason.txt"
    reason.write_text("VERDICT: REJECT\nREASON: the mutation (< 2 to < 1) stays green\n")

    code, out, err = run_cli(pin_reject_route, [str(reason), str(ledger), "a one", TARGET],
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
    none = run_cli(pin_reject_route, [str(reason), str(ledger), "no such step", TARGET],
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

    code, out, err = run_cli(pin_reject_route, [str(reason), str(ledger), "a one", TARGET],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, out.strip(), ledger.read_text(), (ledger.parent / "events.jsonl").exists()) == (
        1, "revise", body, False), err


def test_main_missing_reroute_reject_not_saying_stays_green_retires_the_step_already_holds_3300(
        tmp_path, run_cli, pin_reject_route):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    ledger.write_text("# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n")
    reason = tmp_path / "reason.txt"
    reason.write_text("VERDICT: REJECT\nREASON: the behaviour is already covered by an earlier step\n")

    code, out, err = run_cli(pin_reject_route, ["--missing-reroute", str(reason), str(ledger), "a one", TARGET],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    events_file = ledger.parent / "events.jsonl"
    events = [json.loads(line) for line in events_file.read_text().splitlines()] if events_file.exists() else []
    names = [e.get("event") for e in events]
    assert (code, out.strip(), ledger.read_text(), names.count("already-holds-step"), "revise" in names) == (
        0, "retired",
        "# Plan for #42\n\n- [x] a one ⟦criterion 1⟧ ⟂ retired already holds\n- [ ] b two ⟦criterion 2⟧\n",
        1, False), err


def test_main_missing_reroute_reject_saying_stays_green_exits_2_and_ticks_nothing_3300(
        tmp_path, run_cli, pin_reject_route):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    ledger.write_text("# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n")
    reason = tmp_path / "reason.txt"
    reason.write_text("VERDICT: REJECT\nREASON: the real before-state stays green\n")

    code, out, err = run_cli(pin_reject_route, ["--missing-reroute", str(reason), str(ledger), "a one", TARGET],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, "retired" in out, ledger.read_text()) == (
        2, False,
        "# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n"), err


def test_main_missing_reroute_stays_green_matching_no_open_step_exits_3_and_writes_nothing_3343(
        tmp_path, run_cli, pin_reject_route):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    body = "# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n"
    ledger.write_text(body)
    reason = tmp_path / "reason.txt"
    reason.write_text("VERDICT: REJECT\nREASON: the real before-state stays green\n")

    code, out, err = run_cli(pin_reject_route, ["--missing-reroute", str(reason), str(ledger), "no such step", TARGET],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, out, ledger.read_text(), (ledger.parent / "events.jsonl").exists()) == (3, "", body, False), err


def test_main_no_argument_usage_line_names_the_missing_reroute_flag_3300(run_cli, pin_reject_route):
    code, out, err = run_cli(pin_reject_route, [])

    assert (code, out, "[--missing-reroute]" in err) == (2, "", True), err


def test_main_missing_reroute_with_fewer_than_four_arguments_exits_2_printing_usage_only_3472(
        tmp_path, run_cli, pin_reject_route):
    reason = tmp_path / "reason.txt"
    reason.write_text("VERDICT: REJECT\nREASON: the mutation stays green\n")

    code, out, err = run_cli(pin_reject_route, ["--missing-reroute", str(reason), str(tmp_path / "l.md"), "a one"])

    assert (code, out, "usage:" in err) == (2, "", True), err


def test_main_unpinnable_no_answer_exit_2_passes_through_and_prints_no_revise_3300(
        tmp_path, run_cli, pin_reject_route, monkeypatch):
    monkeypatch.setattr(pin_reject_route.tick_ledger, "main", lambda argv: 2)

    code, out, err = run_cli(pin_reject_route, [str(tmp_path / "r.txt"), str(tmp_path / "l.md"), "a one", TARGET])

    assert (code, "revise" in out) == (2, False), (out, err)


def test_main_unpinnable_no_step_matched_exit_3_passes_through_and_prints_no_revise_3300(
        tmp_path, run_cli, pin_reject_route, monkeypatch):
    monkeypatch.setattr(pin_reject_route.tick_ledger, "main", lambda argv: 3)

    code, out, err = run_cli(pin_reject_route, [str(tmp_path / "r.txt"), str(tmp_path / "l.md"), "a one", TARGET])

    assert (code, "revise" in out) == (3, False), (out, err)


def test_main_missing_reroute_stays_green_records_one_unpinnable_missing_event_and_leaves_ledger_untouched_3343(
        tmp_path, run_cli, pin_reject_route):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    body = "# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n"
    ledger.write_text(body)
    ledger_bytes = ledger.read_bytes()
    reason = tmp_path / "reason.txt"
    reason.write_text("VERDICT: REJECT\nREASON: the real before-state stays green\n")

    code, out, err = run_cli(pin_reject_route, ["--missing-reroute", str(reason), str(ledger), "a one", TARGET],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    events_file = ledger.parent / "events.jsonl"
    events = [json.loads(line) for line in events_file.read_text().splitlines()] if events_file.exists() else []
    names = [e.get("event") for e in events]
    missing = [e for e in events if e.get("event") == "unpinnable-missing"]
    assert (names.count("unpinnable-missing"), [e.get("step") for e in missing],
            [n for n in names if n in ("unpinnable-step", "already-holds-step", "revise")],
            ledger.read_bytes()) == (1, ["a one ⟦criterion 1⟧"], [], ledger_bytes), (code, out, err, names)


def test_main_missing_reroute_stays_green_prints_unpinnable_missing_and_exits_2_with_one_event_3472(
        tmp_path, run_cli, pin_reject_route):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    body = "# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n"
    ledger.write_text(body)
    ledger_bytes = ledger.read_bytes()
    reason = tmp_path / "reason.txt"
    reason.write_text("VERDICT: REJECT\nREASON: the real before-state stays green\n")

    code, out, err = run_cli(pin_reject_route, ["--missing-reroute", str(reason), str(ledger), "a one", TARGET],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    events_file = ledger.parent / "events.jsonl"
    events = [json.loads(line) for line in events_file.read_text().splitlines()] if events_file.exists() else []
    names = [e.get("event") for e in events]
    assert (code, out.strip(), names.count("unpinnable-missing"), ledger.read_bytes()) == (
        2, "unpinnable-missing", 1, ledger_bytes), err


@pytest.mark.parametrize("unpinnable_clause", [
    "the before-state is green",
    "the before-state case passes",
    "on the before-state the case passes",
    "the case passes on the before-state",
    "green on the before-state",
    "the case is green on the before-state",
])
def test_main_missing_reroute_every_before_state_green_wording_routes_unpinnable_missing_3458(
        tmp_path, run_cli, pin_reject_route, unpinnable_clause):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    ledger.write_text("# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n")
    reason = tmp_path / "reason.txt"
    reason.write_text("VERDICT: REJECT\nREASON: the mutation stays green. " + unpinnable_clause + "\n")

    code, out, err = run_cli(pin_reject_route, ["--missing-reroute", str(reason), str(ledger), "a one", TARGET],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, out.strip()) == (2, "unpinnable-missing"), err


def test_main_stays_green_reject_with_failing_target_test_prints_revise_and_leaves_line_unticked_3305(
        tmp_path, run_cli, pin_reject_route, monkeypatch):
    ran = []
    monkeypatch.setattr(pin_reject_route.tick_ledger, "run_case", lambda case, *rest, **kw: ran.append(case) or 1)
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    body = "# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n"
    ledger.write_text(body)
    reason = tmp_path / "reason.txt"
    reason.write_text("VERDICT: REJECT\nREASON: the mutation (< 2 to < 1) stays green\n")

    code, out, err = run_cli(pin_reject_route, [str(reason), str(ledger), "a one", TARGET],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, out.strip(), ran, ledger.read_text(), (ledger.parent / "events.jsonl").exists()) == (
        1, "revise", [TARGET], body, False), err


def test_main_missing_reroute_already_holds_fallback_runs_the_target_test_and_retires_the_step_3305(
        tmp_path, run_cli, pin_reject_route, monkeypatch):
    ran = []
    monkeypatch.setattr(pin_reject_route.tick_ledger, "run_case", lambda case, *rest, **kw: ran.append(case) or 0)
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    ledger.write_text("# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n")
    reason = tmp_path / "reason.txt"
    reason.write_text("VERDICT: REJECT\nREASON: the behaviour is already covered by an earlier step\n")

    code, out, err = run_cli(pin_reject_route, ["--missing-reroute", str(reason), str(ledger), "a one", TARGET],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, out.strip(), ledger.read_text(), ran) == (
        0, "retired",
        "# Plan for #42\n\n- [x] a one ⟦criterion 1⟧ ⟂ retired already holds\n- [ ] b two ⟦criterion 2⟧\n",
        [TARGET]), err


def test_main_target_test_missing_exits_2_with_usage_naming_it_and_leaves_ledger_untouched_3305(
        tmp_path, run_cli, pin_reject_route):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    body = "# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n"
    ledger.write_text(body)
    reason = tmp_path / "reason.txt"
    reason.write_text("VERDICT: REJECT\nREASON: the mutation (< 2 to < 1) stays green\n")

    code, out, err = run_cli(pin_reject_route, [str(reason), str(ledger), "a one"],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, out, "usage" in err.lower() and "<target-test>" in err, ledger.read_text(),
            (ledger.parent / "events.jsonl").exists()) == (2, "", True, body, False), err


def test_main_missing_reroute_bare_name_case_whose_command_fails_in_setup_prints_nothing_exits_2_and_spends_no_revise_3425(
        tmp_path, run_cli, pin_reject_route, monkeypatch):
    import subprocess

    monkeypatch.undo()
    ledger = tmp_path / ".tdd" / "issue-99.md"
    ledger.parent.mkdir()
    body = "# Plan for #99\n\n- [ ] a one ⟦criterion 4⟧\n- [ ] b two ⟦criterion 5⟧\n"
    ledger.write_text(body)
    reason = tmp_path / "reason.txt"
    reason.write_text("VERDICT: REJECT\nREASON: the behaviour is already covered by an earlier step\n")
    bare = "TestIssue99CheckExitsZero"
    setup_error = f"stat {tmp_path}/{bare}: directory not found\nFAIL {bare} [setup failed]\n"

    def fake_run(argv, *args, **kwargs):
        text = bool(kwargs.get("text") or kwargs.get("universal_newlines"))
        if str(argv[0]).endswith("detect-test-command.sh"):
            out = 'go test "$1"\n'
            return subprocess.CompletedProcess(argv, 0, stdout=out if text else out.encode(), stderr="" if text else b"")
        return subprocess.CompletedProcess(argv, 1, stdout="" if text else b"",
                                           stderr=setup_error if text else setup_error.encode())

    monkeypatch.setattr(pin_reject_route.tick_ledger.subprocess, "run", fake_run)

    code, out, err = run_cli(pin_reject_route, ["--missing-reroute", str(reason), str(ledger), "a one", bare],
                             env={"VERI_ISSUE": "99"}, cwd=tmp_path)

    assert (code, out.strip(), ledger.read_text(), (ledger.parent / "events.jsonl").exists()) == (
        2, "", body, False), err


def test_main_missing_reroute_surviving_mutant_reason_prints_revise_exits_1_and_leaves_ledger_and_events_untouched_3458(
        tmp_path, run_cli, pin_reject_route):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    body = "# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n"
    ledger.write_text(body)
    reason = tmp_path / "reason.txt"
    reason.write_text("VERDICT: REJECT\nREASON: the mutation (a-z to a-y) stays green\n")

    code, out, err = run_cli(pin_reject_route, ["--missing-reroute", str(reason), str(ledger), "a one", TARGET],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, out.strip(), ledger.read_bytes(), (ledger.parent / "events.jsonl").exists()) == (
        1, "revise", body.encode(), False), err


def test_main_missing_reroute_hand_mutation_stays_green_reason_prints_revise_exits_1_and_leaves_ledger_and_events_untouched_3458(
        tmp_path, run_cli, pin_reject_route):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    body = "# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n"
    ledger.write_text(body)
    reason = tmp_path / "reason.txt"
    reason.write_text("VERDICT: REJECT\nREASON: the hand mutation stays green\n")

    code, out, err = run_cli(pin_reject_route, ["--missing-reroute", str(reason), str(ledger), "a one", TARGET],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, out.strip(), ledger.read_bytes(), (ledger.parent / "events.jsonl").exists()) == (
        1, "revise", body.encode(), False), err


def test_main_missing_reroute_target_red_on_before_state_but_mutant_stays_green_prints_revise_exits_1_and_leaves_ledger_and_events_untouched_3458(
        tmp_path, run_cli, pin_reject_route):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    body = "# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n"
    ledger.write_text(body)
    reason = tmp_path / "reason.txt"
    reason.write_text("VERDICT: REJECT\nREASON: the target is red on the before-state, but the mutation (a-z to a-y) stays green\n")

    code, out, err = run_cli(pin_reject_route, ["--missing-reroute", str(reason), str(ledger), "a one", TARGET],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, out.strip(), ledger.read_bytes(), (ledger.parent / "events.jsonl").exists()) == (
        1, "revise", body.encode(), False), err


def test_main_missing_reroute_before_state_green_without_stays_green_is_retired_already_holds_not_unpinnable_missing_3458(
        tmp_path, run_cli, pin_reject_route):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    body = "# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n"
    ledger.write_text(body)
    reason = tmp_path / "reason.txt"
    reason.write_text("VERDICT: REJECT\nREASON: the case is green on the before-state\n")

    code, out, err = run_cli(pin_reject_route, ["--missing-reroute", str(reason), str(ledger), "a one", TARGET],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, out.strip(), ledger.read_text()) == (
        0, "retired",
        "# Plan for #42\n\n- [x] a one ⟦criterion 1⟧ ⟂ retired already holds\n- [ ] b two ⟦criterion 2⟧\n"), err


@pytest.mark.parametrize("reason_text", [
    pytest.param("the target is red on the before-state. The mutant stays green", id="alt1-period"),
    pytest.param("the target is red on the before-state\nthe mutant stays green", id="alt1-newline"),
    pytest.param("the target is red on the before-state, but the mutant stays green", id="alt1-comma"),
    pytest.param("the target is red on the before-state; the mutant stays green", id="alt1-semicolon"),
    pytest.param("the before-state is evergreen, the mutant stays green", id="alt1-word-boundary-green"),
    pytest.param("the before-state is a bypass, the mutant stays green", id="alt1-word-boundary-pass"),
    pytest.param("the mutant stays green. The target is red on the before-state", id="alt2-period"),
    pytest.param("the mutant stays green\nthe target is red on the before-state", id="alt2-newline"),
    pytest.param("the mutant stays green, but the target is red on the before-state", id="alt2-comma"),
    pytest.param("the mutant stays green; the target is red on the before-state", id="alt2-semicolon"),
    pytest.param("the mutant stays green; we bypass the before-state", id="alt2-word-boundary-pass"),
    pytest.param("the mutant stays green; the evergreen case on the before-state", id="alt2-word-boundary-green"),
])
def test_main_missing_reroute_before_state_and_green_in_different_clauses_prints_revise_not_unpinnable_missing_3458(
        tmp_path, run_cli, pin_reject_route, reason_text):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    body = "# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n"
    ledger.write_text(body)
    reason = tmp_path / "reason.txt"
    reason.write_text("VERDICT: REJECT\nREASON: " + reason_text + "\n")

    code, out, err = run_cli(pin_reject_route, ["--missing-reroute", str(reason), str(ledger), "a one", TARGET],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, out.strip(), ledger.read_bytes(), (ledger.parent / "events.jsonl").exists()) == (
        1, "revise", body.encode(), False), err


def test_main_recheck_stayed_green_pin_inserts_a_diff_checked_repin_step_after_the_ticked_step_3469(
        tmp_path, run_cli, pin_reject_route):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    ledger.write_text("# Plan for #42\n\n- [x] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n")
    reason = tmp_path / "reason.txt"
    reason.write_text("pin stayed green under its mutation: tests/py/test_review.py\n")

    code, out, err = run_cli(pin_reject_route, ["--recheck", str(reason), str(ledger), "a one"],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    lines = ledger.read_text().split("\n")
    at = next(i for i, line in enumerate(lines) if "a one" in line)
    inserted = lines[at + 1]
    added_file = ledger.parent / "issue-42-added.md"
    added = added_file.read_text() if added_file.exists() else ""
    assert (code, out.strip(), "⟦diff-checked⟧" in inserted, "⟦added⟧" in inserted,
            "tests/py/test_review.py" in inserted, "tests/py/test_review.py" in added) == (
        0, "repin tests/py/test_review.py", True, True, True, True), (err, lines)


def test_main_recheck_before_state_pin_disarmed_by_the_range_inserts_a_diff_checked_repin_step_3469(
        tmp_path, run_cli, pin_reject_route):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    ledger.write_text("# Plan for #42\n\n- [x] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n")
    reason = tmp_path / "reason.txt"
    reason.write_text("pin stayed green on the before-state: tests/py/test_review.py\n")

    code, out, err = run_cli(pin_reject_route, ["--recheck", str(reason), str(ledger), "a one"],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    lines = ledger.read_text().split("\n")
    at = next(i for i, line in enumerate(lines) if "a one" in line)
    inserted = lines[at + 1]
    added_file = ledger.parent / "issue-42-added.md"
    added = added_file.read_text() if added_file.exists() else ""
    assert (code, out.strip(), "⟦diff-checked⟧" in inserted, "⟦added⟧" in inserted,
            "tests/py/test_review.py" in inserted, "tests/py/test_review.py" in added) == (
        0, "repin tests/py/test_review.py", True, True, True, True), (err, lines)


def test_main_recheck_reason_with_no_disarm_line_prints_revise_and_leaves_ledger_and_added_record_untouched_3469(
        tmp_path, run_cli, pin_reject_route):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    body = "# Plan for #42\n\n- [x] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n"
    ledger.write_text(body)
    reason = tmp_path / "reason.txt"
    reason.write_text("needs a look: tests/py/test_review.py\n")

    code, out, err = run_cli(pin_reject_route, ["--recheck", str(reason), str(ledger), "a one"],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, out.strip(), ledger.read_text(), (ledger.parent / "issue-42-added.md").exists()) == (
        1, "revise", body, False), err


def test_main_recheck_pin_whose_file_already_has_a_checked_repin_step_prints_repin_failed_adds_no_step_and_exits_1_3469(
        tmp_path, run_cli, pin_reject_route):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    body = ("# Plan for #42\n\n- [x] a one ⟦criterion 1⟧\n"
            "- [x] ⟦diff-checked⟧ edit the case of the pin on tests/py/test_review.py"
            " so its recorded mutation turns it red ⟦added⟧\n"
            "- [ ] b two ⟦criterion 2⟧\n")
    ledger.write_text(body)
    reason = tmp_path / "reason.txt"
    reason.write_text("pin stayed green under its mutation: tests/py/test_review.py\n")

    code, out, err = run_cli(pin_reject_route, ["--recheck", str(reason), str(ledger), "a one"],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, out.strip(), ledger.read_text(), (ledger.parent / "issue-42-added.md").exists()) == (
        1, "repin-failed tests/py/test_review.py", body, False), err
