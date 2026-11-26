"""veri/queued_merge.py in-process, every process boundary (merge-lock.sh, wait-ci.sh, git, gh) faked."""
import ast
import base64
import json
import os
import pathlib

import pytest
from veri import queued_merge

from process_fakes import HANGS

PR = "https://github.com/o/r/pull/7"
ARGV = [PR, "/wt", "feature", "the capability"]
ORIGIN_SHA = "1111111"
PUSHED_HEAD = "abc1234"
MERGE_SHA = "fedcba9"
TAG_OID = "7a90000"
GUARDED_DELETE = "git -C /wt update-ref -d refs/tags/v0.11 %s" % TAG_OID
PID = str(os.getpid())
WAIT_CI = os.path.join(queued_merge.SCRIPTS, "wait-ci.sh")


@pytest.fixture
def fake_processes(fake_processes, monkeypatch):
    """conftest's fake in its legacy form, fake_processes(answer) -> calls, answering every entry point Popen included
    (the network calls run under github.bounded_group); os.killpg reaches the fake children by pid, never a real group."""
    fakes = []

    def every_entry(answer=None):
        fake = fake_processes.answers({}, default=answer or (lambda line, **_: (0, "", "")))
        fakes.append(fake)
        return fake.calls

    every_entry.answers = fake_processes.answers
    monkeypatch.setattr(os, "killpg", lambda group, sig: [c.send_signal(sig) for f in fakes for c in f.popens if c.pid == group])
    return every_entry


def hanging(fake_processes, line):
    """A fake_processes for scenario whose call <line> never returns."""
    def install(answer):
        return fake_processes(lambda called, **kwargs: HANGS if called == line else answer(called, **kwargs))
    return install


def scenario(fake_processes, take=0, ci=(0,), merged=json.dumps({"merged": True, "merge_commit_sha": "fedcba9"}), gh_code=0, fail=(), diverged=False, lease_readable=True, behind=False, dirty=False, tags="v0.10\nv0.9\n"):
    """A queued merge's world: the lock, CI's answers in order, GitHub's merged answer, the clone's tags as
    `git tag --sort=-v:refname` lists them, and commands that fail."""
    state = {"rebased": False, "ci": list(ci), "merged": False}

    def answer(line, **_):
        for needle in fail:
            if needle in line:
                return 1, "", "%s refused" % needle
        if line.startswith("merge-lock.sh take"):
            return take, "", ""
        if "rebase origin/main" in line:
            state["rebased"] = True
        if "pr merge" in line:
            state["merged"] = True
        is_put = "gh api" in line and "pulls/7/merge" in line
        if is_put and gh_code == 0:
            state["merged"] = True
        if "merge-base --is-ancestor" in line and "origin/main" in line:
            return 1, "", ""
        if behind and "merge-base --is-ancestor" in line:
            return (1 if line.endswith(" HEAD") else 0), "", ""
        if dirty and "status --porcelain" in line:
            return 0, " M file\n", ""
        if "merge-base --is-ancestor" in line and (ORIGIN_SHA in line or "origin/feature" in line):
            return (1 if diverged else 0), "", ""
        if "rev-parse --verify origin/main" in line or "rev-parse origin/main" in line:
            return 0, ("later00" if state["merged"] else "pre0000") + "\n", ""
        if "wait-ci.sh" in line:
            return state["ci"].pop(0), "", ""
        if "rev-parse --verify refs/remotes/origin/feature" in line and not lease_readable:
            return 1, "", "fatal: Needed a single revision"
        if "rev-parse --verify refs/remotes/origin/feature" in line:
            return 0, (ORIGIN_SHA if not state["rebased"] else "2222222") + "\n", ""
        if "rev-parse --verify HEAD" in line:
            return 0, (PUSHED_HEAD if state["rebased"] else "0000000") + "\n", ""
        if "--git-common-dir" in line:
            return 0, "/main/.git\n", ""
        if "ls-remote --heads origin refs/heads/feature" in line:
            return 0, "9999999\trefs/heads/feature\n", ""  # origin still holds the branch unless a case says otherwise
        if line == "git -C /wt rev-parse --verify refs/tags/v0.11":
            return 0, TAG_OID + "\n", ""
        if "tag --sort=-v:refname" in line:
            return 0, tags, ""
        if "gh api" in line and not is_put and not state["merged"]:
            return 0, json.dumps({"state": "open", "merged": False, "head": {"sha": "9999999"}}), ""
        if line.startswith("gh api"):
            return gh_code, merged, ""
        return 0, "", ""

    return fake_processes(answer)


def rest_body(answer, line, read, **kwargs):
    """The REST read of the PR (`gh api repos/o/r/pulls/7`) answering `read` as the body read once the branch is rebased, the world's answer before."""
    code, out, err = answer(line, **kwargs)
    rebased = answer("git rev-parse --verify HEAD", **kwargs)[1].strip() == PUSHED_HEAD
    if code or not rebased:
        return code, out, err
    if read[0] or not read[1].lstrip().startswith("{"):
        return read
    return code, json.dumps({**json.loads(out), **json.loads(read[1])}), err


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

    pushes = [c.rsplit(" ", 1)[0] for c in calls if " push " in c and "--delete" not in c and "v0." not in c]
    assert (code, pushes) == (0, ["merge-lock.sh gate --keep --pid %s -- git -C /wt push --force-with-lease=feature:%s origin"
                                  % (PID, ORIGIN_SHA)])


def test_2372_queued_merge_waits_for_ci_through_wait_ci_on_the_pushed_head_after_the_push_and_merges_that_head(fake_processes, run_cli):
    calls = scenario(fake_processes)

    code, _, _ = run_cli(queued_merge, ARGV, env={"VERI_GH_DRIVER": "graphql"})

    push, wait = first(calls, "--force-with-lease"), first(calls, "wait-ci.sh")
    waits = [c for c in calls if "wait-ci.sh" in c]
    merges = [c for c in calls if "pr merge" in c]
    assert (code, push is not None and wait is not None and push < wait, waits, merges) == (
        0, True, ["merge-lock.sh gate --pid %s -- %s %s 540  %s" % (PID, WAIT_CI, PR, PUSHED_HEAD)],
        ["merge-lock.sh gate --keep --pid %s -- gh pr merge %s --rebase --match-head-commit %s" % (PID, PR, PUSHED_HEAD)])


def test_2372_queued_merge_on_red_ci_exits_1_through_the_releasing_gate_and_never_merges(fake_processes, run_cli):
    calls = scenario(fake_processes, ci=(1,))

    code, _, _ = run_cli(queued_merge, ARGV)

    waits = [c for c in calls if "wait-ci.sh" in c]
    assert (code, [("--keep" in c) for c in waits], first(calls, "pr merge")) == (1, [False], None)


@pytest.mark.parametrize("ci, expected", [((3, 3, 0), 0), ((3, 2), 2), ((3, 3, 1), 1)])
def test_2372_queued_merge_treats_pending_or_absent_checks_as_not_green_and_asks_wait_ci_again(fake_processes, run_cli, ci, expected):
    calls = scenario(fake_processes, ci=ci)

    code, _, _ = run_cli(queued_merge, ARGV, env={"VERI_GH_DRIVER": "graphql"})

    asked = len([c for c in calls if "wait-ci.sh" in c])
    merged_after = first(calls, "pr merge") is not None
    assert (code, asked, merged_after) == (expected, len(ci), expected == 0)


def test_3978_queued_merge_whose_wait_ci_exits_2_on_a_head_that_never_matched_exits_2_through_the_releasing_gate_and_makes_no_merge_call(fake_processes, run_cli):
    calls = scenario(fake_processes, ci=(3, 3, 2))

    code, _, _ = run_cli(queued_merge, ARGV)

    waits = [c for c in calls if "wait-ci.sh" in c]
    merges = [c for c in calls if "pr merge" in c or "pulls/7/merge" in c]
    keeps_after_wait = [c for c in calls[first(calls, "wait-ci.sh"):] if c.startswith("merge-lock.sh") and "wait-ci.sh" not in c]
    assert (code, [c.startswith("merge-lock.sh gate --pid") for c in waits], merges, keeps_after_wait) == (2, [True] * 3, [], [])


@pytest.mark.parametrize("take", [2, 1])
def test_2372_queued_merge_whose_take_fails_stops_with_takes_code_and_touches_nothing(fake_processes, run_cli, take):
    calls = scenario(fake_processes, take=take)

    code, _, _ = run_cli(queued_merge, ARGV)

    assert (code, [c.split()[1] for c in calls]) == (take, ["take"])


def test_3994_queued_merge_whose_take_exits_2_on_a_stale_holder_exits_2_naming_the_take_and_makes_no_fetch_push_merge_or_release(
        fake_processes, run_cli):
    calls = fake_processes(lambda line, **_: (2, "", "stale lock: 4242 host t; clear it with merge-lock.sh release --force\n")
                           if line.startswith("merge-lock.sh take") else (0, "", ""))

    code, _, err = run_cli(queued_merge, ARGV)

    assert (code, calls, "queued-merge: taking the merge lock failed (exit 2)" in err) == (
        2, ["merge-lock.sh take --pid %s" % PID], True)


@pytest.mark.parametrize("merged, gh_code, expected", [
    (json.dumps({"merged": None}), 0, 1),
    (json.dumps({"state": "closed"}), 0, 1),
    (json.dumps({"merged": "true"}), 0, 1),
    ("not json", 0, 2),
    ("", 1, 1),
])
def test_2372_queued_merge_proceeds_to_tag_and_cleanup_only_on_an_observed_merged_true(fake_processes, run_cli, merged, gh_code, expected):
    calls = scenario(fake_processes, merged=merged, gh_code=gh_code)

    code, _, err = run_cli(queued_merge, ARGV, env={"VERI_MERGE_SETTLE_READS": "2", "VERI_MERGE_SETTLE_SLEEP": "0"})

    released = [c for c in calls if c.startswith("merge-lock.sh release")]
    assert (code, PR in err, cleaned(calls), len(released)) == (expected, True, [], 1)


@pytest.mark.parametrize("failing, named", [
    ("push origin --delete feature", "branch delete"),
    ("worktree remove", "worktree remove"),
    ("merge-lock.sh release", "release"),
    ("tag -a", "tag"),
])
def test_2372_queued_merge_reports_a_failed_cleanup_step_on_stderr_and_exits_2_running_the_rest(fake_processes, run_cli, failing, named):
    calls = scenario(fake_processes, fail=(failing,))

    code, _, err = run_cli(queued_merge, ARGV)

    ran = {step: first(calls, needle) is not None for step, needle in (
        ("branch delete", "--delete feature"), ("worktree remove", "worktree remove"), ("release", "merge-lock.sh release"))}
    assert (code, named in err, ran) == (2, True, {"branch delete": True, "worktree remove": True, "release": True})


def test_2372_queued_merge_tags_the_merge_commit_github_reports_for_the_pr_fetched_after_the_merge(fake_processes, run_cli):
    calls = scenario(fake_processes)

    code, _, _ = run_cli(queued_merge, ARGV, env={"VERI_GH_DRIVER": "graphql"})

    tags = [c for c in calls if " tag -a " in c]
    fetches = [i for i, c in enumerate(calls) if c.endswith("fetch origin")]
    merge = first(calls, "pr merge")
    assert (code, tags, any(i > merge for i in fetches)) == (
        0, ["git -C /wt tag -a v0.11 -m the capability %s" % MERGE_SHA], True)


def test_2372_queued_merge_whose_worktree_lacks_a_commit_on_origin_branch_exits_2_naming_it_and_pushes_nothing(fake_processes, run_cli):
    calls = scenario(fake_processes, diverged=True)

    code, _, err = run_cli(queued_merge, ARGV)

    pushes = [c for c in calls if " push " in c]
    released = [c for c in calls if c.startswith("merge-lock.sh release")]
    assert (code, "origin/feature" in err, pushes, first(calls, "rebase"), len(released)) == (2, True, [], None, 1)


def test_3030_queued_merge_on_a_dirty_worktree_strictly_behind_origin_branch_exits_2_naming_it_and_never_rebases_or_pushes(fake_processes, run_cli):
    calls = scenario(fake_processes, behind=True, dirty=True)

    code, _, err = run_cli(queued_merge, ARGV)

    pushes = [c for c in calls if " push " in c]
    released = [c for c in calls if c.startswith("merge-lock.sh release")]
    assert (code, "has commits the worktree lacks" in err, pushes, first(calls, "rebase"), len(released)) == (2, True, [], None, 1)


def test_3030_queued_merge_on_a_clean_worktree_strictly_behind_origin_branch_fast_forwards_then_rebases_and_pushes_under_the_lease_pinned_to_that_tip(fake_processes, run_cli):
    calls = scenario(fake_processes, behind=True)

    code, _, _ = run_cli(queued_merge, ARGV)

    pushes = [c.rsplit(" ", 1)[0] for c in calls if " push " in c and "--delete" not in c and "v0." not in c]
    assert (code, first(calls, "rebase origin/main") is not None, pushes) == (
        0, True, ["merge-lock.sh gate --keep --pid %s -- git -C /wt push --force-with-lease=feature:%s origin"
                  % (PID, ORIGIN_SHA)])


def test_3030_queued_merge_on_a_clean_worktree_strictly_behind_origin_branch_whose_fast_forward_fails_exits_2_and_pushes_nothing(fake_processes, run_cli):
    calls = scenario(fake_processes, behind=True, fail=("merge --ff-only",))

    code, _, err = run_cli(queued_merge, ARGV)

    pushes = [c for c in calls if " push " in c]
    forwards = [c for c in calls if "merge --ff-only" in c]
    assert (code, "has commits the worktree lacks" in err, forwards, pushes, first(calls, "rebase")) == (
        2, True, ["git -C /wt merge --ff-only " + ORIGIN_SHA], [], None)


def test_2372_queued_merge_releases_the_lock_only_after_the_tag_branch_delete_and_worktree_remove(fake_processes, run_cli):
    calls = scenario(fake_processes)

    code, _, _ = run_cli(queued_merge, ARGV)

    release = first(calls, "merge-lock.sh release")
    steps = [first(calls, needle) for needle in (" tag -a ", "push origin v0.11", "--delete feature", "worktree remove")]
    assert (code, None not in steps and release is not None and release > max(steps)) == (0, True)


def test_2372_queued_merge_whose_origin_branch_sha_is_unreadable_exits_2_naming_the_branch_pushes_nothing_and_frees_the_lock(fake_processes, run_cli):
    calls = scenario(fake_processes, lease_readable=False)

    code, _, err = run_cli(queued_merge, ARGV)

    pushes = [c for c in calls if " push " in c]
    released = [c for c in calls if c.startswith("merge-lock.sh release")]
    assert (code, "origin/feature" in err, pushes, first(calls, "rebase"), len(released)) == (2, True, [], None, 1)


@pytest.mark.parametrize("merged, fail, named", [
    (json.dumps({"merged": True}), (), "GitHub reports no merge commit"),
    (json.dumps({"merged": True, "merge_commit_sha": None}), (), "GitHub reports no merge commit"),
    (json.dumps({"merged": True, "merge_commit_sha": "fedcba9"}), ("cat-file -e",), "not in the clone"),
])
def test_2372_queued_merge_with_no_reported_merge_commit_or_one_the_clone_lacks_cuts_no_tag_names_why_exits_2_and_frees_the_lock(
        fake_processes, run_cli, merged, fail, named):
    calls = scenario(fake_processes, merged=merged, fail=fail)

    code, _, err = run_cli(queued_merge, ARGV, env={"VERI_FETCH_RETRY_SLEEP": "0"})

    tagged = [c for c in calls if " tag -a " in c or "push origin v0." in c]
    released = [c for c in calls if c.startswith("merge-lock.sh release")]
    assert (code, named in err, tagged, len(released)) == (2, True, [], 1)


def test_2695_queued_merge_whose_merge_commit_never_shows_up_after_any_fetch_names_it_lists_tag_in_the_cleanup_summary_and_exits_2(
        fake_processes, run_cli):
    calls = scenario(fake_processes, fail=("cat-file -e",))

    code, _, err = run_cli(queued_merge, ARGV, env={"VERI_FETCH_RETRY_SLEEP": "0"})

    tagged = [c for c in calls if " tag -a " in c or "push origin v0." in c]
    assert (code, "is not in the clone after a fetch" in err, "merged, but cleanup failed: tag" in err, tagged) == (
        2, True, True, [])


def test_2695_queued_merge_whose_merge_commit_is_absent_after_the_first_fetch_and_present_after_a_later_one_tags_it_pushes_the_tag_and_exits_0(
        fake_processes, run_cli):
    seen = {"cat-file": 0}

    def lagging(answer):
        def lag(line, **kwargs):
            if "cat-file -e" in line:
                seen["cat-file"] += 1
                return (1, "", "") if seen["cat-file"] == 1 else (0, "", "")
            return answer(line, **kwargs)
        return fake_processes(lag)

    calls = scenario(lagging)

    code, _, _ = run_cli(queued_merge, ARGV, env={"VERI_FETCH_RETRY_SLEEP": "0"})

    tags = [c for c in calls if " tag -a " in c or "push origin v0." in c]
    assert (code, tags) == (0, ["git -C /wt tag -a v0.11 -m the capability %s" % MERGE_SHA, "git -C /wt push origin v0.11"])


def test_2695_queued_merge_waits_for_fetch_retry_sleep_between_fetches_of_a_lagging_merge_commit_and_not_before_the_first(
        fake_processes, run_cli, monkeypatch):
    seen = {"cat-file": 0}
    waits = []

    def lagging(answer):
        def lag(line, **kwargs):
            if "cat-file -e" in line:
                seen["cat-file"] += 1
                return (1, "", "") if seen["cat-file"] == 1 else (0, "", "")
            return answer(line, **kwargs)
        return fake_processes(lag)

    scenario(lagging)
    monkeypatch.setattr(queued_merge.time, "sleep", waits.append)

    code, _, _ = run_cli(queued_merge, ARGV, env={"VERI_FETCH_RETRY_SLEEP": "0.25"})

    assert (code, waits) == (0, [0.25])


def test_2695_queued_merge_whose_fetch_origin_exits_non_zero_after_the_merge_names_the_failed_fetch_and_its_exit_code_not_a_missing_commit_and_lists_tag_failed_with_exit_2(
        fake_processes, run_cli):
    merged = {"put": False}

    def broken(answer):
        def fetch(line, **kwargs):
            if "-X PUT" in line:
                merged["put"] = True
            if merged["put"] and line.endswith("fetch origin"):
                return 128, "", "fatal: unable to access"
            return answer(line, **kwargs)
        return fake_processes(fetch)

    calls = scenario(broken)

    code, _, err = run_cli(queued_merge, ARGV, env={"VERI_FETCH_RETRY_SLEEP": "0"})

    tagged = [c for c in calls if " tag -a " in c or "push origin v0." in c]
    assert (code, "fetch" in err and "128" in err, "is not in the clone" in err, "merged, but cleanup failed: tag" in err, tagged) == (
        2, True, False, True, [])


def test_2425_queued_merge_refuses_a_pr_argument_that_is_not_a_pr_url_before_any_lock_or_git(fake_processes, run_cli):
    calls = scenario(fake_processes)

    code, _, err = run_cli(queued_merge, ["2415", "/wt", "feature", "the capability"])

    assert (code, "<pr-url>" in err, calls) == (2, True, [])


def test_2425_queued_merge_deletes_the_local_branch_from_the_main_clone_after_the_worktree_is_removed(fake_processes, run_cli):
    calls = scenario(fake_processes)

    code, _, _ = run_cli(queued_merge, ARGV)

    removed = first(calls, "worktree remove")
    local = [i for i, c in enumerate(calls) if c.startswith("git -C /main ") and " branch " in c and c.endswith(" feature")]
    assert (code, len(local), bool(local) and local[0] > removed) == (0, 1, True)


def test_2425_queued_merge_fast_forwards_the_main_clones_main_to_origin_main_with_ff_only_after_the_tag_and_the_lock_release(fake_processes, run_cli):
    calls = scenario(fake_processes)

    code, _, _ = run_cli(queued_merge, ARGV)

    forwards = [i for i, c in enumerate(calls) if c.startswith("git -C /main ") and "--ff-only" in c and c.endswith("origin/main")]
    tagged = first(calls, " tag -a ")
    released = first(calls, "merge-lock.sh release")
    assert (code, len(forwards), bool(forwards) and forwards[0] > max(tagged, released)) == (0, 1, True)


def test_2425_queued_merge_whose_main_clone_cannot_fast_forward_reports_it_on_stderr_and_exits_non_zero_after_the_tag_and_the_lock_release(fake_processes, run_cli):
    calls = scenario(fake_processes, fail=("--ff-only",))

    code, _, err = run_cli(queued_merge, ARGV)

    tagged = first(calls, " tag -a ")
    released = first(calls, "merge-lock.sh release")
    attempt = first(calls, "--ff-only")
    assert (code != 0, "origin/main" in err, max(tagged, released) < attempt) == (True, True, True)


def test_2455_queued_merge_whose_local_branch_delete_fails_names_it_on_stderr_lists_it_in_the_cleanup_summary_and_exits_2(fake_processes, run_cli):
    scenario(fake_processes, fail=("branch -D",))

    code, _, err = run_cli(queued_merge, ARGV)

    assert (code, "branch -D refused" in err, "merged, but cleanup failed" in err) == (2, True, True)


def test_2455_queued_merge_that_succeeds_exits_0_and_deletes_the_local_branch_with_branch_dash_d_exactly_once_after_the_worktree_remove(fake_processes, run_cli):
    calls = scenario(fake_processes)

    code, _, err = run_cli(queued_merge, ARGV)

    removed = first(calls, "worktree remove")
    deletes = [i for i, c in enumerate(calls) if c == "git -C /main branch -D feature"]
    assert (code, err, len(deletes), bool(deletes) and removed is not None and deletes[0] > removed) == (0, "", 1, True)


def test_2455_queued_merge_whose_main_clone_is_on_another_branch_does_not_fast_forward_it_names_why_and_lists_the_fast_forward_in_the_cleanup_summary(fake_processes, run_cli):
    def on_scratch(answer):
        def wrapped(line, **kw):
            if line.startswith("git -C /main ") and ("symbolic-ref" in line or "--abbrev-ref" in line or "--show-current" in line):
                return 0, "scratch\n", ""
            return answer(line, **kw)
        return fake_processes(wrapped)

    calls = scenario(on_scratch)

    code, _, err = run_cli(queued_merge, ARGV)

    moved = [c for c in calls if c.startswith("git -C /main ") and "--ff-only" in c]
    assert (code, moved, "scratch" in err, "cleanup failed: fast-forward" in err) == (2, [], True, True)


def test_2585_queued_merge_by_default_merges_through_one_rest_put_of_the_pushed_head_with_rebase_and_no_gh_pr_merge(fake_processes, run_cli):
    calls = scenario(fake_processes)

    code, _, _ = run_cli(queued_merge, ARGV)

    puts = [c for c in calls if "gh api" in c and "pulls/7/merge" in c]
    assert (code, len(puts), all("PUT" in c and "merge_method=rebase" in c and "sha=%s" % PUSHED_HEAD in c and "repos/o/r/pulls/7/merge" in c for c in puts),
            [c for c in calls if "pr merge" in c], len([c for c in calls if " tag -a " in c])) == (0, 1, True, [], 1)


def test_2585_queued_merge_by_default_exits_1_with_no_tag_branch_delete_or_worktree_removal_when_the_rest_merge_is_refused_because_the_head_moved(fake_processes, run_cli):
    calls = scenario(fake_processes, fail=("pulls/7/merge",))

    code, _, _ = run_cli(queued_merge, ARGV, env={"VERI_MERGE_SETTLE_READS": "3", "VERI_MERGE_SETTLE_SLEEP": "0"})

    puts = [c for c in calls if "pulls/7/merge" in c]
    assert (code, len(puts), cleaned(calls)) == (1, 1, [])


def test_3500_queued_merge_whose_merge_call_fails_and_never_lands_holds_the_lock_through_the_settle_reads_and_releases_it_exactly_once_after_the_last(fake_processes, run_cli):
    calls = scenario(fake_processes, fail=("pulls/7/merge",))

    code, _, _ = run_cli(queued_merge, ARGV, env={"VERI_MERGE_SETTLE_READS": "3", "VERI_MERGE_SETTLE_SLEEP": "0"})

    put = first(calls, "pulls/7/merge")
    reads = [i for i, c in enumerate(calls) if i > put and c.endswith("gh api repos/o/r/pulls/7")]
    released = [i for i, c in enumerate(calls) if c.startswith("merge-lock.sh release")]
    assert (code, "--keep" in calls[put], len(reads), len(released), bool(reads) and released[-1:] > reads[-1:]) == (
        1, True, 3, 1, True)


def test_3500_queued_merge_whose_merge_call_fails_while_the_pr_still_reads_open_rereads_it_across_the_settle_window_then_exits_with_the_merge_calls_own_code_with_nothing_cleaned(fake_processes, run_cli):
    def failing_with_4(answer):
        def wrapped(line, **kw):
            if "pulls/7/merge" in line:
                return 4, "", "HTTP 502"
            return answer(line, **kw)
        return fake_processes(wrapped)

    calls = scenario(failing_with_4)

    code, _, _ = run_cli(queued_merge, ARGV, env={"VERI_MERGE_SETTLE_READS": "3", "VERI_MERGE_SETTLE_SLEEP": "0"})

    put = first(calls, "pulls/7/merge")
    rereads = [c for c in calls[put + 1:] if c.endswith("gh api repos/o/r/pulls/7")]
    assert (code, len(rereads), cleaned(calls)) == (4, 3, [])


def test_3500_queued_merge_under_the_auto_driver_whose_gh_pr_merge_and_rest_put_both_fail_while_the_pr_still_reads_open_exits_1_releasing_the_lock_once_after_the_settle_reads_and_nothing_cleaned(fake_processes, run_cli):
    calls = scenario(fake_processes, fail=("pr merge", "pulls/7/merge"))

    code, _, _ = run_cli(queued_merge, ARGV, env={"VERI_GH_DRIVER": "auto", "VERI_MERGE_SETTLE_READS": "2", "VERI_MERGE_SETTLE_SLEEP": "0"})

    put = first(calls, "PUT")
    reads = [i for i, c in enumerate(calls) if put is not None and i > put and c.endswith("gh api repos/o/r/pulls/7")]
    released = [i for i, c in enumerate(calls) if c.startswith("merge-lock.sh release")]
    assert (code, "--keep" in calls[put], len(reads), len(released), bool(reads) and released[-1:] > reads[-1:], cleaned(calls)) == (
        1, True, 2, 1, True, [])


def test_3500_queued_merge_under_the_auto_driver_whose_gh_pr_merge_fails_runs_it_through_the_keeping_gate_so_the_rest_fallback_still_holds_the_lock(fake_processes, run_cli):
    calls = scenario(fake_processes, fail=("pr merge", "pulls/7/merge"))

    run_cli(queued_merge, ARGV, env={"VERI_GH_DRIVER": "auto", "VERI_MERGE_SETTLE_READS": "1", "VERI_MERGE_SETTLE_SLEEP": "0"})

    merges = [c for c in calls if "pr merge" in c]
    assert ["--keep" in c for c in merges] == [True]


def test_3500_queued_merge_whose_first_fetch_fails_exits_1_through_the_releasing_gate_and_makes_no_merge_call(fake_processes, run_cli):
    calls = scenario(fake_processes, fail=("fetch origin",))

    code, _, _ = run_cli(queued_merge, ARGV)

    fetches = [c for c in calls if c.endswith("fetch origin")]
    assert (code, ["--keep" in c for c in fetches], [c for c in calls if "pr merge" in c or "pulls/7/merge" in c]) == (1, [False], [])


def test_3500_queued_merge_whose_merge_call_fails_but_whose_pr_reads_merged_on_the_first_reread_exits_0_and_tags_deletes_the_branch_and_removes_the_worktree(fake_processes, run_cli):
    landed = []

    def landing(answer):
        def wrapped(line, **kw):
            if "pulls/7/merge" in line:
                landed.append(line)
                return 1, "", "502 Bad Gateway"
            if landed and line.endswith("gh api repos/o/r/pulls/7"):
                return 0, json.dumps({"merged": True, "merge_commit_sha": MERGE_SHA}), ""
            return answer(line, **kw)
        return fake_processes(wrapped)

    calls = scenario(landing)

    code, _, _ = run_cli(queued_merge, ARGV, env={"VERI_MERGE_SETTLE_SLEEP": "0"})

    assert (code, len(cleaned(calls))) == (0, 3)


def test_3500_queued_merge_whose_pr_reads_merged_on_a_reread_after_a_failed_merge_call_keeps_that_answer_when_a_later_read_would_say_open(fake_processes, run_cli):
    landed = []
    reads = []

    def landing(answer):
        def wrapped(line, **kw):
            if "pulls/7/merge" in line:
                landed.append(line)
                return 1, "", "502 Bad Gateway"
            if landed and line.endswith("gh api repos/o/r/pulls/7"):
                reads.append(line)
                if len(reads) == 1:
                    return 0, json.dumps({"merged": True, "merge_commit_sha": MERGE_SHA}), ""
                return 0, json.dumps({"state": "open", "merged": False}), ""
            return answer(line, **kw)
        return fake_processes(wrapped)

    calls = scenario(landing)

    code, _, _ = run_cli(queued_merge, ARGV, env={"VERI_MERGE_SETTLE_SLEEP": "0"})

    assert (code, len(cleaned(calls)), len(reads)) == (0, 3, 1)


def test_3500_queued_merge_whose_pr_reads_open_on_the_first_reread_after_a_failed_merge_call_but_merged_on_a_later_one_within_the_settle_reads_exits_0_and_cleans_up(fake_processes, run_cli):
    landed = []
    reads = []

    def landing(answer):
        def wrapped(line, **kw):
            if "pulls/7/merge" in line:
                landed.append(line)
                return 1, "", "502 Bad Gateway"
            if landed and line.endswith("gh api repos/o/r/pulls/7"):
                reads.append(line)
                if len(reads) < 3:
                    return 0, json.dumps({"state": "open", "merged": False}), ""
                return 0, json.dumps({"merged": True, "merge_commit_sha": MERGE_SHA}), ""
            return answer(line, **kw)
        return fake_processes(wrapped)

    calls = scenario(landing)

    code, _, _ = run_cli(queued_merge, ARGV, env={"VERI_MERGE_SETTLE_READS": "5", "VERI_MERGE_SETTLE_SLEEP": "0"})

    assert (code, len(cleaned(calls)), len(reads)) == (0, 3, 3)


def settling(fake_processes, merge_code, answers):
    """A merge call exiting <merge_code>, then the PR reads after it answering <answers> in order (the last repeats):
    "fail" a read that gets no answer, "open" one that answers unmerged, "merged" one that answers merged."""
    after = []
    bodies = {"open": json.dumps({"state": "open", "merged": False}),
              "merged": json.dumps({"merged": True, "merge_commit_sha": MERGE_SHA})}

    def wrapped(answer):
        def inner(line, **kw):
            if "pulls/7/merge" in line:
                after.append(line)
                return merge_code, "", "" if merge_code == 0 else "gh: HTTP 502"
            if after and line.endswith("gh api repos/o/r/pulls/7"):
                read = answers[min(len(after) - 1, len(answers) - 1)]
                after.append(line)
                return (1, "", "gh: HTTP 502") if read == "fail" else (0, bodies[read], "")
            return answer(line, **kw)
        return fake_processes(inner)

    return scenario(wrapped)


def test_3979_queued_merge_whose_merge_call_exits_0_and_whose_first_read_gets_no_answer_but_the_second_reads_merged_exits_0_tagged_and_cleaned_up(fake_processes, run_cli):
    calls = settling(fake_processes, 0, ["fail", "merged"])

    code, _, _ = run_cli(queued_merge, ARGV, env={"VERI_MERGE_SETTLE_SLEEP": "0"})

    assert (code, len(cleaned(calls))) == (0, 3)


def test_3979_queued_merge_whose_merge_call_exits_0_and_whose_window_gets_no_answer_exits_2_saying_so_releases_the_lock_once_and_cleans_nothing(fake_processes, run_cli):
    calls = settling(fake_processes, 0, ["fail"])

    code, _, err = run_cli(queued_merge, ARGV, env={"VERI_MERGE_SETTLE_READS": "3", "VERI_MERGE_SETTLE_SLEEP": "0"})

    released = [c for c in calls if c.startswith("merge-lock.sh release")]
    assert (code, "merge call succeeded" in err and "could not be read" in err, len(released), cleaned(calls)) == (2, True, 1, [])


def test_3979_queued_merge_whose_merge_call_exits_0_and_whose_reads_answer_and_never_say_merged_exits_1_releasing_the_lock_once_after_the_window(fake_processes, run_cli):
    calls = settling(fake_processes, 0, ["fail", "open"])

    code, _, _ = run_cli(queued_merge, ARGV, env={"VERI_MERGE_SETTLE_READS": "3", "VERI_MERGE_SETTLE_SLEEP": "0"})

    reads = [i for i, c in enumerate(calls) if i > first(calls, "pulls/7/merge") and c.endswith("gh api repos/o/r/pulls/7")]
    released = [i for i, c in enumerate(calls) if c.startswith("merge-lock.sh release")]
    assert (code, len(reads), len(released), released[-1:] > reads[-1:], cleaned(calls)) == (1, 3, 1, True, [])


def test_3979_queued_merge_whose_merge_call_exits_non_zero_and_whose_window_gets_no_answer_exits_2_releasing_the_lock_once(fake_processes, run_cli):
    calls = settling(fake_processes, 1, ["fail"])

    code, _, _ = run_cli(queued_merge, ARGV, env={"VERI_MERGE_SETTLE_READS": "3", "VERI_MERGE_SETTLE_SLEEP": "0"})

    released = [c for c in calls if c.startswith("merge-lock.sh release")]
    assert (code, len(released), cleaned(calls)) == (2, 1, [])


def test_3979_queued_merge_whose_merge_call_exits_non_zero_and_whose_window_answered_unmerged_before_a_failed_read_exits_with_the_calls_code_releasing_the_lock_once(fake_processes, run_cli):
    calls = settling(fake_processes, 4, ["open", "fail"])

    code, _, _ = run_cli(queued_merge, ARGV, env={"VERI_MERGE_SETTLE_READS": "3", "VERI_MERGE_SETTLE_SLEEP": "0"})

    released = [c for c in calls if c.startswith("merge-lock.sh release")]
    assert (code, len(released), cleaned(calls)) == (4, 1, [])


def test_3500_queued_merge_with_no_settle_tunables_set_rereads_an_open_pr_ten_times_each_after_a_three_second_wait(fake_processes, run_cli, monkeypatch):
    calls = scenario(fake_processes, fail=("pulls/7/merge",))
    waits = []
    monkeypatch.setattr(queued_merge.time, "sleep", waits.append)

    code, _, _ = run_cli(queued_merge, ARGV)

    put = first(calls, "pulls/7/merge")
    rereads = [c for c in calls[put + 1:] if c.endswith("gh api repos/o/r/pulls/7")]
    assert (code, len(rereads), waits, cleaned(calls)) == (1, 10, [3.0] * 10, [])


def test_2585_queued_merge_under_the_graphql_driver_merges_with_gh_pr_merge_match_head_commit_and_makes_no_rest_put(fake_processes, run_cli):
    calls = scenario(fake_processes)

    code, _, _ = run_cli(queued_merge, ARGV, env={"VERI_GH_DRIVER": "graphql"})

    merges = [c for c in calls if "pr merge" in c]
    puts = [c for c in calls if "PUT" in c or "pulls/7/merge" in c]
    assert (code, merges, puts) == (
        0, ["merge-lock.sh gate --keep --pid %s -- gh pr merge %s --rebase --match-head-commit %s" % (PID, PR, PUSHED_HEAD)], [])


def test_2585_queued_merge_under_the_auto_driver_tries_gh_pr_merge_first_and_when_it_fails_falls_back_to_one_rest_put_of_the_pushed_head_then_tags_and_exits_0(fake_processes, run_cli):
    calls = scenario(fake_processes, fail=("pr merge",))

    code, _, _ = run_cli(queued_merge, ARGV, env={"VERI_GH_DRIVER": "auto"})

    merges = [i for i, c in enumerate(calls) if "gh pr merge %s --rebase --match-head-commit %s" % (PR, PUSHED_HEAD) in c]
    puts = [i for i, c in enumerate(calls) if "PUT" in c and "merge_method=rebase" in c and "sha=%s" % PUSHED_HEAD in c and "repos/o/r/pulls/7/merge" in c]
    assert (code, len(merges), len(puts), merges[0] < puts[0] if merges and puts else None, len([c for c in calls if " tag -a " in c])) == (0, 1, 1, True, 1)


def test_2585_queued_merge_refuses_a_driver_other_than_auto_rest_or_graphql_with_exit_2_naming_the_value_and_makes_no_merge_call(fake_processes, run_cli):
    calls = scenario(fake_processes)

    code, _, err = run_cli(queued_merge, ARGV, env={"VERI_GH_DRIVER": "rst"})

    merges = [c for c in calls if "pr merge" in c or "PUT" in c or "pulls/7/merge" in c]
    assert (code, "VERI_GH_DRIVER is 'rst': expected auto, rest or graphql" in err, merges) == (2, True, [])


def test_2585_queued_merge_under_an_explicit_rest_driver_merges_through_one_rest_put_of_the_pushed_head_and_no_gh_pr_merge(fake_processes, run_cli):
    calls = scenario(fake_processes)

    code, _, _ = run_cli(queued_merge, ARGV, env={"VERI_GH_DRIVER": "rest"})

    puts = [c for c in calls if "gh api" in c and "pulls/7/merge" in c]
    assert (code, len(puts), all("PUT" in c and "merge_method=rebase" in c and "sha=%s" % PUSHED_HEAD in c and "repos/o/r/pulls/7/merge" in c for c in puts),
            [c for c in calls if "pr merge" in c], len([c for c in calls if " tag -a " in c])) == (0, 1, True, [], 1)


def test_2749_queued_merge_that_cuts_a_tag_emits_merged_with_pr_tag_and_message_before_the_worktree_is_removed(
        fake_processes, run_cli, tmp_path):
    BRANCH = "tdd/2749-prd-014-2"
    worktree = tmp_path / "wt"
    worktree.mkdir()
    events = worktree / ".tdd" / "events.jsonl"
    seen = {}

    def spied(answer):
        def wrapped(line, **kwargs):
            if "worktree remove" in line:
                seen["before_remove"] = events.read_text() if events.exists() else ""
            return answer(line.replace(BRANCH, "feature"), **kwargs)
        return fake_processes(wrapped)

    scenario(spied)

    code, _, _ = run_cli(queued_merge, [PR, str(worktree), BRANCH, "the capability"])

    rows = [json.loads(r) for r in seen.get("before_remove", "").splitlines()]
    merged = [(r["issue"], r["pr"], r["tag"], r["message"]) for r in rows if r.get("event") == "merged"]
    assert (code, merged) == (0, [("2749", PR, "v0.11", "the capability")])


def test_2749_queued_merge_given_a_dash_for_the_message_emits_merged_with_the_pr_and_an_empty_tag_and_message(
        fake_processes, run_cli, tmp_path):
    BRANCH = "tdd/2749-prd-014-2"
    worktree = tmp_path / "wt"
    worktree.mkdir()
    events = worktree / ".tdd" / "events.jsonl"
    seen = {}

    def spied(answer):
        def wrapped(line, **kwargs):
            if "worktree remove" in line:
                seen["before_remove"] = events.read_text() if events.exists() else ""
            return answer(line.replace(BRANCH, "feature"), **kwargs)
        return fake_processes(wrapped)

    scenario(spied)

    code, _, _ = run_cli(queued_merge, [PR, str(worktree), BRANCH, "-"])

    rows = [json.loads(r) for r in seen.get("before_remove", "").splitlines()]
    merged = [(r["issue"], r["pr"], r["tag"], r["message"]) for r in rows if r.get("event") == "merged"]
    assert (code, merged) == (0, [("2749", PR, "", "")])


@pytest.mark.parametrize("merged, deleted", [
    (json.dumps({"merged": True, "merge_commit_sha": "fedcba9"}), True),
    (json.dumps({"state": "open", "merged": False}), False),
])
def test_4079_queued_merge_deletes_refs_veri_runs_n_on_origin_once_the_pr_reads_merged_and_leaves_it_otherwise(
        fake_processes, run_cli, tmp_path, merged, deleted):
    branch = "tdd/4079-run-records"
    worktree = tmp_path / "wt"
    worktree.mkdir()
    calls = []

    def spied(answer):
        def wrapped(line, **kwargs):
            calls.append(line)
            return answer(line.replace(branch, "feature"), **kwargs)
        return fake_processes(wrapped)

    scenario(spied, merged=merged)

    run_cli(queued_merge, [PR, str(worktree), branch, "the capability"],
            env={"VERI_MERGE_SETTLE_READS": "2", "VERI_MERGE_SETTLE_SLEEP": "0"})

    assert any(line.endswith("push origin --delete refs/veri/runs/4079") for line in calls) is deleted


def test_2886_queued_merge_on_a_pr_with_no_checks_whose_rebase_leaves_head_unchanged_merges_without_running_the_full_test_command(
        fake_processes, run_cli):
    def unmoved(answer):
        def wrapped(line, **kwargs):
            if "rev-parse --verify HEAD" in line:
                return 0, PUSHED_HEAD + "\n", ""
            return answer(line, **kwargs)
        return fake_processes(wrapped)

    calls = scenario(unmoved)

    code, _, _ = run_cli(queued_merge, ARGV, env={"VERI_CI_ON_PR": "0"})

    full_runs = [c for c in calls if "detect-test-command" in c or "make test" in c]
    merges = [c for c in calls if "pulls/7/merge" in c]
    assert (code, full_runs, len(merges)) == (0, [], 1)


def test_2886_queued_merge_on_a_pr_with_checks_whose_rebase_moved_its_tip_merges_on_the_ci_verdict_without_running_the_full_test_command(
        fake_processes, run_cli):
    calls = scenario(fake_processes, ci=(0,))

    code, _, _ = run_cli(queued_merge, ARGV, env={"VERI_CI_ON_PR": "1"})

    full_runs = [c for c in calls if "detect-test-command" in c or "make test" in c]
    merges = [c for c in calls if "pulls/7/merge" in c]
    assert (code, full_runs, len(merges)) == (0, [], 1)


def test_2886_queued_merge_on_a_pr_with_no_checks_whose_rebase_moved_its_tip_never_merges_when_the_full_test_command_is_red_and_names_the_run(
        fake_processes, run_cli):
    def red_full_run(answer):
        def wrapped(line, **kwargs):
            if "detect-test-command" in line:
                return 0, "make test\n", ""
            if "make test" in line:
                return 1, "", "FAILED test_combined"
            return answer(line, **kwargs)
        return fake_processes(wrapped)

    calls = scenario(red_full_run)

    code, _, err = run_cli(queued_merge, ARGV, env={"VERI_CI_ON_PR": "0"})

    merges = [c for c in calls if "pulls/7/merge" in c or "pr merge" in c]
    released = [c for c in calls if c.startswith("merge-lock.sh release")]
    assert (code, merges, len(released), "make test" in err) == (1, [], 1, True)


def test_2886_queued_merge_on_a_pr_with_no_checks_whose_rebase_moved_its_tip_merges_the_pushed_head_when_the_full_test_command_is_green(
        fake_processes, run_cli):
    def green_full_run(answer):
        def wrapped(line, **kwargs):
            if "detect-test-command" in line:
                return 0, "make test\n", ""
            if "make test" in line:
                return 0, "", ""
            return answer(line, **kwargs)
        return fake_processes(wrapped)

    calls = scenario(green_full_run)

    code, _, _ = run_cli(queued_merge, ARGV, env={"VERI_CI_ON_PR": "0"})

    full_runs = [c for c in calls if "make test" in c]
    merges = [c for c in calls if "pulls/7/merge" in c and "sha=%s" % PUSHED_HEAD in c]
    assert (code, len(full_runs), len(merges)) == (0, 1, 1)


def test_2886_queued_merge_on_a_pr_with_no_checks_whose_rebase_moved_its_tip_never_merges_when_the_full_test_command_is_empty_and_names_the_cause(
        fake_processes, run_cli):
    def empty_detection(answer):
        def wrapped(line, **kwargs):
            if "detect-test-command" in line:
                return 0, "  \n", ""
            return answer(line, **kwargs)
        return fake_processes(wrapped)

    calls = scenario(empty_detection)

    code, _, err = run_cli(queued_merge, ARGV, env={"VERI_CI_ON_PR": "0"})

    merges = [c for c in calls if "pulls/7/merge" in c or "pr merge" in c]
    shells = [c for c in calls if c.startswith("sh -c")]
    released = [c for c in calls if c.startswith("merge-lock.sh release")]
    assert (code, merges, shells, len(released), "printed nothing" in err) == (2, [], [], 1, True)


def test_2886_queued_merge_on_a_pr_with_no_checks_whose_rebase_moved_its_tip_never_merges_when_detecting_the_full_test_command_fails_and_names_the_exit_code(
        fake_processes, run_cli):
    def failed_detection(answer):
        def wrapped(line, **kwargs):
            if "detect-test-command" in line:
                return 4, "make test\n", "boom"
            return answer(line, **kwargs)
        return fake_processes(wrapped)

    calls = scenario(failed_detection)

    code, _, err = run_cli(queued_merge, ARGV, env={"VERI_CI_ON_PR": "0"})

    merges = [c for c in calls if "pulls/7/merge" in c or "pr merge" in c]
    shells = [c for c in calls if c.startswith("sh -c")]
    released = [c for c in calls if c.startswith("merge-lock.sh release")]
    assert (code, merges, shells, len(released), "exited 4" in err) == (2, [], [], 1, True)


def test_3022_queued_merge_whose_rebase_stops_with_would_be_overwritten_on_a_really_dirty_tree_fails_with_gits_code_keeps_the_lock_and_neither_refreshes_the_index_nor_continues(fake_processes, run_cli):
    def dirty_world(answer):
        def world(line, **kwargs):
            if "status --porcelain" in line:
                return 0, " M skills/tdd/scripts/veri/queued_merge.py\n", ""
            if "rebase origin/main" in line:
                return 1, "", PHANTOM
            return answer(line, **kwargs)
        return fake_processes(world)

    calls = scenario(dirty_world)

    code, _, _ = run_cli(queued_merge, ARGV)

    ran = [c for c in calls if "update-index" in c or "rebase --continue" in c or " push " in c or "merge-lock.sh release" in c]
    assert (code, ran) == (1, [])


def test_3022_queued_merge_whose_rebase_stops_on_a_real_conflict_fails_with_gits_code_keeps_the_lock_pushes_nothing_and_neither_refreshes_the_index_nor_continues(fake_processes, run_cli):
    def conflict_world(answer):
        def world(line, **kwargs):
            if "status --porcelain" in line:
                return 0, "UU skills/tdd/scripts/veri/queued_merge.py\n", ""
            if "rebase origin/main" in line:
                return 1, "", "CONFLICT (content): Merge conflict in skills/tdd/scripts/veri/queued_merge.py\n"
            return answer(line, **kwargs)
        return fake_processes(world)

    calls = scenario(conflict_world)

    code, _, _ = run_cli(queued_merge, ARGV)

    ran = [c for c in calls if "update-index" in c or "rebase --continue" in c or " push " in c or "merge-lock.sh release" in c]
    assert (code, ran) == (1, [])


PHANTOM = "error: Your local changes to the following files would be overwritten by merge:\n"


def test_3022_queued_merge_whose_rebase_first_stops_on_a_phantom_would_be_overwritten_with_a_clean_status_refreshes_the_index_continues_the_rebase_and_pushes(fake_processes, run_cli):
    def phantom_world(answer):
        stopped = []

        def world(line, **kwargs):
            if "status --porcelain" in line:
                return 0, "", ""
            if "rebase origin/main" in line and not stopped:
                stopped.append(answer(line, **kwargs))
                return 1, "", PHANTOM
            return answer(line, **kwargs)
        return fake_processes(world)

    calls = scenario(phantom_world)

    code, _, _ = run_cli(queued_merge, ARGV)

    ran = [needle for c in calls if "--delete" not in c
           for needle in ("update-index --really-refresh", "rebase --continue", "--force-with-lease") if needle in c]
    assert (code, ran) == (0, ["update-index --really-refresh", "rebase --continue", "--force-with-lease"])


def test_3022_queued_merge_whose_rebase_stops_on_two_phantoms_appends_one_retry_event_per_refresh_and_continue_to_events_jsonl(fake_processes, run_cli, tmp_path):
    BRANCH = "tdd/3022-phantom"
    worktree = tmp_path / "wt"
    worktree.mkdir()
    events = worktree / ".tdd" / "events.jsonl"

    def phantom_world(answer):
        stops = []

        def world(line, **kwargs):
            line = line.replace(BRANCH, "feature")
            if "status --porcelain" in line:
                return 0, "", ""
            if ("rebase origin/main" in line or "rebase --continue" in line) and len(stops) < 2:
                stops.append(line)
                return 1, "", PHANTOM
            return answer(line, **kwargs)
        return fake_processes(world)

    scenario(phantom_world)

    code, _, _ = run_cli(queued_merge, [PR, str(worktree), BRANCH, "-"])

    rows = [json.loads(r) for r in events.read_text().splitlines()] if events.exists() else []
    retries = [r["event"] for r in rows if r.get("event") != "merged"]
    assert (code, retries) == (0, ["rebase-refresh-retry"] * 2)


def test_3022_queued_merge_whose_phantom_would_be_overwritten_stop_recurs_past_the_retry_bound_fails_with_gits_code_keeps_the_lock_and_pushes_nothing(fake_processes, run_cli):

    def phantom_world(answer):
        stops = []

        def world(line, **kwargs):
            if "status --porcelain" in line:
                return 0, "", ""
            if ("rebase origin/main" in line or "rebase --continue" in line) and len(stops) < 50:
                stops.append(line)
                return 1, "", PHANTOM
            return answer(line, **kwargs)
        return fake_processes(world)

    calls = scenario(phantom_world)

    code, _, _ = run_cli(queued_merge, ARGV)

    ran = [c for c in calls if " push " in c or "--force-with-lease" in c or "merge-lock.sh release" in c]
    assert (code, ran) == (1, [])


def test_3022_queued_merge_whose_rebase_stops_non_zero_on_a_clean_status_with_other_output_fails_with_gits_code_keeps_the_lock_and_neither_refreshes_the_index_nor_records_a_retry(fake_processes, run_cli, tmp_path):
    BRANCH = "tdd/3022-other-stop"
    worktree = tmp_path / "wt"
    worktree.mkdir()
    events = worktree / ".tdd" / "events.jsonl"

    def other_stop_world(answer):
        def world(line, **kwargs):
            line = line.replace(BRANCH, "feature")
            if "status --porcelain" in line:
                return 0, "", ""
            if "rebase origin/main" in line:
                return 1, "", "error: could not apply 1234567... some commit\n"
            return answer(line, **kwargs)
        return fake_processes(world)

    calls = scenario(other_stop_world)

    code, _, _ = run_cli(queued_merge, [PR, str(worktree), BRANCH, "-"])

    ran = [c for c in calls if "update-index" in c or "rebase --continue" in c or " push " in c or "merge-lock.sh release" in c]
    assert (code, ran, events.exists()) == (1, [], False)


def test_3422_queued_merge_of_a_pr_whose_body_carries_closes_for_the_runs_issue_merges_it_on_the_pushed_head_and_exits_0(
        fake_processes, run_cli, tmp_path):
    worktree = tmp_path / "wt"
    (worktree / ".tdd").mkdir(parents=True)
    (worktree / ".tdd" / "issue-3255.md").write_text("# issue\n")
    body = json.dumps({"body": "Closes #3255 — the capability\n"})

    def with_body(answer):
        def wrapped(line, **kwargs):
            if "pr view" in line:
                return 0, body, ""
            if line.endswith("gh api repos/o/r/pulls/7"):
                return rest_body(answer, line, (0, body, ""), **kwargs)
            return answer(line, **kwargs)
        return fake_processes(wrapped)

    calls = scenario(with_body)

    code, _, _ = run_cli(queued_merge, [PR, str(worktree), "feature", "the capability"], env={"VERI_GH_DRIVER": "graphql"})

    merges = [c for c in calls if "pr merge" in c]
    assert (code, merges) == (0, ["merge-lock.sh gate --keep --pid %s -- gh pr merge %s --rebase --match-head-commit %s" % (PID, PR, PUSHED_HEAD)])


def test_3980_queued_merge_whose_pr_body_read_answers_text_that_is_not_json_releases_the_lock_once_and_exits_2_with_one_refusal_line(
        fake_processes, run_cli, tmp_path):
    worktree = tmp_path / "wt"
    worktree.mkdir()

    def garbled(answer):
        def wrapped(line, **kwargs):
            if "diff --name-only origin/main...HEAD" in line:
                return 0, ".tdd/issue-3255.md\n", ""
            if "pr view" in line:
                return 0, "<html>502 Bad Gateway</html>", ""
            if line.endswith("gh api repos/o/r/pulls/7"):
                return rest_body(answer, line, (0, "<html>502 Bad Gateway</html>", ""), **kwargs)
            return answer(line, **kwargs)
        return fake_processes(wrapped)

    calls = scenario(garbled)

    code, _, err = run_cli(queued_merge, [PR, str(worktree), "feature", "the capability"])

    released = [c for c in calls if c.startswith("merge-lock.sh release")]
    merges = [c for c in calls if "pr merge" in c or "pulls/7/merge" in c]
    assert (code, len(released), merges, err.splitlines()[-1:] == err.splitlines(),
            err.startswith("queued-merge.sh: JSONDecodeError: "), "(at " in err) == (2, 1, [], True, True, True)


def test_3422_queued_merge_of_a_pr_whose_body_lacks_closes_for_the_runs_issue_exits_2_naming_the_line_makes_no_merge_call_and_frees_the_lock(
        fake_processes, run_cli, tmp_path):
    worktree = tmp_path / "wt"
    worktree.mkdir()
    body = json.dumps({"body": "## Review fixes\n- tidy\n"})

    def with_body(answer):
        def wrapped(line, **kwargs):
            if "diff --name-only origin/main...HEAD" in line:
                return 0, ".tdd/issue-3255.md\n", ""
            if "pr view" in line:
                return 0, body, ""
            if line.endswith("gh api repos/o/r/pulls/7"):
                return rest_body(answer, line, (0, body, ""), **kwargs)
            return answer(line, **kwargs)
        return fake_processes(wrapped)

    calls = scenario(with_body)

    code, _, err = run_cli(queued_merge, [PR, str(worktree), "feature", "the capability"], env={"VERI_GH_DRIVER": "auto"})

    merges = [c for c in calls if "pr merge" in c or "pulls/7/merge" in c]
    released = [c for c in calls if c.startswith("merge-lock.sh release")]
    assert (code, "Closes #3255" in err, merges, len(released)) == (2, True, [], 1)


def test_4664_queued_merge_with_graphql_refused_reads_the_pr_body_over_rest_and_refuses_one_lacking_closes_for_the_runs_issue_exit_2_no_merge_lock_released(
        fake_processes, run_cli, tmp_path):
    worktree = tmp_path / "wt"
    worktree.mkdir()
    body = json.dumps({"body": "## Review fixes\n- tidy\n"})

    def rest_only(answer):
        def wrapped(line, **kwargs):
            if "diff --name-only origin/main...HEAD" in line:
                return 0, ".tdd/issue-3255.md\n", ""
            if "pr view" in line:
                return 1, "", "HTTP 403: Resource not accessible (graphql)"
            if line.endswith("gh api repos/o/r/pulls/7"):
                return rest_body(answer, line, (0, body, ""), **kwargs)
            return answer(line, **kwargs)
        return fake_processes(wrapped)

    calls = scenario(rest_only)

    code, _, err = run_cli(queued_merge, [PR, str(worktree), "feature", "the capability"], env={"VERI_GH_DRIVER": "rest"})

    merges = [c for c in calls if "pr merge" in c or "pulls/7/merge" in c]
    released = [c for c in calls if c.startswith("merge-lock.sh release")]
    assert (code, "Closes #3255" in err, merges, len(released)) == (2, True, [], 1)


def test_4664_queued_merge_with_graphql_refused_whose_rest_pr_read_exits_non_zero_exits_2_naming_the_pr_makes_no_merge_call_and_frees_the_lock(
        fake_processes, run_cli, tmp_path):
    worktree = tmp_path / "wt"
    worktree.mkdir()

    def rest_fails(answer):
        def wrapped(line, **kwargs):
            if "diff --name-only origin/main...HEAD" in line:
                return 0, ".tdd/issue-3255.md\n", ""
            if "pr view" in line:
                return 1, "", "HTTP 403: Resource not accessible (graphql)"
            if line.endswith("gh api repos/o/r/pulls/7"):
                return rest_body(answer, line, (1, "", "HTTP 502"), **kwargs)
            return answer(line, **kwargs)
        return fake_processes(wrapped)

    calls = scenario(rest_fails)

    code, _, err = run_cli(queued_merge, [PR, str(worktree), "feature", "the capability"], env={"VERI_GH_DRIVER": "rest"})

    merges = [c for c in calls if "pr merge" in c or "pulls/7/merge" in c]
    released = [c for c in calls if c.startswith("merge-lock.sh release")]
    assert (code, "could not read the PR body of %s; not merged" % PR in err, merges, len(released)) == (2, True, [], 1)


def test_4664_queued_merge_with_graphql_refused_whose_rest_pr_read_carries_no_body_key_exits_2_naming_the_pr_makes_no_merge_call_and_frees_the_lock(
        fake_processes, run_cli, tmp_path):
    worktree = tmp_path / "wt"
    worktree.mkdir()

    def rest_no_body(answer):
        def wrapped(line, **kwargs):
            if "diff --name-only origin/main...HEAD" in line:
                return 0, ".tdd/issue-3255.md\n", ""
            if "pr view" in line:
                return 1, "", "HTTP 403: Resource not accessible (graphql)"
            if line.endswith("gh api repos/o/r/pulls/7"):
                return rest_body(answer, line, (0, json.dumps({"number": 7}), ""), **kwargs)
            return answer(line, **kwargs)
        return fake_processes(wrapped)

    calls = scenario(rest_no_body)

    code, _, err = run_cli(queued_merge, [PR, str(worktree), "feature", "the capability"], env={"VERI_GH_DRIVER": "rest"})

    merges = [c for c in calls if "pr merge" in c or "pulls/7/merge" in c]
    released = [c for c in calls if c.startswith("merge-lock.sh release")]
    assert (code, "could not read the PR body of %s; not merged" % PR in err, merges, len(released)) == (2, True, [], 1)


def test_3422_queued_merge_of_a_pr_whose_only_closing_line_is_for_a_longer_issue_number_sharing_the_runs_number_as_a_prefix_exits_2_and_makes_no_merge_call(
        fake_processes, run_cli, tmp_path):
    worktree = tmp_path / "wt"
    worktree.mkdir()
    body = json.dumps({"body": "Closes #32550 — another capability\n"})

    def with_body(answer):
        def wrapped(line, **kwargs):
            if "diff --name-only origin/main...HEAD" in line:
                return 0, ".tdd/issue-3255.md\n", ""
            if "pr view" in line:
                return 0, body, ""
            if line.endswith("gh api repos/o/r/pulls/7"):
                return rest_body(answer, line, (0, body, ""), **kwargs)
            return answer(line, **kwargs)
        return fake_processes(wrapped)

    calls = scenario(with_body)

    code, _, err = run_cli(queued_merge, [PR, str(worktree), "feature", "the capability"], env={"VERI_GH_DRIVER": "auto"})

    merges = [c for c in calls if "pr merge" in c or "pulls/7/merge" in c]
    assert (code, merges) == (2, [])


def test_3422_queued_merge_on_a_worktree_holding_other_issues_ledgers_and_their_metrics_and_refactor_owed_files_checks_only_the_runs_own_issue_and_merges_a_pr_carrying_its_closes_line(
        fake_processes, run_cli, tmp_path):
    BRANCH = "tdd/3255-the-done-comment"
    worktree = tmp_path / "wt"
    (worktree / ".tdd").mkdir(parents=True)
    for name in ("issue-3255.md", "issue-3100.md", "issue-3100-metrics.md", "issue-3100-refactor-owed.md"):
        (worktree / ".tdd" / name).write_text("# issue\n")
    body = json.dumps({"body": "Closes #3255 — the capability\n"})

    def with_body(answer):
        def wrapped(line, **kwargs):
            if "pr view" in line:
                return 0, body, ""
            if line.endswith("gh api repos/o/r/pulls/7"):
                return rest_body(answer, line, (0, body, ""), **kwargs)
            return answer(line.replace(BRANCH, "feature"), **kwargs)
        return fake_processes(wrapped)

    calls = scenario(with_body)

    code, _, _ = run_cli(queued_merge, [PR, str(worktree), BRANCH, "the capability"], env={"VERI_GH_DRIVER": "graphql"})

    merges = [c for c in calls if "pr merge" in c]
    assert (code, len(merges)) == (0, 1)


def test_3452_queued_merge_whose_pr_body_read_fails_exits_2_naming_the_pr_frees_the_lock_and_makes_no_merge_call_while_a_successful_read_of_a_closes_body_merges(
        fake_processes, run_cli, tmp_path):
    worktree = tmp_path / "wt"
    worktree.mkdir()

    def run(read):
        def with_body(answer):
            def wrapped(line, **kwargs):
                if "diff --name-only origin/main...HEAD" in line:
                    return 0, ".tdd/issue-3255.md\n", ""
                if "pr view" in line:
                    return read
                if line.endswith("gh api repos/o/r/pulls/7"):
                    return rest_body(answer, line, read, **kwargs)
                return answer(line, **kwargs)
            return fake_processes(wrapped)

        calls = scenario(with_body)
        code, _, err = run_cli(queued_merge, [PR, str(worktree), "feature", "the capability"], env={"VERI_GH_DRIVER": "graphql"})
        merges = [c for c in calls if "pr merge" in c]
        released = [c for c in calls if c.startswith("merge-lock.sh release")]
        return code, PR in err, len(merges), len(released)

    failed = run((1, "", "HTTP 502"))
    read = run((0, json.dumps({"body": "Closes #3255 — the capability\n"}), ""))

    assert (failed, read[:3]) == ((2, True, 0, 1), (0, False, 1))


def test_3452_queued_merge_on_a_branch_not_named_tdd_n_whose_worktree_holds_a_metrics_file_beside_the_ledger_checks_the_ledgers_issue_and_merges_as_with_the_ledger_alone(
        fake_processes, run_cli, tmp_path):
    def run(name, extra):
        worktree = tmp_path / name
        (worktree / ".tdd").mkdir(parents=True)
        for file in ("issue-3255.md",) + extra:
            (worktree / ".tdd" / file).write_text("# issue\n")

        changed = "".join(".tdd/%s\n" % file for file in ("issue-3255.md",) + extra)

        def with_body(answer):
            def wrapped(line, **kwargs):
                if "diff --name-only origin/main...HEAD" in line:
                    return 0, changed, ""
                if "pr view" in line:
                    return 0, json.dumps({"body": "Closes #3255 — the capability\n"}), ""
                if line.endswith("gh api repos/o/r/pulls/7"):
                    return rest_body(answer, line, (0, json.dumps({"body": "Closes #3255 — the capability\n"}), ""), **kwargs)
                return answer(line, **kwargs)
            return fake_processes(wrapped)

        calls = scenario(with_body)
        code, _, _ = run_cli(queued_merge, [PR, str(worktree), "feature", "the capability"], env={"VERI_GH_DRIVER": "graphql"})
        return code, len([c for c in calls if "pr merge" in c])

    alone = run("alone", ())
    beside = run("beside", ("issue-3255-metrics.md",))

    assert (beside, alone) == ((0, 1), (0, 1))


def test_3490_queued_merge_on_a_branch_not_named_tdd_n_whose_diff_holds_only_a_metrics_file_numbered_unlike_any_ledger_demands_no_closes_for_it_and_merges(
        fake_processes, run_cli, tmp_path):
    worktree = tmp_path / "wt"
    (worktree / ".tdd").mkdir(parents=True)
    (worktree / ".tdd" / "issue-400-metrics.md").write_text("# metrics\n")

    def with_body(answer):
        def wrapped(line, **kwargs):
            if "diff --name-only origin/main...HEAD" in line:
                return 0, ".tdd/issue-400-metrics.md\n", ""
            if "pr view" in line:
                return 0, json.dumps({"body": "the capability\n"}), ""
            return answer(line, **kwargs)
        return fake_processes(wrapped)

    calls = scenario(with_body)
    code, _, err = run_cli(queued_merge, [PR, str(worktree), "feature", "the capability"], env={"VERI_GH_DRIVER": "graphql"})

    merges = [c for c in calls if "pr merge" in c]
    assert (code, len(merges), "Closes #400" in err) == (0, 1, False)


def test_3500_queued_merge_of_a_pr_already_reading_merged_after_the_fetch_exits_2_naming_it_on_stderr_before_any_rebase_or_push(fake_processes, run_cli):
    def already_merged(answer):
        def wrapped(line, **kw):
            if line.endswith("gh api repos/o/r/pulls/7"):
                return 0, json.dumps({"merged": True, "merge_commit_sha": MERGE_SHA}), ""
            return answer(line, **kw)
        return fake_processes(wrapped)

    calls = scenario(already_merged)

    code, _, err = run_cli(queued_merge, ARGV)

    moved = [c for c in calls if "rebase" in c or " push " in c]
    assert (code, "merged" in err, moved) == (2, True, [])


def test_3500_queued_merge_of_a_pr_already_reading_merged_after_the_fetch_releases_the_merge_lock_once(fake_processes, run_cli):
    def already_merged(answer):
        def wrapped(line, **kw):
            if line.endswith("gh api repos/o/r/pulls/7"):
                return 0, json.dumps({"merged": True, "merge_commit_sha": MERGE_SHA}), ""
            return answer(line, **kw)
        return fake_processes(wrapped)

    calls = scenario(already_merged)

    code, _, _ = run_cli(queued_merge, ARGV)

    released = [c for c in calls if c.startswith("merge-lock.sh release")]
    assert (code, len(released)) == (2, 1)


def test_3500_queued_merge_of_a_pr_reading_closed_and_unmerged_after_the_fetch_exits_2_naming_it_on_stderr_before_any_rebase_or_push(fake_processes, run_cli):
    def closed_unmerged(answer):
        def wrapped(line, **kw):
            if line.endswith("gh api repos/o/r/pulls/7"):
                return 0, json.dumps({"state": "closed", "merged": False}), ""
            return answer(line, **kw)
        return fake_processes(wrapped)

    calls = scenario(closed_unmerged)

    code, _, err = run_cli(queued_merge, ARGV)

    moved = [c for c in calls if "rebase" in c or " push " in c]
    assert (code, "closed" in err, moved) == (2, True, [])


def test_3500_queued_merge_of_a_pr_reading_closed_and_unmerged_after_the_fetch_releases_the_merge_lock_once(fake_processes, run_cli):
    def closed_unmerged(answer):
        def wrapped(line, **kw):
            if line.endswith("gh api repos/o/r/pulls/7"):
                return 0, json.dumps({"state": "closed", "merged": False}), ""
            return answer(line, **kw)
        return fake_processes(wrapped)

    calls = scenario(closed_unmerged)

    code, _, _ = run_cli(queued_merge, ARGV)

    released = [c for c in calls if c.startswith("merge-lock.sh release")]
    assert (code, len(released)) == (2, 1)


def test_3500_queued_merge_of_an_open_pr_whose_head_is_already_an_ancestor_of_origin_main_releases_the_merge_lock_once(fake_processes, run_cli):
    def head_on_main(answer):
        def wrapped(line, **kw):
            if line.endswith("merge-base --is-ancestor 9999999 origin/main"):
                return 0, "", ""
            return answer(line, **kw)
        return fake_processes(wrapped)

    calls = scenario(head_on_main)

    code, _, _ = run_cli(queued_merge, ARGV)

    released = [c for c in calls if c.startswith("merge-lock.sh release")]
    assert (code, len(released)) == (2, 1)


def test_3500_queued_merge_whose_pr_read_fails_after_the_fetch_exits_2_naming_it_on_stderr_before_any_rebase_or_push_and_frees_the_lock(fake_processes, run_cli, monkeypatch):
    monkeypatch.setattr(queued_merge, "_pull", lambda repo, pr: None)

    calls = scenario(fake_processes)

    code, _, err = run_cli(queued_merge, ARGV)

    moved = [c for c in calls if "rebase" in c or " push " in c]
    released = [c for c in calls if c.startswith("merge-lock.sh release")]
    assert (code, "could not read" in err, moved, len(released)) == (2, True, [], 1)


def test_3500_scenario_fixture_answers_not_an_ancestor_for_a_strictly_behind_pr_head_against_origin_main(fake_processes):
    scenario(fake_processes, behind=True)

    ran = queued_merge._git("/wt", "merge-base", "--is-ancestor", "9999999", "origin/main")

    assert ran.returncode == 1


def test_3500_queued_merge_of_an_open_pr_whose_head_is_already_an_ancestor_of_origin_main_exits_2_naming_it_on_stderr_before_any_rebase_or_push(fake_processes, run_cli):
    def head_on_main(answer):
        def wrapped(line, **kw):
            if line.endswith("merge-base --is-ancestor 9999999 origin/main"):
                return 0, "", ""
            return answer(line, **kw)
        return fake_processes(wrapped)

    calls = scenario(head_on_main)

    code, _, err = run_cli(queued_merge, ARGV)

    moved = [c for c in calls if "rebase" in c or " push " in c]
    assert (code, "9999999" in err, moved) == (2, True, [])


def test_3500_queued_merge_of_an_open_pr_whose_pull_record_carries_no_head_sha_exits_2_before_any_rebase_or_push(fake_processes, run_cli):
    def no_head(answer):
        def wrapped(line, **kw):
            if line.startswith("gh api") and "pulls/7" in line and "/merge" not in line:
                return 0, json.dumps({"state": "open", "merged": False}), ""
            return answer(line, **kw)
        return fake_processes(wrapped)

    calls = scenario(no_head)

    code, _, err = run_cli(queued_merge, ARGV)

    moved = [c for c in calls if "rebase" in c or " push " in c]
    assert (code, bool(err), moved) == (2, True, [])


def test_queued_merge_with_empty_settle_tunables_rereads_an_open_pr_ten_times_each_after_a_three_second_wait(fake_processes, run_cli, monkeypatch):
    calls = scenario(fake_processes, fail=("pulls/7/merge",))
    waits = []
    monkeypatch.setattr(queued_merge.time, "sleep", waits.append)

    code, _, _ = run_cli(queued_merge, ARGV, env={"VERI_MERGE_SETTLE_READS": "", "VERI_MERGE_SETTLE_SLEEP": ""})

    put = first(calls, "pulls/7/merge")
    rereads = [c for c in calls[put + 1:] if c.endswith("gh api repos/o/r/pulls/7")]
    assert (code, len(rereads), waits, cleaned(calls)) == (1, 10, [3.0] * 10, [])


def test_queued_merge_with_an_empty_fetch_retry_sleep_waits_one_second_between_fetches(fake_processes, run_cli, monkeypatch):
    seen = {"cat-file": 0}
    waits = []

    def lag(answer):
        def lagging(line, **kwargs):
            if "cat-file -e" in line:
                seen["cat-file"] += 1
                return (1, "", "") if seen["cat-file"] == 1 else (0, "", "")
            return answer(line, **kwargs)
        return fake_processes(lagging)

    scenario(lag)
    monkeypatch.setattr(queued_merge.time, "sleep", waits.append)

    code, _, _ = run_cli(queued_merge, ARGV, env={"VERI_FETCH_RETRY_SLEEP": ""})

    assert (code, waits) == (0, [1.0])


def test_queued_merge_refuses_an_empty_veri_gh_driver_with_2_naming_it_before_taking_the_lock(fake_processes, run_cli):
    calls = scenario(fake_processes)

    code, out, err = run_cli(queued_merge, ARGV, env={"VERI_GH_DRIVER": ""})

    assert (code, out, err, calls) == (2, "", "VERI_GH_DRIVER is '': expected auto, rest or graphql\n", [])


def test_3980_queued_merge_whose_exception_escapes_while_a_rebase_is_stopped_keeps_the_lock_and_exits_2_with_one_refusal_line(
        fake_processes, run_cli, monkeypatch, tmp_path):
    stopped_rebase = tmp_path / "rebase-merge"
    stopped_rebase.mkdir()

    def phantom_world(answer):
        def world(line, **kwargs):
            if "status --porcelain" in line:
                return 0, "", ""
            if "rebase origin/main" in line:
                answer(line, **kwargs)
                return 1, "", PHANTOM
            if "rev-parse --git-path rebase-merge" in line:
                return 0, "%s\n" % stopped_rebase, ""
            return answer(line, **kwargs)
        return fake_processes(world)

    def broken_mark(*_args, **_kwargs):
        raise OSError("events.jsonl is not writable")

    calls = scenario(phantom_world)
    monkeypatch.setattr(queued_merge.event, "mark", broken_mark)

    code, _, err = run_cli(queued_merge, ARGV)

    released = [c for c in calls if c.startswith("merge-lock.sh release")]
    refusals = [line for line in err.splitlines() if line.startswith("queued-merge.sh: ")]
    assert (code, released, len(refusals), refusals[0].startswith("queued-merge.sh: OSError: "),
            "lock kept, clear it with merge-lock.sh release --force" in err) == (2, [], 1, True, True)


@pytest.mark.parametrize("env, named", [
    ({"VERI_MERGE_SETTLE_READS": "many"}, "VERI_MERGE_SETTLE_READS"),
    ({"VERI_MERGE_SETTLE_SLEEP": "soon"}, "VERI_MERGE_SETTLE_SLEEP"),
    ({"VERI_MERGE_SETTLE_READS": "0"}, "VERI_MERGE_SETTLE_READS"),
    ({"VERI_MERGE_SETTLE_SLEEP": "-1"}, "VERI_MERGE_SETTLE_SLEEP"),
    ({"VERI_MERGE_SETTLE_SLEEP": "inf"}, "VERI_MERGE_SETTLE_SLEEP"),
    ({"VERI_MERGE_SETTLE_SLEEP": "nan"}, "VERI_MERGE_SETTLE_SLEEP"),
])
def test_3979_queued_merge_refuses_a_settle_tunable_it_cannot_use_with_2_naming_it_before_any_lock_or_gh_call(fake_processes, run_cli, env, named):
    calls = scenario(fake_processes)

    code, _, err = run_cli(queued_merge, ARGV, env=env)

    assert (code, named in err, calls) == (2, True, [])


def test_3981_queued_merge_in_a_clone_holding_v1_2_3_release_1_and_v0_10_bumps_only_from_vN_M_tags_and_cuts_v0_11(fake_processes, run_cli):
    calls = scenario(fake_processes, tags="v1.2.3\nv0.10\nrelease-1\n")

    code, _, _ = run_cli(queued_merge, ARGV)

    tags = [c for c in calls if " tag -a " in c or "push origin v" in c]
    assert (code, tags) == (0, ["git -C /wt tag -a v0.11 -m the capability %s" % MERGE_SHA, "git -C /wt push origin v0.11"])


def test_3981_queued_merge_in_a_clone_holding_only_release_1_cuts_no_tag_names_why_runs_the_cleanup_and_exits_2_naming_tag(fake_processes, run_cli):
    calls = scenario(fake_processes, tags="release-1\n")

    code, _, err = run_cli(queued_merge, ARGV)

    tagged = [c for c in calls if " tag -a " in c or "push origin v" in c]
    ran = [first(calls, needle) is not None for needle in (
        "push origin --delete feature", "worktree remove", "branch -D feature", "merge-lock.sh release", "pull --ff-only")]
    assert (code, tagged, "no vN.M tag to bump from; no tag cut" in err, "merged, but cleanup failed: tag" in err, ran) == (
        2, [], True, True, [True] * 5)


def test_3981_queued_merge_whose_tag_step_raises_runs_every_later_cleanup_step_and_exits_2_with_tag_named_as_failed(fake_processes, run_cli):
    def raising(answer):
        def wrapped(line, **kwargs):
            if "tag --sort=-v:refname" in line:
                raise OSError("git vanished mid-tag")
            return answer(line, **kwargs)
        return fake_processes(wrapped)

    calls = scenario(raising)

    code, _, err = run_cli(queued_merge, ARGV)

    ran = [first(calls, needle) is not None for needle in (
        "push origin --delete feature", "worktree remove", "branch -D feature", "merge-lock.sh release", "pull --ff-only")]
    assert (code, "merged, but cleanup failed: tag" in err, ran) == (2, True, [True] * 5)


def test_3982_queued_merge_whose_tag_push_fails_deletes_the_local_tag_says_it_was_cut_not_published_and_removed_and_exits_2_naming_tag(fake_processes, run_cli):
    calls = scenario(fake_processes, fail=("push origin v0.11",))

    code, _, err = run_cli(queued_merge, ARGV)

    deleted = [c for c in calls if "update-ref -d" in c]
    assert (code, deleted, "v0.11 cut, not published, and removed" in err, "merged, but cleanup failed: tag" in err) == (
        2, [GUARDED_DELETE], True, True)


def test_3982_queued_merge_whose_tag_push_and_tag_delete_both_fail_names_the_failed_delete_and_exits_2_naming_tag(fake_processes, run_cli):
    scenario(fake_processes, fail=("push origin v0.11", "update-ref -d refs/tags/v0.11"))

    code, _, err = run_cli(queued_merge, ARGV)

    assert (code, "tag v0.11 left in the clone" in err, "and removed" in err, "merged, but cleanup failed: tag" in err) == (2, True, False, True)


@pytest.mark.parametrize("name", ["VERI_GIT_NETWORK_TIMEOUT", "VERI_GH_TIMEOUT"])
@pytest.mark.parametrize("value", ["soon", "0", "-5", "2.5", ""])
def test_3984_queued_merge_refuses_a_network_timeout_that_is_not_a_whole_number_of_at_least_1_empty_included_with_2_naming_it_before_any_lock(fake_processes, run_cli, name, value):
    calls = scenario(fake_processes)

    code, _, err = run_cli(queued_merge, ARGV, env={name: value})

    assert (code, name in err, calls) == (2, True, [])


def test_3984_queued_merge_whose_fetch_origin_never_returns_ends_it_after_the_git_network_timeout_exits_2_naming_it_and_the_limit_and_releases_the_lock(fake_processes, run_cli):
    calls = scenario(hanging(fake_processes, "merge-lock.sh gate --pid %s -- git -C /wt fetch origin" % PID))

    code, _, err = run_cli(queued_merge, ARGV, env={"VERI_GIT_NETWORK_TIMEOUT": "7"})

    released = [c for c in calls if c.startswith("merge-lock.sh release")]
    assert (code, "fetch origin: no answer after 7s (VERI_GIT_NETWORK_TIMEOUT)" in err, len(released), first(calls, "rebase")) == (
        2, True, 1, None)


def test_3984_queued_merge_whose_leased_push_never_returns_ends_it_after_the_git_network_timeout_exits_2_naming_it_and_the_limit_and_keeps_the_lock(fake_processes, run_cli):
    push = "merge-lock.sh gate --keep --pid %s -- git -C /wt push --force-with-lease=feature:%s origin HEAD:refs/heads/feature" % (PID, ORIGIN_SHA)
    calls = scenario(hanging(fake_processes, push))

    code, _, err = run_cli(queued_merge, ARGV, env={"VERI_GIT_NETWORK_TIMEOUT": "7"})

    released = [c for c in calls if c.startswith("merge-lock.sh release")]
    assert (code, "HEAD:refs/heads/feature: no answer after 7s (VERI_GIT_NETWORK_TIMEOUT)" in err, "lock kept" in err,
            released, first(calls, "wait-ci.sh")) == (2, True, True, [], None)


def test_3984_queued_merge_whose_tag_push_never_returns_ends_it_after_the_git_network_timeout_as_a_failed_tag_push_and_exits_2_naming_tag(fake_processes, run_cli):
    calls = scenario(hanging(fake_processes, "git -C /wt push origin v0.11"))

    code, _, err = run_cli(queued_merge, ARGV, env={"VERI_GIT_NETWORK_TIMEOUT": "7"})

    released = [c for c in calls if c.startswith("merge-lock.sh release")]
    assert (code, "push origin v0.11: no answer after 7s (VERI_GIT_NETWORK_TIMEOUT)" in err, first(calls, GUARDED_DELETE) is not None,
            "merged, but cleanup failed: tag" in err, len(released)) == (2, True, True, True, 1)


def test_3984_queued_merge_whose_tag_push_times_out_says_the_tag_may_have_been_published_never_that_it_was_not(fake_processes, run_cli):
    scenario(hanging(fake_processes, "git -C /wt push origin v0.11"))

    code, _, err = run_cli(queued_merge, ARGV, env={"VERI_GIT_NETWORK_TIMEOUT": "7"})

    assert (code, "tag v0.11 cut, may have been published" in err, "not published" in err) == (2, True, False)


def test_3984_queued_merge_whose_branch_delete_never_returns_ends_it_after_the_git_network_timeout_as_a_failed_branch_delete_and_runs_the_rest(fake_processes, run_cli):
    calls = scenario(hanging(fake_processes, "git -C /wt push origin --delete feature --force-with-lease=feature:%s" % PUSHED_HEAD))

    code, _, err = run_cli(queued_merge, ARGV, env={"VERI_GIT_NETWORK_TIMEOUT": "7"})

    ran = [first(calls, needle) is not None for needle in ("worktree remove", "branch -D feature", "merge-lock.sh release", "pull --ff-only")]
    assert (code, "push origin --delete feature --force-with-lease=feature:%s: no answer after 7s (VERI_GIT_NETWORK_TIMEOUT)" % PUSHED_HEAD in err,
            "merged, but cleanup failed: branch delete" in err, ran) == (2, True, True, [True] * 4)


def test_3984_queued_merge_whose_merge_call_lands_and_never_returns_ends_it_after_the_gh_timeout_and_the_settle_window_holding_the_lock_reads_it_merged(fake_processes, run_cli):
    def landed_then_hangs(answer):
        def world(line, **kwargs):
            got = answer(line, **kwargs)
            return HANGS if "-X PUT repos/o/r/pulls/7/merge" in line else got
        return fake_processes(world)

    calls = scenario(landed_then_hangs)

    code, _, err = run_cli(queued_merge, ARGV, env={"VERI_GH_TIMEOUT": "5", "VERI_MERGE_SETTLE_SLEEP": "0"})

    released = [i for i, c in enumerate(calls) if c.startswith("merge-lock.sh release")]
    tagged = first(calls, " tag -a v0.11 ")
    assert (code, "pulls/7/merge -f merge_method=rebase -f sha=%s: no answer after 5s (VERI_GH_TIMEOUT)" % PUSHED_HEAD in err,
            tagged is not None, len(released), bool(released) and tagged is not None and released[0] > tagged) == (0, True, True, 1, True)


def test_3984_queued_merge_whose_fetch_after_the_merge_never_returns_ends_it_after_the_git_network_timeout_as_a_failed_fetch_and_cuts_no_tag(fake_processes, run_cli):
    calls = scenario(hanging(fake_processes, "git -C /wt fetch origin"))

    code, _, err = run_cli(queued_merge, ARGV, env={"VERI_GIT_NETWORK_TIMEOUT": "7", "VERI_FETCH_RETRY_SLEEP": "0"})

    assert (code, "fetch origin: no answer after 7s (VERI_GIT_NETWORK_TIMEOUT)" in err, "merged, but cleanup failed: tag" in err,
            first(calls, " tag -a ")) == (2, True, True, None)


def test_3984_queued_merge_whose_fetch_after_the_merge_times_out_does_not_fetch_again_and_exits_2_naming_tag_the_lock_released(fake_processes, run_cli):
    calls = scenario(hanging(fake_processes, "git -C /wt fetch origin"))

    code, _, err = run_cli(queued_merge, ARGV, env={"VERI_GIT_NETWORK_TIMEOUT": "7", "VERI_FETCH_RETRY_SLEEP": "0"})

    fetches = [c for c in calls if c == "git -C /wt fetch origin"]
    released = [c for c in calls if c.startswith("merge-lock.sh release")]
    assert (code, fetches, "merged, but cleanup failed: tag" in err, len(released)) == (2, ["git -C /wt fetch origin"], True, 1)


def test_3984_queued_merge_deletes_an_unpublished_tag_only_while_its_ref_still_points_at_the_object_this_run_cut_and_names_a_moved_one(fake_processes, run_cli):
    def moved(answer):
        def world(line, **kwargs):
            if line == GUARDED_DELETE:
                return 1, "", "error: cannot lock ref 'refs/tags/v0.11': is at 5555555 but expected %s" % TAG_OID
            return answer(line, **kwargs)
        return fake_processes(world)

    calls = scenario(moved, fail=("push origin v0.11",))

    code, _, err = run_cli(queued_merge, ARGV)

    deletes = [c for c in calls if "update-ref -d" in c or " tag -d " in c]
    assert (code, deletes, "tag v0.11 left in the clone" in err, "and removed" in err) == (2, [GUARDED_DELETE], True, False)


def raising_on(fake_processes, needle):
    """A fake_processes for scenario whose call containing <needle> raises instead of answering."""
    def install(answer):
        def world(line, **kwargs):
            if needle in line:
                raise RuntimeError("%s blew up" % needle)
            return answer(line, **kwargs)
        return fake_processes(world)
    return install


def test_3984_queued_merge_whose_tag_push_raises_after_the_cut_deletes_the_tag_it_cut_and_says_so_exiting_2_naming_tag(fake_processes, run_cli):
    calls = scenario(raising_on(fake_processes, "push origin v0.11"))

    code, _, err = run_cli(queued_merge, ARGV)

    assert (code, first(calls, GUARDED_DELETE) is not None, "tag v0.11" in err and "removed" in err,
            "merged, but cleanup failed: tag" in err) == (2, True, True, True)


def test_3984_queued_merge_whose_guarded_tag_delete_raises_names_the_tag_left_in_the_clone_and_exits_2_naming_tag(fake_processes, run_cli):
    scenario(raising_on(fake_processes, "update-ref -d refs/tags/v0.11"), fail=("push origin v0.11",))

    code, _, err = run_cli(queued_merge, ARGV)

    assert (code, "tag v0.11 left in the clone" in err, "merged, but cleanup failed: tag" in err) == (2, True, True)


def test_3984_queued_merge_whose_cut_tag_object_cannot_be_read_still_publishes_the_tag_and_exits_0(fake_processes, run_cli):
    calls = scenario(fake_processes, fail=("rev-parse --verify refs/tags/v0.11",))

    code, _, _ = run_cli(queued_merge, ARGV)

    assert (code, first(calls, "git -C /wt push origin v0.11") is not None) == (0, True)


def test_3984_queued_merge_whose_cut_tag_object_cannot_be_read_and_whose_push_fails_leaves_the_tag_named_runs_the_cleanup_and_exits_2_naming_tag(fake_processes, run_cli):
    calls = scenario(fake_processes, fail=("rev-parse --verify refs/tags/v0.11", "push origin v0.11"))

    code, _, err = run_cli(queued_merge, ARGV)

    deletes = [c for c in calls if "update-ref -d" in c or " tag -d " in c]
    ran = [first(calls, needle) is not None for needle in (
        "push origin --delete feature", "worktree remove", "branch -D feature", "merge-lock.sh release", "pull --ff-only")]
    released = [c for c in calls if c.startswith("merge-lock.sh release")]
    assert (code, deletes, "tag v0.11 left in the clone: its object could not be read" in err, "merged, but cleanup failed: tag" in err,
            ran, len(released)) == (2, [], True, True, [True] * 5, 1)


def test_the_merge_paths_branch_delete_is_leased_to_the_head_it_pushed_so_a_later_commit_is_never_dropped(fake_processes, run_cli):
    calls = scenario(fake_processes)

    code, _, _ = run_cli(queued_merge, ARGV)

    deletes = [c for c in calls if c.startswith("git -C /wt push origin --delete feature")]
    assert (code, deletes) == (0, ["git -C /wt push origin --delete feature --force-with-lease=feature:%s" % PUSHED_HEAD])


@pytest.mark.parametrize("listed, expected", [((0, "", ""), 0), ((0, "9999999\trefs/heads/feature\n", ""), 2)])
def test_the_merge_paths_branch_origin_already_deleted_counts_as_deleted_and_one_still_there_is_exit_2(
        fake_processes, run_cli, listed, expected):
    gone = (1, "", "error: unable to delete 'feature': remote ref does not exist\n")

    def world(answer):
        def answering(line, **kwargs):
            if "push origin --delete feature" in line:
                return gone
            if "ls-remote --heads origin refs/heads/feature" in line:
                return listed
            return answer(line, **kwargs)
        return fake_processes(answering)

    scenario(world)
    code, _, err = run_cli(queued_merge, ARGV)

    assert (code, ("branch delete" in err) == (expected == 2)) == (expected, True), err


def linked_worktree(tmp_path, n):
    """A main clone holding `.tdd/` and its linked worktree `<main>/.tdd/wt/<n>`, laid out as git lays them out."""
    main = tmp_path / "main"
    admin = main / ".git" / "worktrees" / n
    admin.mkdir(parents=True)
    (admin / "commondir").write_text("../..\n")
    worktree = main / ".tdd" / "wt" / n
    worktree.mkdir(parents=True)
    (worktree / ".git").write_text("gitdir: %s\n" % admin)
    return main, worktree


@pytest.mark.parametrize("take, code", [(0, 0), (2, 2)], ids=["merged", "lock refused"])
def test_4232_queued_merge_runs_as_stage_merge_carrying_the_branchs_issue_in_the_main_clone_ending_with_its_exit_code(
        fake_processes, run_cli, tmp_path, events, take, code):
    main, worktree = linked_worktree(tmp_path, "12")

    def world(answer):  # the scenario's world, its worktree /wt and branch feature here a run's
        return fake_processes(lambda line, **kwargs: answer(
            line.replace(str(worktree), "/wt").replace("tdd/12-a-run", "feature"), **kwargs))

    scenario(world, take=take)

    returned, _, err = run_cli(queued_merge, [PR, str(worktree), "tdd/12-a-run", "-"], cwd=tmp_path)

    stages = [(r["event"], r["stage"], r.get("status"), r["issue"]) for r in events.records(main) if "stage" in r]
    in_worktree = [r for r in events.records(worktree) if "stage" in r]  # the worktree a merge removes holds none
    assert (returned, stages, in_worktree) == (
        code, [("stage-start", "merge", None, "12"), ("stage-end", "merge", str(code), "12")], []), err


def test_4471_queued_merge_reads_the_ci_on_pr_line_from_the_merge_worktrees_claude_md_not_the_launch_directorys(
        fake_processes, run_cli, tmp_path):
    worktree = tmp_path / "wt"
    worktree.mkdir()
    (worktree / "CLAUDE.md").write_text("# notes\n\nveri: ci on pr: 0\n")
    launch = tmp_path / "launch"
    launch.mkdir()
    (launch / "CLAUDE.md").write_text("# notes\n\nveri: ci on pr: 1\n")

    def green_full_run(answer):  # the scenario's worktree is /wt; this one is on disk
        def wrapped(line, **kwargs):
            line = line.replace(str(worktree), "/wt")
            if "detect-test-command" in line:
                return 0, "make test\n", ""
            if "make test" in line:
                return 0, "", ""
            return answer(line, **kwargs)
        return fake_processes(wrapped)

    calls = scenario(green_full_run)

    code, _, err = run_cli(queued_merge, [PR, str(worktree), "feature", "the capability"], cwd=str(launch))

    full_runs = [c for c in calls if "make test" in c]
    assert (code, len(full_runs)) == (0, 1), err


def test_4471_queued_merge_runs_the_wait_ci_gate_in_the_merge_worktree_so_wait_ci_reads_its_claude_md_not_the_launch_directorys(
        fake_processes, run_cli, tmp_path):
    seen = []

    def recording(answer):
        def wrapped(line, **kwargs):
            if "wait-ci.sh" in line:
                seen.append(kwargs.get("cwd"))
            return answer(line, **kwargs)
        return fake_processes(wrapped)

    scenario(recording)

    code, _, err = run_cli(queued_merge, ARGV, cwd=str(tmp_path))

    assert (code, seen) == (0, ["/wt"]), err


def test_4471_queued_merge_runs_the_rebased_trees_full_suite_in_the_merge_worktree_so_it_tests_that_tree_not_the_launch_directorys(
        fake_processes, run_cli, tmp_path):
    worktree = tmp_path / "wt"
    worktree.mkdir()
    (worktree / "CLAUDE.md").write_text("# notes\n\nveri: ci on pr: 0\n")
    launch = tmp_path / "launch"
    launch.mkdir()
    seen = []

    def recording(answer):  # the scenario's worktree is /wt; this one is on disk
        def wrapped(line, **kwargs):
            line = line.replace(str(worktree), "/wt")
            if "detect-test-command" in line:
                return 0, "make test\n", ""
            if "make test" in line:
                seen.append(kwargs.get("cwd"))
                return 0, "", ""
            return answer(line, **kwargs)
        return fake_processes(wrapped)

    scenario(recording)

    code, _, err = run_cli(queued_merge, [PR, str(worktree), "feature", "the capability"], cwd=str(launch))

    assert (code, seen) == (0, [str(worktree)]), err


def test_4471_queued_merge_with_a_ci_on_pr_line_that_is_neither_0_nor_1_and_the_variable_unset_exits_2_with_one_stderr_line_naming_the_line(
        fake_processes, run_cli, tmp_path):
    worktree = tmp_path / "wt"
    worktree.mkdir()
    (worktree / "CLAUDE.md").write_text("# notes\n\nveri: ci on pr: maybe\n")
    scenario(lambda answer: fake_processes(lambda line, **kwargs: answer(line.replace(str(worktree), "/wt"), **kwargs)))

    code, _, err = run_cli(queued_merge, [PR, str(worktree), "feature", "the capability"], cwd=str(tmp_path))

    assert (code, "veri: ci on pr:" in err and "maybe" in err, len(err.strip().splitlines())) == (2, True, 1), err


def test_4741_queued_merge_of_a_run_whose_worktree_holds_a_mutation_record_entry_whose_old_text_is_gone_merges_and_queued_merge_imports_no_mutation_record(
        fake_processes, run_cli, tmp_path):
    BRANCH = "tdd/3255-the-done-comment"
    worktree = tmp_path / "wt"
    (worktree / ".tdd").mkdir(parents=True)
    (worktree / "lib").mkdir()
    (worktree / ".tdd" / "issue-3255.md").write_text("# issue\n")
    (worktree / "lib" / "calc.py").write_text("def add(a, b):\n    return a + b\n")
    old, new = (base64.b64encode(text.encode()).decode() for text in ("    return a - b\n", "    return 0\n"))
    (worktree / ".tdd" / "issue-3255-mutations.md").write_text(
        "file 11\nlib/calc.py\nold-b64 %d\n%s\nnew-b64 %d\n%s\n\n" % (len(old), old, len(new), new))
    body = json.dumps({"body": "Closes #3255 — the capability\n"})
    source = pathlib.Path(queued_merge.__file__).read_text(encoding="utf-8")
    imported = {alias.name for node in ast.walk(ast.parse(source)) if isinstance(node, (ast.Import, ast.ImportFrom))
                for alias in node.names} | {node.module for node in ast.walk(ast.parse(source))
                                            if isinstance(node, ast.ImportFrom)}

    def with_body(answer):
        def wrapped(line, **kwargs):
            if "pr view" in line:
                return 0, body, ""
            return answer(line.replace(BRANCH, "feature"), **kwargs)
        return fake_processes(wrapped)

    calls = scenario(with_body)

    code, _, err = run_cli(queued_merge, [PR, str(worktree), BRANCH, "the capability"], env={"VERI_GH_DRIVER": "graphql"})

    merges = [c for c in calls if "pr merge" in c or "pulls/7/merge" in c]
    assert (code, "mutation record" in err, len(merges), "mutation_record" in imported) == (0, False, 1, False), err
