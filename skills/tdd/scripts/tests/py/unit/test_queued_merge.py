"""veri/queued_merge.py in-process, every process boundary (merge-lock.sh, wait-ci.sh, git, gh) faked."""
import json
import os

import pytest

from veri import queued_merge

PR = "https://github.com/o/r/pull/7"
ARGV = [PR, "/wt", "feature", "the capability"]
ORIGIN_SHA = "1111111"
PUSHED_HEAD = "abc1234"
MERGE_SHA = "fedcba9"
PID = str(os.getpid())
WAIT_CI = os.path.join(queued_merge.SCRIPTS, "wait-ci.sh")


def scenario(fake_processes, take=0, ci=(0,), merged=json.dumps({"merged": True, "merge_commit_sha": "fedcba9"}), gh_code=0, fail=(), behind=False, lease_readable=True):
    """A queued merge's world: the lock, CI's answers in order, GitHub's merged answer, and commands that fail."""
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
        if "merge-base --is-ancestor %s HEAD" % ORIGIN_SHA in line:
            return (1 if behind else 0), "", ""
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

    code, _, _ = run_cli(queued_merge, ARGV, env={"VERI_GH_DRIVER": "graphql"})

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

    code, _, _ = run_cli(queued_merge, ARGV, env={"VERI_GH_DRIVER": "graphql"})

    asked = len([c for c in calls if "wait-ci.sh" in c])
    merged_after = first(calls, "pr merge") is not None
    assert (code, asked, merged_after) == (expected, len(ci), expected == 0)


@pytest.mark.parametrize("take", [2, 1])
def test_2372_queued_merge_whose_take_fails_stops_with_takes_code_and_touches_nothing(fake_processes, run_cli, take):
    calls = scenario(fake_processes, take=take)

    code, _, _ = run_cli(queued_merge, ARGV)

    assert (code, [c.split()[1] for c in calls]) == (take, ["take"])


@pytest.mark.parametrize("merged, gh_code", [
    (json.dumps({"merged": None}), 0),
    (json.dumps({"state": "closed"}), 0),
    (json.dumps({"merged": "true"}), 0),
    ("not json", 0),
    ("", 1),
])
def test_2372_queued_merge_proceeds_to_tag_and_cleanup_only_on_an_observed_merged_true(fake_processes, run_cli, merged, gh_code):
    calls = scenario(fake_processes, merged=merged, gh_code=gh_code)

    code, _, err = run_cli(queued_merge, ARGV)

    released = [c for c in calls if c.startswith("merge-lock.sh release")]
    assert (code != 0, PR in err, cleaned(calls), len(released)) == (True, True, [], 1)


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
    calls = scenario(fake_processes, behind=True)

    code, _, err = run_cli(queued_merge, ARGV)

    pushes = [c for c in calls if " push " in c]
    released = [c for c in calls if c.startswith("merge-lock.sh release")]
    assert (code, "origin/feature" in err, pushes, first(calls, "rebase"), len(released)) == (2, True, [], None, 1)


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

    code, _, err = run_cli(queued_merge, ARGV)

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

    code, _, _ = run_cli(queued_merge, ARGV)

    puts = [c for c in calls if "pulls/7/merge" in c]
    assert (code, len(puts), ["--keep" in c for c in puts], cleaned(calls), first(calls, "pulls/7 ")) == (1, 1, [False], [], None)


def test_2585_queued_merge_under_the_graphql_driver_merges_with_gh_pr_merge_match_head_commit_and_makes_no_rest_put(fake_processes, run_cli):
    calls = scenario(fake_processes)

    code, _, _ = run_cli(queued_merge, ARGV, env={"VERI_GH_DRIVER": "graphql"})

    merges = [c for c in calls if "pr merge" in c]
    puts = [c for c in calls if "PUT" in c or "pulls/7/merge" in c]
    assert (code, merges, puts) == (
        0, ["merge-lock.sh gate --pid %s -- gh pr merge %s --rebase --match-head-commit %s" % (PID, PR, PUSHED_HEAD)], [])


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
