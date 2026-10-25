"""veri/queued_merge.py in-process, every process boundary (merge-lock.sh, wait-ci.sh, git, gh) faked."""
import json
import os

import pytest

from veri import queued_merge

PR = "https://github.com/o/r/pull/7"
ARGV = [PR, "/wt", "feature", "the capability"]
ORIGIN_SHA = "1111111"
PUSHED_HEAD = "abc1234"
PID = str(os.getpid())
WAIT_CI = os.path.join(queued_merge.SCRIPTS, "wait-ci.sh")


def scenario(fake_processes, take=0, ci=(0,), merged=json.dumps({"merged": True}), gh_code=0, fail=()):
    """A queued merge's world: the lock, CI's answers in order, GitHub's merged answer, and commands that fail."""
    state = {"rebased": False, "ci": list(ci)}

    def answer(line, **_):
        for needle in fail:
            if needle in line:
                return 1, "", "%s refused" % needle
        if line.startswith("merge-lock.sh take"):
            return take, "", ""
        if "rebase origin/main" in line:
            state["rebased"] = True
        if "wait-ci.sh" in line:
            return state["ci"].pop(0), "", ""
        if "rev-parse --verify refs/remotes/origin/feature" in line:
            return 0, (ORIGIN_SHA if not state["rebased"] else "2222222") + "\n", ""
        if "rev-parse --verify HEAD" in line:
            return 0, (PUSHED_HEAD if state["rebased"] else "0000000") + "\n", ""
        if "tag --sort=-v:refname" in line:
            return 0, "v0.10\nv0.9\n", ""
        if line.startswith("gh api"):
            return gh_code, merged, ""
        return 0, "", ""

    return fake_processes(answer)


def first(calls, needle):
    return next((i for i, c in enumerate(calls) if needle in c), None)


def cleaned(calls):
    return [c for c in calls if "--delete" in c or "worktree remove" in c or " tag -a " in c]


def test_2372_queued_merge_fetches_origin_before_it_rebases(fake_processes, run_cli):
    calls = scenario(fake_processes)

    code, _, _ = run_cli(queued_merge, ARGV)

    fetch, rebase = first(calls, "fetch origin"), first(calls, "rebase origin/main")
    assert (code, fetch is not None, rebase is not None and fetch is not None and fetch < rebase) == (0, True, True)


def test_2372_queued_merge_pushes_under_a_lease_pinned_to_origin_branch_sha_read_before_the_rebase(fake_processes, run_cli):
    calls = scenario(fake_processes)

    code, _, _ = run_cli(queued_merge, ARGV)

    pushes = [c for c in calls if " push " in c and "--delete" not in c and "v0." not in c]
    assert (code, pushes) == (0, ["merge-lock.sh gate --keep --pid %s -- git -C /wt push --force-with-lease=feature:%s origin feature"
                                  % (PID, ORIGIN_SHA)])


def test_2372_queued_merge_waits_for_ci_through_wait_ci_on_the_pushed_head_after_the_push_and_merges_that_head(fake_processes, run_cli):
    calls = scenario(fake_processes)

    code, _, _ = run_cli(queued_merge, ARGV)

    push, wait = first(calls, "--force-with-lease"), first(calls, "wait-ci.sh")
    waits = [c for c in calls if "wait-ci.sh" in c]
    merges = [c for c in calls if "pr merge" in c]
    assert (code, push is not None and wait is not None and push < wait, waits, merges) == (
        0, True, ["merge-lock.sh gate --pid %s -- %s %s 540  %s" % (PID, WAIT_CI, PR, PUSHED_HEAD)],
        ["merge-lock.sh gate --pid %s -- gh pr merge %s --rebase --match-head-commit %s" % (PID, PR, PUSHED_HEAD)])


def test_2372_queued_merge_on_red_ci_exits_1_through_the_releasing_gate_and_never_merges(fake_processes, run_cli):
    calls = scenario(fake_processes, ci=(1,))

    code, _, _ = run_cli(queued_merge, ARGV)

    waits = [c for c in calls if "wait-ci.sh" in c]
    assert (code, [("--keep" in c) for c in waits], first(calls, "pr merge")) == (1, [False], None)


@pytest.mark.parametrize("ci, expected", [((3, 3, 0), 0), ((3, 2), 2), ((3, 3, 1), 1)])
def test_2372_queued_merge_treats_pending_or_absent_checks_as_not_green_and_asks_wait_ci_again(fake_processes, run_cli, ci, expected):
    calls = scenario(fake_processes, ci=ci)

    code, _, _ = run_cli(queued_merge, ARGV)

    asked = len([c for c in calls if "wait-ci.sh" in c])
    merged_after = first(calls, "pr merge") is not None
    assert (code, asked, merged_after) == (expected, len(ci), expected == 0)
