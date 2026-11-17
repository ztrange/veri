"""In-process cases for veri/stack_revert.py, the module stack-revert.sh is a shim over (PRD 034.3d): the merge lock and
stack-red.sh (stack_fix's script calls), the stack's span, the worktree it adds and removes, the revert, the fast tier
and prose-owed.sh, the push and GitHub's reads and writes are injected in-process, so no case starts a process."""
import importlib
import re

import pytest

TOP = "/repo"
PATH = TOP + "/.tdd/stack-revert-"


@pytest.fixture
def revert():
    return importlib.import_module("veri.stack_revert")


def sha(n):
    return "%040x" % n


RED, REVERTED = sha(90), sha(99)
STACK = [(sha(1), "feat: a (#11)", []), (sha(2), "feat: b (#12)", []), (sha(3), "docs: names none", []),
         (sha(4), "feat: c (#13)", []), (sha(5), "fix: b's case (#12)", [RED])]


class World:
    """The stack (oldest first), what each script, git step and GitHub call answers, and every call made."""

    def __init__(self, monkeypatch, revert, stack=STACK, red_code=0, lock=0, add=True, reverted="ok", tier=None,
                 pushes=(None,), moved_stacks=None, span=None, pulls=None, edit_fails=(), tracking=1, removed=True):
        self.scripts, self.steps, self.pushed, self.posted, self.edited, self.reverts = [], [], [], [], [], []
        self.lock_held = False
        self.tip = sha(5) if stack == STACK else stack[-1][0]
        stacks = [list(stack)] + list(moved_stacks or [])
        self.fetches = 0
        pushes = list(pushes)

        def script(name, *args, limit=None):
            self.scripts.append((name,) + args)
            if name == "merge-lock.sh":
                self.lock_held = args[0] == "take" and lock == 0
                return (lock if args[0] == "take" else 0), ""
            if name == "stack-red.sh":
                return red_code, ("%s https://github.com/o/r/actions/runs/42 failure\n" % RED) if red_code == 0 else ""
            return 2, ""

        def current():
            return stacks[min(self.fetches - 1, len(stacks) - 1)]

        def ahead(root):
            self.fetches += 1
            if isinstance(span, BaseException):
                raise span
            if span is not None:
                return span
            return "stack", "trunk", [commit[:2] for commit in current()]

        def log(rev_range):
            return [(commit[0], commit[1], list(commit[2])) for commit in current()]

        def rev(ref):
            return current()[-1][0] if current() else ""

        def do_revert(path, commits):
            self.reverts.append(list(commits))
            if reverted != "ok":
                return reverted
            return "ok"

        def commit(path, subject, body):
            self.steps.append(("commit", subject, body))
            return REVERTED

        def tier_and_prose(top, say):
            self.steps.append(("tier", top))
            if tier:
                raise tier

        def pushed(head, stack_name, onto):
            self.pushed.append((head, stack_name, onto))
            outcome = pushes.pop(0) if pushes else None
            if outcome:
                raise outcome

        def merged_pulls(base, repo=None):
            if isinstance(pulls, BaseException):
                raise pulls
            return [revert.github.Pull(number=number, url=None, html_url=None, draft=None, head_ref="", head_sha="",
                                       body=body, state="MERGED", labels=(), cross_repository=fork)
                    for number, body, fork in (pulls if pulls is not None else [(41, "Run.\n\nCloses #12\n", False)])]

        def pr_body_edit(number, body):
            if number in edit_fails:
                raise revert.github.NoAnswer("", "HTTP 403")
            self.edited.append((number, body))

        def stack_pulls(head, base):
            return [type("P", (), {"number": 5, "html_url": "https://github.com/o/r/pull/5"})() for _ in range(tracking)]

        monkeypatch.setattr(revert.stack_fix, "script", script)
        monkeypatch.setattr(revert.stack_fix, "log", log)
        monkeypatch.setattr(revert.stack_fix, "tier_and_prose", tier_and_prose)
        monkeypatch.setattr(revert.stack_fix, "pushed", pushed)
        monkeypatch.setattr(revert.stack_branch, "ahead", ahead)
        monkeypatch.setattr(revert, "_top", lambda: TOP)
        monkeypatch.setattr(revert, "_rev", rev)
        monkeypatch.setattr(revert, "_add_worktree", lambda path, commit: self.steps.append(("add", path, commit)) or add)
        monkeypatch.setattr(revert, "_checkout", lambda path, commit: self.steps.append(("checkout", path, commit)) or True)
        monkeypatch.setattr(revert, "_remove_worktree", lambda path: self.steps.append(("remove", path)) or removed)
        monkeypatch.setattr(revert, "_revert", do_revert)
        monkeypatch.setattr(revert, "_commit", commit)
        monkeypatch.setattr(revert.github, "merged_pulls", merged_pulls)
        monkeypatch.setattr(revert.github, "pr_body_edit", pr_body_edit)
        monkeypatch.setattr(revert.github, "stack_pulls", stack_pulls)
        monkeypatch.setattr(revert.github, "gh_comment_post", lambda number, body: self.posted.append((number, body)))


def test_reverts_every_commit_of_n_by_kt5_newest_first_as_one_commit_on_the_tip_whose_subject_ends_n(
        monkeypatch, run_cli, revert):
    world = World(monkeypatch, revert)

    code, out, err = run_cli(revert, ["12"])

    commits = [step for step in world.steps if step[0] == "commit"]
    assert (code, out, world.reverts, len(commits), commits[0][1].endswith("(#12)")) == (
        0, REVERTED + "\n", [[sha(5), sha(3), sha(2)]], 1, True), err
    assert world.pushed == [(REVERTED, "stack", sha(5))]
    assert [step for step in world.steps if step[0] == "add"] == [("add", "%s%d" % (PATH, world_pid(world)), sha(5))]


def world_pid(world):
    added = [step for step in world.steps if step[0] == "add"][0][1]
    return int(added.rsplit("-", 1)[1])


@pytest.mark.parametrize("stack, reverted", [
    ([(sha(1), "feat: b (#12)", []), (sha(2), "fix: b more", []), (sha(3), "feat: c (#13)", [])], [sha(2), sha(1)]),
    ([(sha(1), "feat: b (#12)", []), (sha(2), "feat: c (#13)", []), (sha(3), "feat: d (#14)", []),
      (sha(4), "fix: b's case (#12)", [RED])], [sha(4), sha(1)]),
    ([(sha(1), "feat: a and b (#11, #12)", []), (sha(2), "feat: c (#13)", [])], [sha(1)]),
])
def test_a_commit_naming_no_issue_after_one_of_ns_and_a_hand_fix_above_other_issues_are_reverted_with_it(
        monkeypatch, run_cli, revert, stack, reverted):
    world = World(monkeypatch, revert, stack=stack)

    code, _, err = run_cli(revert, ["12"])

    assert (code, world.reverts) == (0, [reverted]), err


def test_the_fast_tier_and_prose_owed_run_on_the_reverted_tip_in_its_own_worktree_before_the_push(
        monkeypatch, run_cli, revert):
    world = World(monkeypatch, revert)

    run_cli(revert, ["12"])

    kinds = [step[0] for step in world.steps]
    assert (kinds.index("commit") < kinds.index("tier"), world.steps[kinds.index("tier")][1].startswith(PATH)) == (
        True, True)


def test_when_origin_moved_it_starts_again_from_the_fetch_reverting_onto_the_new_tip(monkeypatch, run_cli, revert):
    moved = STACK + [(sha(6), "feat: d (#14)", [])]
    world = World(monkeypatch, revert, pushes=(revert.stack_fix.Refused("moved"), None), moved_stacks=[moved])

    code, _, err = run_cli(revert, ["12"])

    assert (code, world.pushed, [step[2] for step in world.steps if step[0] in ("add", "checkout")]) == (
        0, [(REVERTED, "stack", sha(5)), (REVERTED, "stack", sha(6))], [sha(5), sha(6)]), err


def test_origin_moving_on_every_attempt_is_exit_2(monkeypatch, run_cli, revert):
    world = World(monkeypatch, revert, pushes=[revert.stack_fix.Refused("moved")] * 10)

    code, _, err = run_cli(revert, ["12"])

    assert (code, len(world.pushed), world.edited, world.posted, world.lock_held) == (2, 5, [], [], False), err


@pytest.mark.parametrize("given", [{"reverted": "conflict"}, {"tier": "red"}, {"tier": "owed"}])
def test_a_revert_conflict_a_red_fast_tier_or_a_unit_owing_a_grade_is_exit_1_nothing_pushed_the_lock_freed(
        monkeypatch, run_cli, revert, given):
    kwargs = dict(given)
    if "tier" in kwargs:
        kwargs["tier"] = revert.stack_fix.Refused("the fast tier is red" if given["tier"] == "red" else "owes a grade")
    world = World(monkeypatch, revert, **kwargs)

    code, _, err = run_cli(revert, ["12"])

    assert (code, world.pushed, world.lock_held, world.edited, world.posted) == (1, [], False, [], []), err
    assert world.scripts[-1][:2] == ("merge-lock.sh", "release")


def test_exits_3_when_stack_red_exits_3_or_no_commit_of_the_stack_belongs_to_n(monkeypatch, run_cli, revert):
    for kwargs, n in (({"red_code": 3}, "12"), ({}, "77")):
        world = World(monkeypatch, revert, **kwargs)

        code, _, err = run_cli(revert, [n])

        assert (code, world.pushed, world.reverts, world.lock_held) == (3, [], [], False), err


@pytest.mark.parametrize("given", ["red 2", "red 1", "lock", "span", "no stack", "add", "revert fails", "push",
                                   "tier no answer"])
def test_exits_2_on_no_answer_from_git_github_stack_red_or_the_lock_nothing_pushed(monkeypatch, run_cli, revert,
                                                                                    given):
    kwargs = {"red 2": {"red_code": 2}, "red 1": {"red_code": 1}, "lock": {"lock": 2},
              "span": {"span": revert.stack_branch.Refused("the fetch got no answer")}, "add": {"add": False},
              "revert fails": {"reverted": "failed"},
              "push": {"pushes": (revert.stack_fix.NoAnswer("no answer"),)},
              "tier no answer": {"tier": revert.stack_fix.NoAnswer("no fast tier")}}.get(given, {})
    world = World(monkeypatch, revert, **kwargs)
    if given == "no stack":
        monkeypatch.setattr(revert.stack_branch, "ahead", lambda root: None)

    code, _, err = run_cli(revert, ["12"])

    assert (code, [push for push in world.pushed if given != "push"], world.lock_held) == (2, [], False), err


@pytest.mark.parametrize("argv", [[], ["x"], ["12", "13"], ["0"]])
def test_bad_arguments_are_exit_2_before_the_lock(monkeypatch, run_cli, revert, argv):
    world = World(monkeypatch, revert)

    code, _, err = run_cli(revert, argv)

    assert (code, world.scripts) == (2, []), err


@pytest.mark.parametrize("given", [{}, {"reverted": "conflict"}, {"red_code": 2}])
def test_its_own_worktree_is_removed_on_every_exit_after_it_was_added_and_a_failed_removal_is_said(
        monkeypatch, run_cli, revert, given):
    world = World(monkeypatch, revert, **given)

    run_cli(revert, ["12"])

    added = [step[1] for step in world.steps if step[0] == "add"]
    assert [step[1] for step in world.steps if step[0] == "remove"] == added
    world = World(monkeypatch, revert, removed=False)
    code, _, err = run_cli(revert, ["12"])
    assert (code, "worktree remove" in err and PATH in err) == (0, True), err
