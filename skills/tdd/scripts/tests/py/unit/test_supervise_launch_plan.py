"""supervise.launch_plan: whether a leaf may launch, answered as a value, one case per gate.

A refusal is returned, not performed: no case finds an `.exit` file or an event on disk after launch_plan.
"""
import json
import os

import pytest
from veri import supervise

HEAD = "git -C"
TOP = "git rev-parse --show-toplevel"
REFUSING = "supervise: refusing to launch {}: {}"


@pytest.fixture
def work_tree(tmp_path, monkeypatch):
    """A work tree (a `.git` directory, never a real repository) the case runs in, the skill's checkout outside it."""
    (tmp_path / ".git").mkdir()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(supervise, "HERE", "/skill")
    return tmp_path


def shape(plan):
    """(stderr lines, exit code, `.exit` written?, journal fields or None)."""
    assert isinstance(plan, supervise.Refusal), plan
    return plan.lines, plan.code, plan.exit_file is not None, plan.journal and plan.journal[2]


def nothing_written(root):
    return not any(name.endswith(".exit") or name == "events.jsonl" for name in os.listdir(root / ".tdd"))


def launch_refused(name, reason):
    return ((REFUSING.format(name, reason),), 2, True, ("launch-refused", f"name={name}", f"reason={reason}"))


def hand_exit(name, reason):
    return ((REFUSING.format(name, reason),), 2, True, None)


def test_gate_1_no_argument_or_an_empty_name_refuses_with_the_usage_line_alone(work_tree, fake_processes):
    fake = fake_processes.answers({})

    assert [shape(supervise.launch_plan(argv)) for argv in ([], [""])] == [((supervise.USAGE,), 2, False, None)] * 2
    assert fake.calls == [] and os.listdir(work_tree) == [".git"]


def test_gate_2_a_name_alone_refuses_missing_cmd_then_the_usage_line(work_tree, fake_processes):
    fake_processes.answers({})

    assert shape(supervise.launch_plan(["develop-red"])) == (("supervise: missing <cmd>", supervise.USAGE), 2, False, None)


def test_gate_3_a_non_numeric_veri_timeout_refuses_before_any_process(work_tree, monkeypatch, fake_processes):
    monkeypatch.setenv("VERI_TIMEOUT", "soon")
    monkeypatch.setenv("VERI_ISSUE", "7")
    fake = fake_processes.answers({})

    assert shape(supervise.launch_plan(["develop-red", "true"])) == (
        ("supervise: VERI_TIMEOUT is not a number: 'soon'",), 2, False, None)
    assert fake.calls == []


@pytest.mark.parametrize("pinned, line", [
    ("abc", "supervise: {} is not a number: 'abc'"),
    ("0", "supervise: {} must hold a whole number of seconds >= 1: '0'"),
    ("", "supervise: {} must hold a whole number of seconds >= 1: ''"),
], ids=["gate-4-not-a-number", "gate-5-below-one", "gate-5-empty"])
def test_gates_4_and_5_the_runs_timeout_pin_found_through_the_toplevel_must_be_a_whole_number_above_zero(
        work_tree, monkeypatch, fake_processes, pinned, line):
    monkeypatch.setenv("VERI_ISSUE", "7")
    pin = work_tree / ".tdd" / "issue-7-timeout"
    pin.parent.mkdir()
    pin.write_text(pinned + "\n")
    fake = fake_processes.answers({"git rev-parse --show-toplevel": (0, f"{work_tree}\n", "")})

    assert shape(supervise.launch_plan(["develop-red", "true"])) == ((line.format(pin),), 2, False, None)
    assert fake.calls == ["git rev-parse --show-toplevel"]


@pytest.mark.parametrize("var, value, line", [
    ("VERI_KILL_POLL", "x", "supervise: VERI_KILL_POLL must be a non-negative number: x"),
    ("VERI_HEARTBEAT", "x", "supervise: VERI_HEARTBEAT is not a number: 'x'"),
    ("VERI_TOOL_IDLE", "x", "supervise: VERI_TOOL_IDLE is not a number: 'x'"),
    ("VERI_STUCK_RETRIES", "x", "supervise: VERI_STUCK_RETRIES is not a number: 'x'"),
], ids=["gate-6", "gate-7", "gate-8", "gate-9"])
def test_gates_6_to_9_a_bad_window_tunable_refuses_with_its_line_and_no_side_effect(
        work_tree, monkeypatch, fake_processes, var, value, line):
    monkeypatch.setenv(var, value)
    fake = fake_processes.answers({})

    assert shape(supervise.launch_plan(["develop-red", "true"])) == ((line,), 2, False, None)
    assert fake.calls == [] and os.listdir(work_tree) == [".git"]


def test_gates_7_to_9_are_tried_in_order_so_the_first_bad_tunable_is_named(work_tree, monkeypatch, fake_processes):
    for var in ("VERI_HEARTBEAT", "VERI_TOOL_IDLE", "VERI_STUCK_RETRIES"):
        monkeypatch.setenv(var, "x")
    fake_processes.answers({})

    assert supervise.launch_plan(["develop-red", "true"]).lines == ("supervise: VERI_HEARTBEAT is not a number: 'x'",)


def test_gate_10_veri_step_set_but_empty_refuses_with_exit_and_a_launch_refused_event(
        work_tree, monkeypatch, fake_processes):
    monkeypatch.setenv("VERI_STEP", "")
    fake_processes.answers({HEAD: (0, "abc\n", "")})

    assert shape(supervise.launch_plan(["develop-red", "true"])) == launch_refused("develop-red", "VERI_STEP is set but empty")
    assert nothing_written(work_tree)


def test_gate_11_an_empty_step_argument_refuses_with_exit_and_a_launch_refused_event(work_tree, fake_processes):
    fake_processes.answers({HEAD: (0, "abc\n", "")})

    assert shape(supervise.launch_plan(["verdict-red", "x.sh", "--step", ""])) == launch_refused("verdict-red", "--step is empty")


def test_gates_12_to_14_run_leaf_without_a_usable_prompt_refuse_with_exit_and_a_launch_refused_event(
        work_tree, fake_processes):
    fake_processes.answers({HEAD: (0, "abc\n", "")})
    (work_tree / "empty.md").write_text("")

    assert [shape(supervise.launch_plan(["develop-red", "/s/run-leaf.sh", *prompt]))
            for prompt in ([], ["gone.md"], ["empty.md"])] == [
        launch_refused("develop-red", "run-leaf.sh was given no prompt argument"),
        launch_refused("develop-red", "the prompt file gone.md does not exist"),
        launch_refused("develop-red", "the prompt file empty.md is empty"),
    ]
    assert nothing_written(work_tree)


@pytest.mark.parametrize("mode", ["at-leaf", "now"])
def test_gate_15_a_pending_stop_refuses_with_exit_and_a_launch_refused_event(work_tree, fake_processes, mode):
    (work_tree / ".tdd").mkdir()
    (work_tree / ".tdd" / "stop").write_text(mode + "\n")
    fake_processes.answers({HEAD: (0, "abc\n", "")})

    assert shape(supervise.launch_plan(["develop-red", "true"])) == launch_refused("develop-red", f"a stop ({mode}) is pending")


def test_gate_16_develop_green_after_an_unpassed_red_refuses_with_exit_and_no_event(work_tree, monkeypatch, fake_processes):
    monkeypatch.setenv("VERI_STEP", "1")
    (work_tree / ".tdd").mkdir()
    (work_tree / ".tdd" / "events.jsonl").write_text(json.dumps({"event": "launch", "step": "1", "phase": "red"}) + "\n")
    fake_processes.answers({HEAD: (0, "abc\n", "")})

    assert shape(supervise.launch_plan(["develop-green", "true"])) == hand_exit(
        "develop-green", "step 1 has no verify-red PASS after its latest red leaf")


def test_gate_17_a_verifier_whose_work_tree_hash_fails_refuses_with_exit_and_no_event(work_tree, fake_processes):
    fake_processes.answers({HEAD: (0, "abc\n", ""), "git check-ignore": (1, "", ""), "git add": (0, "", ""),
                            "git write-tree": (128, "", "")})

    assert shape(supervise.launch_plan(["verify-red", "true"])) == hand_exit(
        "verify-red", "the work-tree hash could not be computed")
    assert nothing_written(work_tree)


@pytest.mark.parametrize("name", ["verify-red", "verify-green"])
def test_gate_18_a_verifier_without_a_current_pass_marker_refuses_with_exit_and_no_event(work_tree, fake_processes, name):
    fake_processes.answers({HEAD: (0, "abc\n", ""), "git check-ignore": (1, "", ""), "git add": (0, "", ""),
                            "git write-tree": (0, "tree\n", "")})

    assert shape(supervise.launch_plan([name, "true"])) == hand_exit(
        name, "step (unset) has no current check-earlier pass marker (run tests-frozen.sh check-earlier first)")


def live_owner(root, name):
    (root / ".tdd").mkdir()
    (root / ".tdd" / "leaf.owner").write_text(f"{os.getpid()} {name}\n")


def test_gate_19_a_live_other_leaf_refuses_with_exit_and_no_event(work_tree, fake_processes):
    live_owner(work_tree, "develop-red")
    fake_processes.answers({HEAD: (0, "abc\n", "")})

    assert shape(supervise.launch_plan(["revise-red", "true"])) == hand_exit(
        "revise-red", f"leaf develop-red (pid {os.getpid()}) is still alive in this worktree")


def test_gate_19_a_live_leaf_of_the_same_name_refuses_without_writing_its_exit(work_tree, fake_processes):
    live_owner(work_tree, "develop-red")
    fake_processes.answers({HEAD: (0, "abc\n", "")})

    assert shape(supervise.launch_plan(["develop-red", "true"])) == (
        (REFUSING.format("develop-red", f"leaf develop-red (pid {os.getpid()}) is still alive in this worktree"),),
        2, False, None)


LSTART = f"ps -o lstart= -p {os.getpid()}"


def test_gate_19_a_leaf_owner_whose_pid_is_alive_under_another_start_time_refuses_nothing_3988(work_tree, fake_processes):
    (work_tree / ".tdd").mkdir()
    (work_tree / ".tdd" / "leaf.owner").write_text(f"{os.getpid()} develop-red\nMon Jan  1 00:00:00 2024\n")
    fake_processes.answers({HEAD: (0, "abc\n", ""), LSTART: (0, "Thu Nov 11 09:00:00 2026\n", "")})

    plan = supervise.launch_plan(["revise-red", "true"])

    assert isinstance(plan, supervise.Launch), plan


def test_gate_19_a_leaf_owner_whose_pid_is_alive_under_the_same_start_time_refuses_3988(work_tree, fake_processes):
    (work_tree / ".tdd").mkdir()
    (work_tree / ".tdd" / "leaf.owner").write_text(f"{os.getpid()} develop-red\nThu Nov 11 09:00:00 2026\n")
    fake_processes.answers({HEAD: (0, "abc\n", ""), LSTART: (0, "Thu Nov 11 09:00:00 2026\n", "")})

    assert shape(supervise.launch_plan(["revise-red", "true"])) == hand_exit(
        "revise-red", f"leaf develop-red (pid {os.getpid()}) is still alive in this worktree")


def test_gate_19_a_leaf_owner_with_no_start_time_line_whose_pid_is_alive_refuses_3988(work_tree, fake_processes):
    (work_tree / ".tdd").mkdir()
    (work_tree / ".tdd" / "leaf.owner").write_text(f"{os.getpid()} develop-red\n")
    fake_processes.answers({HEAD: (0, "abc\n", ""), LSTART: (0, "Thu Nov 11 09:00:00 2026\n", "")})

    assert shape(supervise.launch_plan(["revise-red", "true"])) == hand_exit(
        "revise-red", f"leaf develop-red (pid {os.getpid()}) is still alive in this worktree")


def test_gate_19_a_leaf_owner_whose_live_pids_start_time_ps_cannot_read_refuses_3988(work_tree, fake_processes):
    (work_tree / ".tdd").mkdir()
    (work_tree / ".tdd" / "leaf.owner").write_text(f"{os.getpid()} develop-red\nMon Jan  1 00:00:00 2024\n")
    fake_processes.answers({HEAD: (0, "abc\n", ""), LSTART: (1, "", "")})

    assert shape(supervise.launch_plan(["revise-red", "true"])) == hand_exit(
        "revise-red", f"leaf develop-red (pid {os.getpid()}) is still alive in this worktree")


def test_a_stop_and_an_empty_prompt_report_the_earlier_gate(work_tree, fake_processes):
    (work_tree / ".tdd").mkdir()
    (work_tree / ".tdd" / "stop").write_text("now\n")
    fake_processes.answers({HEAD: (0, "abc\n", "")})

    assert supervise.launch_plan(["develop-red", "run-leaf.sh"]).lines == (
        REFUSING.format("develop-red", "run-leaf.sh was given no prompt argument"),)


def test_every_gate_passed_answers_the_settings_the_attempt_loop_reads(work_tree, monkeypatch, fake_processes):
    monkeypatch.setenv("VERI_TIMEOUT", "60")
    monkeypatch.setenv("VERI_HEARTBEAT", "30")
    monkeypatch.setenv("VERI_STUCK_RETRIES", "3")
    fake = fake_processes.answers({HEAD: (0, "abc\n", "")})

    plan = supervise.launch_plan(["develop-red", "true", "x"])

    assert isinstance(plan, supervise.Launch)
    assert (plan.name, plan.cmd, plan.retries, plan.log, plan.exitfile, plan.ownerfile) == (
        "develop-red", ["true", "x"], "3", ".tdd/develop-red.log", ".tdd/develop-red.exit", ".tdd/leaf.owner")
    assert (plan.watch.watched, plan.watch.timeout, plan.watch.heartbeat) == (True, "60", "30")
    assert plan.leaf_env["VERI_SKILL_COMMIT"] == "abc"
    assert fake.calls == ["git -C /skill rev-parse HEAD"]


def test_perform_writes_exit_then_the_event_then_stderr_and_returns_2(work_tree, monkeypatch, capsys, fake_processes):
    fake_processes.answers({})
    (work_tree / ".tdd").mkdir()
    seen = []
    monkeypatch.setattr(supervise, "mark", lambda role, env, *fields: seen.append(
        (role, fields, (work_tree / ".tdd" / "x.exit").read_text(), capsys.readouterr().err)))

    code = supervise.launch_refused("", {}, "x", "why").perform()

    assert (code, seen, capsys.readouterr().err) == (
        2, [("actor=supervisor", ("launch-refused", "name=x", "reason=why"), "2\n", "")],
        "supervise: refusing to launch x: why\n")


def ledger_of(root, *lines):
    (root / ".tdd").mkdir(exist_ok=True)
    (root / ".tdd" / "issue-7.md").write_text("".join(f"- [ ] {line}\n" for line in lines))


@pytest.mark.parametrize("reference", ["0", "00"])
def test_gate_18_a_step_reference_of_zero_names_no_step_like_one_past_the_ledger(work_tree, monkeypatch, fake_processes, reference):
    ledger_of(work_tree, "first", "second")
    monkeypatch.setenv("VERI_ISSUE", "7")
    monkeypatch.setenv("VERI_STEP", reference)
    monkeypatch.setattr(supervise, "pass_marker_current", lambda text: True)
    fake_processes.answers({TOP: (1, "", ""), HEAD: (0, "abc\n", ""), "git check-ignore": (1, "", ""), "git add": (0, "", ""),
                            "git write-tree": (0, "tree\n", "")})

    assert shape(supervise.launch_plan(["verify-red", "true"])) == hand_exit(
        "verify-red", f"step {reference} has no current check-earlier pass marker (run tests-frozen.sh check-earlier first)")


def test_gate_16_a_step_reference_of_zero_is_no_ci_repair_step_even_when_the_last_step_is_one(work_tree, monkeypatch, fake_processes):
    ledger_of(work_tree, "first", "second ⟦ci-repair⟧")
    (work_tree / ".tdd" / "events.jsonl").write_text(json.dumps({"event": "launch", "step": "0", "phase": "red"}) + "\n")
    monkeypatch.setenv("VERI_ISSUE", "7")
    monkeypatch.setenv("VERI_STEP", "0")
    fake_processes.answers({TOP: (1, "", ""), HEAD: (0, "abc\n", "")})

    assert shape(supervise.launch_plan(["develop-green", "true"])) == hand_exit(
        "develop-green", "step 0 has no verify-red PASS after its latest red leaf")


def snapshot_serving(tmp_path, monkeypatch, work_tree, issue="7"):
    """A skill snapshot supervise runs from, its digest recorded for run <issue> in the work tree's `.tdd/`."""
    from veri import pinned_scripts, run_pins
    snapshot = tmp_path / "veri-snapshot-x"
    (snapshot / "scripts").mkdir(parents=True)
    (snapshot / "SKILL.md").write_text("# skill\n")
    (snapshot / "scripts" / "status.sh").write_text("echo status\n")
    pinned_scripts.write_snapshot_marker(str(snapshot), str(work_tree))
    (work_tree / ".tdd").mkdir(exist_ok=True)
    run_pins.write_snapshot_digest(str(work_tree), issue, pinned_scripts.digest_text(pinned_scripts.snapshot_digest(str(snapshot))))
    monkeypatch.setattr(supervise, "HERE", str(snapshot / "scripts"))
    monkeypatch.setenv("VERI_ISSUE", issue)
    return snapshot


def test_gate_20_a_snapshot_file_edited_since_its_digest_refuses_naming_it_with_exit_and_a_launch_refused_event_3964(
        tmp_path, work_tree, monkeypatch, fake_processes):
    snapshot = snapshot_serving(tmp_path, monkeypatch, work_tree)
    (snapshot / "scripts" / "status.sh").write_text("echo edited\n")
    fake_processes.answers({HEAD: (0, "abc\n", ""), TOP: (0, f"{work_tree}\n", "")})

    assert shape(supervise.launch_plan(["develop-red", "true"])) == launch_refused(
        "develop-red", f"the skill snapshot {snapshot / 'scripts' / 'status.sh'} changed since extraction")


def test_gate_20_an_unpinned_run_launches_from_an_edited_snapshot_3964(tmp_path, work_tree, monkeypatch, fake_processes):
    snapshot = snapshot_serving(tmp_path, monkeypatch, work_tree)
    (snapshot / "scripts" / "status.sh").write_text("echo edited\n")
    monkeypatch.setenv("VERI_SKILL_UNPINNED", "1")
    fake_processes.answers({HEAD: (0, "abc\n", ""), TOP: (0, f"{work_tree}\n", "")})

    assert isinstance(supervise.launch_plan(["develop-red", "true"]), supervise.Launch)


@pytest.mark.parametrize("gone", ["marker", "digest"])
def test_gate_20_a_snapshot_run_whose_marker_or_digest_file_is_gone_refuses_3964(
        tmp_path, work_tree, monkeypatch, fake_processes, gone):
    snapshot = snapshot_serving(tmp_path, monkeypatch, work_tree)
    digest = work_tree / ".tdd" / "issue-7-snapshot-digest"
    (snapshot / ".veri-snapshot" if gone == "marker" else digest).unlink()
    fake_processes.answers({HEAD: (0, "abc\n", ""), TOP: (0, f"{work_tree}\n", "")})

    assert shape(supervise.launch_plan(["develop-red", "true"])) == launch_refused("develop-red", {
        "marker": f"the skill snapshot {snapshot / '.veri-snapshot'} changed since extraction",
        "digest": f"the skill snapshot {snapshot} has no recorded digest {digest}"}[gone])


@pytest.mark.parametrize("recorded", [b"\xff\xfe not utf-8\n", b"directory scripts\n", b"[" * 200000 + b"]" * 200000],
                         ids=["invalid-utf-8", "not-a-digest", "nested-too-deep"])
def test_gate_20_a_digest_file_it_cannot_parse_refuses_with_a_launch_refused_event_3964(
        tmp_path, work_tree, monkeypatch, fake_processes, recorded):
    snapshot = snapshot_serving(tmp_path, monkeypatch, work_tree)
    (work_tree / ".tdd" / "issue-7-snapshot-digest").write_bytes(recorded)
    fake_processes.answers({HEAD: (0, "abc\n", ""), TOP: (0, f"{work_tree}\n", "")})

    lines, code, exit_written, journal = shape(supervise.launch_plan(["develop-red", "true"]))

    assert (lines[0].startswith(REFUSING.format("develop-red", f"the skill snapshot {snapshot} could not be checked: ")),
            code, exit_written, journal[0]) == (True, 2, True, "launch-refused")
