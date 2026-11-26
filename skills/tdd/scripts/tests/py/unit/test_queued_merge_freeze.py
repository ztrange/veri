"""veri/queued_merge.py refusing a join while CI's latest answer on the stack is red (PRD 034.3a, D12), in-process: the
join's world is test_queued_merge_join's, and the stack-red.sh call is queued_merge._stack_red, spied in-process."""
import os

import pytest
from test_queued_merge_join import BRANCH, ENV, PR, World, join, pushed, released
from veri import queued_merge

from process_fakes import HANGS

RED = "%040x" % 9
URL = "https://github.com/o/r/actions/runs/42"


def spy_stack_red(monkeypatch, world, answer=(0, "%s %s failure\n" % (RED, URL))):
    """queued_merge._stack_red swapped for an in-process spy answering (exit code, stdout): each call records the
    worktree it was given and the git and push calls made by then."""
    asked = []

    def stack_red(worktree):
        asked.append((worktree, [c for c in world.calls if " fetch " in c or " rebase " in c or " push " in c]))
        return answer

    monkeypatch.setattr(queued_merge, "_stack_red", stack_red)
    return asked


def test_a_join_asks_stack_red_after_its_fetch_and_before_its_rebase_and_on_exit_0_exits_1_rebasing_and_pushing_nothing(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = World(tmp_path).install(fake_processes, monkeypatch)
    asked = spy_stack_red(monkeypatch, world)

    code, _, err = join(run_cli, world)

    wt = "git -C %s " % world.wt
    rebased = [c for c in world.calls if c.startswith(wt + "rebase ")]
    kept = [c for c in world.calls if "worktree remove" in c or "branch -D" in c or "--delete" in c]
    assert (code, asked, rebased, pushed(world), len(released(world)), kept) == (
        1, [(world.wt, [wt + "fetch --prune origin"])], [], [], 1, []), err


def test_a_refusal_by_the_freeze_is_one_stderr_line_naming_the_red_commit_its_run_url_and_stack_culprit_as_the_next_command(
        tmp_path, fake_processes, monkeypatch, run_cli):
    clean = World(tmp_path / "clean").install(fake_processes, monkeypatch)
    spy_stack_red(monkeypatch, clean, (3, ""))
    _, _, quiet = join(run_cli, clean)
    world = World(tmp_path).install(fake_processes, monkeypatch)
    spy_stack_red(monkeypatch, world)

    _, _, err = join(run_cli, world)
    added = [line for line in err.splitlines() if line not in quiet.splitlines()]

    assert (len(added), RED in added[0], URL in added[0], "stack-culprit.sh %s" % RED in added[0]) == (1, True, True, True), err


@pytest.mark.parametrize("answer", [(2, ""), (1, ""), (124, ""), (-9, "")])
def test_a_stack_red_exit_2_or_any_exit_but_0_and_3_is_the_joins_exit_2_nothing_pushed_and_the_lock_freed(
        tmp_path, fake_processes, monkeypatch, run_cli, answer):
    world = World(tmp_path).install(fake_processes, monkeypatch)
    spy_stack_red(monkeypatch, world, answer)

    code, _, err = join(run_cli, world)

    assert (code, pushed(world), len(released(world)), "stack-red.sh" in err) == (2, [], 1, True), err


def test_a_stack_red_exit_3_lets_the_join_go_on_to_its_stack_push_as_before(
        tmp_path, fake_processes, monkeypatch, run_cli):
    world = World(tmp_path).install(fake_processes, monkeypatch)
    asked = spy_stack_red(monkeypatch, world, (3, ""))

    code, _, err = join(run_cli, world)

    assert (code, len(asked), len(world.stack_pushed())) == (0, 1, 1), err


KNOBS = {"VERI_CI_ON_PR": "0", "VERI_FETCH_RETRY_SLEEP": "0", "VERI_GH_DRIVER": "rest", "VERI_GH_TIMEOUT": "5",
         "VERI_GIT_NETWORK_TIMEOUT": "5", "VERI_MERGE_SETTLE_READS": "1", "VERI_MERGE_SETTLE_SLEEP": "0"}


@pytest.mark.parametrize("knob", sorted(KNOBS) + ["all", "no tag message"])
def test_no_argument_or_variable_of_the_join_gets_it_past_a_stack_red_exit_0(
        tmp_path, fake_processes, monkeypatch, run_cli, knob):
    world = World(tmp_path).install(fake_processes, monkeypatch)
    spy_stack_red(monkeypatch, world)
    env = dict(ENV, **(KNOBS if knob == "all" else {knob: KNOBS[knob]} if knob in KNOBS else {}))

    code, _, err = run_cli(queued_merge, [PR, world.wt, BRANCH, "-" if knob == "no tag message" else "the capability"],
                           env=env)

    assert (code, pushed(world), "stack-culprit.sh" in err) == (1, [], True), err


@pytest.mark.parametrize("stack_line, base", [("# no stack named\n", "stack"), ("veri: stack branch: stack\n", "main")])
def test_a_merge_with_no_stack_named_or_a_pull_request_based_elsewhere_makes_no_stack_red_call(
        tmp_path, fake_processes, monkeypatch, run_cli, stack_line, base):
    unmerged = {"state": "open", "merged": False, "head": {"sha": "9999999"}}
    world = World(tmp_path, stack_line=stack_line, base=base, reads=(unmerged,) * 20, extra={
        "git -C <wt> merge-base --is-ancestor 9999999 origin/main": (1, "", "")}).install(fake_processes, monkeypatch)
    asked = spy_stack_red(monkeypatch, world)

    join(run_cli, world)

    assert (asked, [c for c in world.calls if "stack-red" in c]) == ([], [])


def test_the_stack_red_call_is_bounded_a_hung_child_killed_and_answered_2(tmp_path, fake_processes, monkeypatch):
    fake = fake_processes.answers({"stack-red.sh": HANGS})
    monkeypatch.setattr(os, "killpg", lambda group, sig: [c.send_signal(sig) for c in fake.popens if c.pid == group])
    monkeypatch.setenv("VERI_GIT_NETWORK_TIMEOUT", "1")

    code, out = queued_merge._stack_red(str(tmp_path))

    assert (code, out, [p.signals != [] for p in fake.popens]) == (2, "", [True])
