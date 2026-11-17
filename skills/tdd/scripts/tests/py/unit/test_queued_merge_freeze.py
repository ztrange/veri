"""veri/queued_merge.py refusing a join while CI's latest answer on the stack is red (PRD 034.3a, D12), in-process: the
join's world is test_queued_merge_join's, and the stack-red.sh call is queued_merge._stack_red, spied in-process."""
from test_queued_merge_join import World, join, pushed, released
from veri import queued_merge

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
