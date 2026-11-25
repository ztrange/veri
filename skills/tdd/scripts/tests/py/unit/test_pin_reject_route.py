"""pin-reject-route.sh: a verify-pin REJECT saying the mutation stays green is retired by script."""
import importlib
import json

import pytest


def plan_commit(ledger_text):
    """git's answers naming the plan commit add-ledger-step.sh reads the verified plan's steps from."""
    return {"git log --format=%H %s": (0, "beef plan: scope #42 into 2 steps (#42)\n", ""),
            "git show beef:./issue-42.md": (0, ledger_text, "")}


@pytest.fixture
def pin_reject_route():
    return importlib.import_module("veri.pin_reject_route")


TARGET = "tests/py/test_x.py::test_holds"


@pytest.fixture(autouse=True)
def passing_case(pin_reject_route, monkeypatch):
    monkeypatch.setattr(pin_reject_route.tick_ledger, "run_case", lambda case, *rest, **kw: (0, "", 0))


@pytest.fixture(autouse=True)
def clean_tree(pin_reject_route, monkeypatch):
    """A retire lists the test files differing from HEAD through git: a work tree with none, unless a case says otherwise."""
    import subprocess
    monkeypatch.setattr(pin_reject_route.tick_ledger.git, "git", lambda *args, **kw: subprocess.CompletedProcess(["git", *args], 0, b"", b""))


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
    monkeypatch.setattr(pin_reject_route.tick_ledger, "tick", lambda *args, **kw: 2)

    code, out, err = run_cli(pin_reject_route, [str(tmp_path / "r.txt"), str(tmp_path / "l.md"), "a one", TARGET])

    assert (code, "revise" in out) == (2, False), (out, err)


def test_main_unpinnable_no_step_matched_exit_3_passes_through_and_prints_no_revise_3300(
        tmp_path, run_cli, pin_reject_route, monkeypatch):
    monkeypatch.setattr(pin_reject_route.tick_ledger, "tick", lambda *args, **kw: 3)

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
    monkeypatch.setattr(pin_reject_route.tick_ledger, "run_case", lambda case, *rest, **kw: (ran.append(case) or 1, "", 1))
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
    monkeypatch.setattr(pin_reject_route.tick_ledger, "run_case", lambda case, *rest, **kw: (ran.append(case) or 0, "", 0))
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
        tmp_path, run_cli, pin_reject_route, monkeypatch, fake_processes):
    monkeypatch.undo()
    ledger = tmp_path / ".tdd" / "issue-99.md"
    ledger.parent.mkdir()
    body = "# Plan for #99\n\n- [ ] a one ⟦criterion 4⟧\n- [ ] b two ⟦criterion 5⟧\n"
    ledger.write_text(body)
    reason = tmp_path / "reason.txt"
    reason.write_text("VERDICT: REJECT\nREASON: the behaviour is already covered by an earlier step\n")
    bare = "TestIssue99CheckExitsZero"
    setup_error = f"stat {tmp_path}/{bare}: directory not found\nFAIL {bare} [setup failed]\n"

    fake_processes.answers({"detect-test-command.sh": (0, 'go test "$1"\n', ""), "": (1, "", setup_error)})

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


def test_main_missing_reroute_before_state_green_without_stays_green_routes_unpinnable_missing_3644(
        tmp_path, run_cli, pin_reject_route):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    body = "# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n"
    ledger.write_text(body)
    reason = tmp_path / "reason.txt"
    reason.write_text("VERDICT: REJECT\nREASON: still passes against the real before-state; "
                      "pins nothing the branch introduced\n")

    code, out, err = run_cli(pin_reject_route, ["--missing-reroute", str(reason), str(ledger), "a one", TARGET],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, out.strip(), ledger.read_text()) == (2, "unpinnable-missing", body), err


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


def test_main_before_state_green_reject_without_stays_green_retires_the_step_unpinnable_3644(
        tmp_path, run_cli, pin_reject_route):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    ledger.write_text("# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n")
    reason = tmp_path / "reason.txt"
    reason.write_text("VERDICT: REJECT\nREASON: still passes against the real before-state; "
                      "pins nothing the branch introduced\n")

    code, out, err = run_cli(pin_reject_route, [str(reason), str(ledger), "a one", TARGET],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, out.strip(), ledger.read_text()) == (
        0, "retired",
        "# Plan for #42\n\n- [x] a one ⟦criterion 1⟧ ⟂ retired unpinnable\n- [ ] b two ⟦criterion 2⟧\n"), err


def test_main_reject_saying_only_the_case_passes_naming_no_before_state_or_mutation_prints_revise_and_leaves_ledger_and_events_untouched_3644(
        tmp_path, run_cli, pin_reject_route):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    body = "# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n"
    ledger.write_text(body)
    reason = tmp_path / "reason.txt"
    reason.write_text("VERDICT: REJECT\nREASON: the target case passes\n")

    code, out, err = run_cli(pin_reject_route, [str(reason), str(ledger), "a one", TARGET],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, out.strip(), ledger.read_text(), (ledger.parent / "events.jsonl").exists()) == (
        1, "revise", body, False), err


@pytest.mark.parametrize("flags", [[], ["--missing-reroute"]])
def test_main_reject_saying_the_case_fails_on_the_before_state_and_passes_after_is_not_before_state_green_3644(
        tmp_path, run_cli, pin_reject_route, flags):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    body = "# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n"
    ledger.write_text(body)
    reason = tmp_path / "reason.txt"
    reason.write_text("VERDICT: REJECT\nREASON: the case fails on the before-state and passes after the change\n")

    code, out, err = run_cli(pin_reject_route, flags + [str(reason), str(ledger), "a one", TARGET],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    events = ledger.parent / "events.jsonl"
    text = events.read_text() if events.exists() else ""
    assert (out.strip() != "unpinnable-missing", "unpinnable-step" in text) == (True, False), err
    if not flags:
        assert (code, out.strip(), ledger.read_text()) == (1, "revise", body), err


@pytest.mark.parametrize("reason_text", [
    "the case is red on the before-state and green once the change lands",
    "the case does not pass on the before-state",
    "the case doesn't pass on the before-state",
    "after the change the case passes on the before-state",
], ids=["red", "not", "n't", "after"])
def test_main_reject_with_each_before_state_green_exclusion_word_is_not_before_state_green_3644(
        tmp_path, run_cli, pin_reject_route, reason_text):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    body = "# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n"
    ledger.write_text(body)
    reason = tmp_path / "reason.txt"
    reason.write_text(f"VERDICT: REJECT\nREASON: {reason_text}\n")

    code, out, err = run_cli(pin_reject_route, [str(reason), str(ledger), "a one", TARGET],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    events = ledger.parent / "events.jsonl"
    text = events.read_text() if events.exists() else ""
    assert (code, out.strip(), ledger.read_text(), "unpinnable-step" in text) == (
        1, "revise", body, False), err


def test_main_on_a_case_that_never_ran_exits_2_with_nothing_on_stdout_and_names_the_command_that_was_run_on_stderr_3617(
        tmp_path, run_cli, pin_reject_route, monkeypatch, fake_processes):
    monkeypatch.undo()
    ledger = tmp_path / ".tdd" / "issue-99.md"
    ledger.parent.mkdir()
    ledger.write_text("# Plan for #99\n\n- [ ] a one ⟦criterion 4⟧\n")
    reason = tmp_path / "reason.txt"
    reason.write_text("VERDICT: REJECT\nREASON: the mutation (< 2 to < 1) stays green\n")
    case = str(tmp_path / "gone" / "test_missing.py")

    fake_processes.answers({"detect-test-command.sh": (0, "stub-case-command --flag\n", ""),
                            "": (4, "", "ERROR: file or directory not found\n")})

    code, out, err = run_cli(pin_reject_route, [str(reason), str(ledger), "a one", case],
                             env={"VERI_ISSUE": "99"}, cwd=tmp_path)

    assert (code, out, f"case {case} never run" in err, "stub-case-command --flag" in err) == (2, "", True, True), err


def test_main_bare_target_test_name_runs_the_case_in_the_red_reports_test_path_file_4549(
        tmp_path, run_cli, pin_reject_route, monkeypatch):
    ran = []
    monkeypatch.setattr(pin_reject_route.tick_ledger, "run_case", lambda case, *rest, **kw: (ran.append(case) or 0, "", 0))
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    ledger.write_text("# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_x.py").write_text("def test_holds():\n    assert True\n")
    (ledger.parent / "develop-red.out").write_text(
        "TEST_PATH: tests/test_x.py\nTARGET_TEST: test_holds\nFAIL_OUTPUT: x\n")
    reason = tmp_path / "reason.txt"
    reason.write_text("VERDICT: REJECT\nREASON: the mutation (< 2 to < 1) stays green\n")

    code, out, err = run_cli(pin_reject_route, [str(reason), str(ledger), "a one", "test_holds"],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, out.strip(), ran) == (0, "retired", ["tests/test_x.py::test_holds"]), err


def test_main_bare_target_test_name_the_red_reports_test_path_file_does_not_hold_exits_2_and_ticks_nothing_4549(
        tmp_path, run_cli, pin_reject_route, monkeypatch, fake_processes):
    monkeypatch.undo()
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    body = "# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n"
    ledger.write_text(body)
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_x.py").write_text("def test_holds():\n    assert True\n")
    (ledger.parent / "develop-red.out").write_text("TEST_PATH: tests/test_x.py\nTARGET_TEST: test_holds\n")
    reason = tmp_path / "reason.txt"
    reason.write_text("VERDICT: REJECT\nREASON: the mutation (< 2 to < 1) stays green\n")
    fake_processes.answers({"detect-test-command.sh": (0, 'pytest "$1"\n', ""), "": (1, "", "")})

    code, out, err = run_cli(pin_reject_route, [str(reason), str(ledger), "a one", "test_elsewhere"],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, out.strip(), ledger.read_text()) == (2, "", body), err


def test_main_bare_target_test_name_with_no_red_report_reaches_the_case_run_unchanged_4549(
        tmp_path, run_cli, pin_reject_route, monkeypatch):
    ran = []
    monkeypatch.setattr(pin_reject_route.tick_ledger, "run_case", lambda case, *rest, **kw: (ran.append(case) or 0, "", 0))
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    ledger.write_text("# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n")
    reason = tmp_path / "reason.txt"
    reason.write_text("VERDICT: REJECT\nREASON: the mutation (< 2 to < 1) stays green\n")

    code, out, err = run_cli(pin_reject_route, [str(reason), str(ledger), "a one", "test_holds"],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, out.strip(), ran) == (0, "retired", ["test_holds"]), err


def test_main_bare_target_test_name_only_a_prefix_of_a_case_the_test_path_file_holds_exits_2_and_ticks_nothing_4549(
        tmp_path, run_cli, pin_reject_route, monkeypatch, fake_processes):
    monkeypatch.undo()
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    body = "# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n"
    ledger.write_text(body)
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_x.py").write_text("def test_holds():\n    assert True\n")
    (ledger.parent / "develop-red.out").write_text("TEST_PATH: tests/test_x.py\nTARGET_TEST: test_holds\n")
    reason = tmp_path / "reason.txt"
    reason.write_text("VERDICT: REJECT\nREASON: the mutation (< 2 to < 1) stays green\n")
    fake_processes.answers({"detect-test-command.sh": (0, 'pytest "$1"\n', ""), "": (1, "", "")})

    code, out, err = run_cli(pin_reject_route, [str(reason), str(ledger), "a one", "test_hold"],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, out.strip(), ledger.read_text()) == (2, "", body), err


def test_main_missing_reroute_already_holds_fallback_runs_the_joined_bare_name_4549(
        tmp_path, run_cli, pin_reject_route, monkeypatch):
    ticks = []
    answers = iter([1, 0])
    monkeypatch.setattr(pin_reject_route.tick_ledger, "tick",
                        lambda ledger, matcher, **kw: (ticks.append((kw["retire"], kw["case"])), next(answers))[1])
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    ledger.write_text("# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_x.py").write_text("def test_holds():\n    assert True\n")
    (ledger.parent / "develop-red.out").write_text("TEST_PATH: tests/test_x.py\nTARGET_TEST: test_holds\n")
    reason = tmp_path / "reason.txt"
    reason.write_text("VERDICT: REJECT\nREASON: the behaviour already holds\n")

    code, out, err = run_cli(pin_reject_route, ["--missing-reroute", str(reason), str(ledger), "a one", "test_holds"],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, out.strip(), ticks) == (0, "retired", [("unpinnable", "tests/test_x.py::test_holds"),
                                                         ("already-holds", "tests/test_x.py::test_holds")]), err


def test_main_bare_target_test_name_with_a_red_report_lacking_test_path_reaches_the_case_run_unchanged_4549(
        tmp_path, run_cli, pin_reject_route, monkeypatch):
    ran = []
    monkeypatch.setattr(pin_reject_route.tick_ledger, "run_case", lambda case, *rest, **kw: (ran.append(case) or 0, "", 0))
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    ledger.write_text("# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n")
    (ledger.parent / "develop-red.out").write_text("TARGET_TEST: test_holds\nFAIL_OUTPUT: x\n")
    reason = tmp_path / "reason.txt"
    reason.write_text("VERDICT: REJECT\nREASON: the mutation (< 2 to < 1) stays green\n")

    code, out, err = run_cli(pin_reject_route, [str(reason), str(ledger), "a one", "test_holds"],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, out.strip(), ran) == (0, "retired", ["test_holds"]), err


def test_main_bare_target_test_name_whose_red_report_test_path_file_is_missing_reaches_the_case_run_unchanged_4549(
        tmp_path, run_cli, pin_reject_route, monkeypatch):
    ran = []
    monkeypatch.setattr(pin_reject_route.tick_ledger, "run_case", lambda case, *rest, **kw: (ran.append(case) or 0, "", 0))
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    ledger.write_text("# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n")
    (ledger.parent / "develop-red.out").write_text("TEST_PATH: tests/test_gone.py\nTARGET_TEST: test_holds\n")
    reason = tmp_path / "reason.txt"
    reason.write_text("VERDICT: REJECT\nREASON: the mutation (< 2 to < 1) stays green\n")

    code, out, err = run_cli(pin_reject_route, [str(reason), str(ledger), "a one", "test_holds"],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, out.strip(), ran) == (0, "retired", ["test_holds"]), err


@pytest.mark.parametrize("reason_text", [
    "not checked: tests/py/test_review.py (old text in no file of the repo)\n",
    "pin stayed green under its mutation: tests/py/test_review.py\n",
], ids=["not-checked", "repin-failed"])
def test_main_recheck_is_an_unknown_argument_exit_2_printing_no_route_and_leaving_the_ledger_untouched_4741(
        tmp_path, run_cli, pin_reject_route, reason_text):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    body = ("# Plan for #42\n\n- [x] a one ⟦criterion 1⟧\n"
            "- [x] ⟦diff-checked⟧ edit the case of the pin on tests/py/test_review.py"
            " so its recorded mutation turns it red ⟦added⟧\n"
            "- [ ] b two ⟦criterion 2⟧\n")
    ledger.write_text(body)
    reason = tmp_path / "reason.txt"
    reason.write_text(reason_text)

    code, out, err = run_cli(pin_reject_route, ["--recheck", str(reason), str(ledger), "a one", TARGET],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, out, "unknown argument: --recheck" in err, ledger.read_text()) == (2, "", True, body), err


class FakeRepo:
    """git's answers over a work tree at <root> whose HEAD holds <head> ({path: text}) and whose index also holds the
    paths in <staged> (added, absent from HEAD): the listing of files differing from HEAD (diff, staged ones included,
    and untracked) read off the tree, `checkout HEAD -- <paths>` writing HEAD's text back and failing, as git does, on a
    path HEAD lacks, `ls-tree` naming the paths HEAD holds, `rm -f` dropping a path from the index and the tree."""

    def __init__(self, root, head, staged=()):
        self.root, self.head, self.staged = root, head, set(staged)

    def __call__(self, *args, **kwargs):
        import subprocess
        args = list(args)
        if args[:2] == ["-C", str(self.root)]:
            args = args[2:]
        out = b""
        paths = args[args.index("--") + 1:] if "--" in args else []
        if args[:1] == ["diff"] and "--name-only" in args:
            out = b"".join(path.encode() + b"\0" for path, text in self.head.items()
                           if not (self.root / path).exists() or (self.root / path).read_text() != text)
            out += b"".join(path.encode() + b"\0" for path in sorted(self.staged) if (self.root / path).exists())
        elif args[:1] == ["ls-files"] and "--others" in args:
            out = b"".join(str(p.relative_to(self.root)).encode() + b"\0" for p in sorted(self.root.rglob("*"))
                           if p.is_file() and ".tdd" not in p.parts
                           and str(p.relative_to(self.root)) not in self.head
                           and str(p.relative_to(self.root)) not in self.staged)
        elif args[:2] == ["rev-parse", "--show-toplevel"]:
            out = str(self.root).encode() + b"\n"
        elif args[:3] == ["checkout", "HEAD", "--"]:
            unknown = [path for path in paths if path not in self.head]
            if unknown:
                return subprocess.CompletedProcess(["git", *args], 1, b"", (
                    "error: pathspec '%s' did not match any file(s) known to git\n" % unknown[0]).encode())
            for path in paths:
                (self.root / path).parent.mkdir(parents=True, exist_ok=True)
                (self.root / path).write_text(self.head[path])
        elif args[:1] == ["ls-tree"] and "HEAD" in args:
            out = b"".join(path.encode() + b"\0" for path in paths if path in self.head)
        elif args[:1] == ["rm"] and "-f" in args:
            unknown = [path for path in paths if path not in self.head and path not in self.staged]
            if unknown:
                return subprocess.CompletedProcess(["git", *args], 128, b"", (
                    "fatal: pathspec '%s' did not match any files\n" % unknown[0]).encode())
            for path in paths:
                self.staged.discard(path)
                self.head.pop(path, None)
                if (self.root / path).exists():
                    (self.root / path).unlink()
        else:
            return subprocess.CompletedProcess(["git", *args], 128, b"", b"fake git: unanswered\n")
        return subprocess.CompletedProcess(["git", *args], 0, out, b"")


def test_main_hand_mutation_stays_green_retire_deletes_an_untracked_test_file_and_restores_a_modified_one_4739(
        tmp_path, run_cli, pin_reject_route, monkeypatch):
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    ledger.write_text("# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n")
    reason = tmp_path / "reason.txt"
    reason.write_text("VERDICT: REJECT\nREASON: the hand mutation stays green\n")
    tests = tmp_path / "tests" / "py"
    tests.mkdir(parents=True)
    (tests / "test_old.py").write_text("def test_old():\n    assert True\n    assert 1\n")
    (tests / "test_new.py").write_text("def test_new():\n    assert True\n")
    monkeypatch.setattr(pin_reject_route.tick_ledger.git, "git",
                        FakeRepo(tmp_path, {"tests/py/test_old.py": "def test_old():\n    assert True\n",
                                            "reason.txt": reason.read_text()}))

    code, out, err = run_cli(pin_reject_route, [str(reason), str(ledger), "a one", TARGET],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, out.strip(), ledger.read_text().split("\n")[2], (tests / "test_new.py").exists(),
            (tests / "test_old.py").read_text()) == (
        0, "retired", "- [x] a one ⟦criterion 1⟧ ⟂ retired unpinnable", False,
        "def test_old():\n    assert True\n"), err


def red_tree(tmp_path, monkeypatch, pin_reject_route, reason_text):
    """A ledger, a reason saying <reason_text>, and the Red leaf's uncommitted test edits over a faked git: test_old.py
    modified from HEAD, test_new.py untracked. Returns (ledger, reason, tests dir, the tree's test files' texts)."""
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.parent.mkdir()
    ledger.write_text("# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n- [ ] b two ⟦criterion 2⟧\n")
    reason = tmp_path / "reason.txt"
    reason.write_text("VERDICT: REJECT\nREASON: " + reason_text + "\n")
    tests = tmp_path / "tests" / "py"
    tests.mkdir(parents=True)
    (tests / "test_old.py").write_text("def test_old():\n    assert True\n    assert 1\n")
    (tests / "test_new.py").write_text("def test_new():\n    assert True\n")
    monkeypatch.setattr(pin_reject_route.tick_ledger.git, "git",
                        FakeRepo(tmp_path, {"tests/py/test_old.py": "def test_old():\n    assert True\n",
                                            "reason.txt": reason.read_text()}))
    return ledger, reason, tests, {p.name: p.read_text() for p in sorted(tests.iterdir())}


def test_main_before_state_green_retire_leaves_every_test_file_as_it_was_4739(
        tmp_path, run_cli, pin_reject_route, monkeypatch):
    ledger, reason, tests, before = red_tree(tmp_path, monkeypatch, pin_reject_route,
                                             "the real before-state stays green")

    code, out, err = run_cli(pin_reject_route, [str(reason), str(ledger), "a one", TARGET],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, out.strip(), ledger.read_text().split("\n")[2],
            {p.name: p.read_text() for p in sorted(tests.iterdir())}) == (
        0, "retired", "- [x] a one ⟦criterion 1⟧ ⟂ retired unpinnable", before), err


def test_main_before_state_green_and_guard_mutation_stays_green_retire_leaves_every_test_file_as_it_was_4739(
        tmp_path, run_cli, pin_reject_route, monkeypatch):
    ledger, reason, tests, before = red_tree(tmp_path, monkeypatch, pin_reject_route,
                                             "the real before-state stays green; the guard mutation stays green")

    code, out, err = run_cli(pin_reject_route, [str(reason), str(ledger), "a one", TARGET],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, out.strip(), ledger.read_text().split("\n")[2],
            {p.name: p.read_text() for p in sorted(tests.iterdir())}) == (
        0, "retired", "- [x] a one ⟦criterion 1⟧ ⟂ retired unpinnable", before), err


def test_main_removing_retire_leaves_the_ledger_rewrite_a_tdd_file_and_a_modified_production_file_unchanged_4739(
        tmp_path, run_cli, pin_reject_route, monkeypatch):
    ledger, reason, tests, _ = red_tree(tmp_path, monkeypatch, pin_reject_route, "the hand mutation stays green")
    (tmp_path / ".tdd" / "notes.md").write_text("notes now\n")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "prod.py").write_text("x = 2\n")
    monkeypatch.setattr(pin_reject_route.tick_ledger.git, "git",
                        FakeRepo(tmp_path, {"tests/py/test_old.py": "def test_old():\n    assert True\n",
                                            "reason.txt": reason.read_text(),
                                            ".tdd/issue-42.md": ledger.read_text(),
                                            ".tdd/notes.md": "notes at HEAD\n",
                                            "src/prod.py": "x = 1\n"}))

    code, out, err = run_cli(pin_reject_route, [str(reason), str(ledger), "a one", TARGET],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, out.strip(), ledger.read_text().split("\n")[2], (tmp_path / ".tdd" / "notes.md").read_text(),
            (tmp_path / "src" / "prod.py").read_text(), sorted(p.name for p in tests.iterdir())) == (
        0, "retired", "- [x] a one ⟦criterion 1⟧ ⟂ retired unpinnable", "notes now\n", "x = 2\n", ["test_old.py"]), err


def test_main_hand_mutation_stays_green_reject_whose_target_case_fails_prints_revise_exits_1_and_removes_no_test_file_4739(
        tmp_path, run_cli, pin_reject_route, monkeypatch):
    ledger, reason, tests, before = red_tree(tmp_path, monkeypatch, pin_reject_route, "the hand mutation stays green")
    body = ledger.read_text()
    monkeypatch.setattr(pin_reject_route.tick_ledger, "run_case", lambda case, *rest, **kw: (1, "", 1))

    code, out, err = run_cli(pin_reject_route, [str(reason), str(ledger), "a one", TARGET],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, out.strip(), ledger.read_text(), {p.name: p.read_text() for p in sorted(tests.iterdir())}) == (
        1, "revise", body, before), err


def test_main_missing_reroute_already_holds_retire_removes_no_test_file_4739(
        tmp_path, run_cli, pin_reject_route, monkeypatch):
    ledger, reason, tests, before = red_tree(tmp_path, monkeypatch, pin_reject_route,
                                             "the behaviour is already covered by an earlier step")

    code, out, err = run_cli(pin_reject_route, ["--missing-reroute", str(reason), str(ledger), "a one", TARGET],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, out.strip(), ledger.read_text().split("\n")[2],
            {p.name: p.read_text() for p in sorted(tests.iterdir())}) == (
        0, "retired", "- [x] a one ⟦criterion 1⟧ ⟂ retired already holds", before), err


def test_main_removing_retire_deletes_a_test_file_staged_as_new_and_leaves_it_out_of_the_index_4739(
        tmp_path, run_cli, pin_reject_route, monkeypatch):
    ledger, reason, tests, _ = red_tree(tmp_path, monkeypatch, pin_reject_route, "the hand mutation stays green")
    (tests / "test_staged.py").write_text("def test_staged():\n    assert True\n")
    repo = FakeRepo(tmp_path, {"tests/py/test_old.py": "def test_old():\n    assert True\n",
                               "reason.txt": reason.read_text()}, staged=["tests/py/test_staged.py"])
    monkeypatch.setattr(pin_reject_route.tick_ledger.git, "git", repo)

    code, out, err = run_cli(pin_reject_route, [str(reason), str(ledger), "a one", TARGET],
                             env={"VERI_ISSUE": "42"}, cwd=tmp_path)

    assert (code, out.strip(), ledger.read_text().split("\n")[2], sorted(p.name for p in tests.iterdir()),
            (tests / "test_old.py").read_text(), sorted(repo.staged)) == (
        0, "retired", "- [x] a one ⟦criterion 1⟧ ⟂ retired unpinnable", ["test_old.py"],
        "def test_old():\n    assert True\n", []), err
