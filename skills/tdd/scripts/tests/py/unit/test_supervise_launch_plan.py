"""supervise.launch_plan: whether a leaf may launch, answered as a value, one case per gate.

A refusal is returned, not performed: no case finds an `.exit` file or an event on disk after launch_plan.
"""
import json
import os

import pytest

from veri import supervise

HEAD = "git -C"
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
