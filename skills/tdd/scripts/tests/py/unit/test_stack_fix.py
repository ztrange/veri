"""In-process cases for veri/stack_fix.py, the module stack-fix.sh is a shim over (PRD 034.3c): the merge lock and
stack-red.sh (its script calls), the stack's span, every git read and the push, the alone runs, the fast tier and
GitHub's reads and comments are injected in-process, so no case starts a process."""
import importlib

import pytest

TOP = "/repo/.tdd/fix"
CASE = "t/test_a.py::test_x"


@pytest.fixture
def fix():
    return importlib.import_module("veri.stack_fix")


def sha(n):
    return "%040x" % n


RED, ONTO, HEAD = sha(3), sha(3), sha(9)


def culprit_text(red=RED, issue="12", cases=(CASE,)):
    return "red: %s\nissue: %s\ncommit: %s\nbefore: %s\n%s" % (
        red, issue, sha(2), sha(1), "".join("case: %s\tFAILED %s - assert 0\n" % (c, c) for c in cases))


class World:
    """The stack (three commits on trunk, the red one its tip), the fix worktree's commits above it, what each script,
    git read, alone run and GitHub call answers, and every call made."""

    def __init__(self, monkeypatch, fix, tmp_path, red_now=RED, red_code=0, stack_subjects=None, fixes=None,
                 changed=(("M", "src/a.py"),), dirty="", has=True, alone=(0, "1 passed\n"), fast=(0, ""), owed=0,
                 push=0, moved=ONTO, ancestor=True, pulls=1, lock=0, culprit=None, span=None,
                 log_fails=False, one_file='make test TESTS="$1"', fast_command="make unit", head_after=None):
        self.scripts, self.pushed, self.posted, self.runs = [], [], [], []
        self.head = HEAD
        self.culprit = tmp_path / "culprit"
        self.culprit.write_text(culprit_text() if culprit is None else culprit)
        stack = [(sha(1), "feat: a (#11)"), (sha(2), "feat: b (#12)"), (sha(3), "feat: c (#13)")]
        if stack_subjects is not None:
            stack = stack_subjects
        fixes = [(HEAD, "fix: b's case (#12)", [RED])] if fixes is None else fixes
        self.lock_held = False

        def script(name, *args, limit=None):
            self.scripts.append((name,) + args)
            if name == "merge-lock.sh" and args[0] == "take":
                self.lock_held = lock == 0
                return lock, ""
            if name == "merge-lock.sh" and args[0] == "release":
                self.lock_held = False
                return 0, ""
            if name == "stack-red.sh":
                return red_code, ("%s https://github.com/o/r/actions/runs/42 failure\n" % red_now) if red_code == 0 else ""
            if name == "prose-owed.sh":
                return owed, ""
            return 2, ""

        def ahead(root):
            if isinstance(span, BaseException):
                raise span
            return ("stack", "trunk", [commit[:2] for commit in stack]) if span is None else span

        def rev(ref):
            if ref == "HEAD":
                return head_after if head_after and self.runs else self.head
            return ONTO if ref.endswith("/stack") else ""

        def log(rev_range):
            if log_fails:
                raise fix.NoAnswer("git log %s failed (exit 128)" % rev_range)
            if rev_range.startswith("refs/remotes/origin/trunk"):
                return [(commit[0], commit[1], list(commit[2:3] and commit[2])) for commit in stack]
            return list(fixes)

        def run(command, target=None):
            self.runs.append((command, target))
            return alone if target else fast

        def do_push(head, branch, lease):
            self.pushed.append((head, branch, lease))
            return push

        def stack_pulls(head, base):
            return [type("P", (), {"number": 5, "html_url": "https://github.com/o/r/pull/5"})() for _ in range(pulls)]

        monkeypatch.setattr(fix, "_script", script)
        monkeypatch.setattr(fix.stack_branch, "ahead", ahead)
        monkeypatch.setattr(fix, "_top", lambda: TOP)
        monkeypatch.setattr(fix, "_rev", rev)
        monkeypatch.setattr(fix, "_ancestor", lambda older, newer: ancestor)
        monkeypatch.setattr(fix, "_log", log)
        monkeypatch.setattr(fix, "_changed", lambda rev_range: list(changed))
        monkeypatch.setattr(fix, "_dirty", lambda: dirty)
        monkeypatch.setattr(fix, "_has", lambda path: has if not isinstance(has, dict) else has.get(path, True))
        monkeypatch.setattr(fix, "_run", run)
        monkeypatch.setattr(fix, "_one_file_command", lambda top: one_file)
        monkeypatch.setattr(fix, "_fast_command", lambda top: fast_command)
        monkeypatch.setattr(fix, "_push", do_push)
        def origin_now(stack_name):
            if isinstance(moved, BaseException):
                raise moved
            return moved

        monkeypatch.setattr(fix, "_origin_now", origin_now)
        monkeypatch.setattr(fix.github, "stack_pulls", stack_pulls)
        monkeypatch.setattr(fix.github, "gh_comment_post", lambda number, body: self.posted.append((number, body)))

    def argv(self, n="12", red=RED):
        return [n, red, str(self.culprit)]


def test_pushes_the_fix_worktrees_head_to_the_stack_under_the_merge_lock_leased_to_the_fetched_tip_printing_its_sha(
        monkeypatch, run_cli, fix, tmp_path):
    world = World(monkeypatch, fix, tmp_path)

    code, out, err = run_cli(fix, world.argv())

    assert (code, out, world.pushed, world.lock_held) == (0, HEAD + "\n", [(HEAD, "stack", ONTO)], False), err
    names = [call[:2] for call in world.scripts]
    assert names.index(("merge-lock.sh", "take")) < names.index(("stack-red.sh",)) and names[-1] == (
        "merge-lock.sh", "release")


def test_a_red_sha_that_is_not_the_commit_stack_red_prints_is_exit_1_naming_the_commit_red_now_nothing_pushed(
        monkeypatch, run_cli, fix, tmp_path):
    world = World(monkeypatch, fix, tmp_path, red_now=sha(7))

    code, _, err = run_cli(fix, world.argv())

    assert (code, world.pushed, sha(7) in err, world.lock_held) == (1, [], True, False), err


@pytest.mark.parametrize("n, text", [
    ("13", culprit_text()),
    ("12", culprit_text(issue="none")),
    ("12", culprit_text(red=sha(5))),
    ("1", culprit_text(issue="11 12")),
])
def test_exits_1_pushing_nothing_when_n_is_not_the_issue_the_culprit_file_names_for_the_red_sha(
        monkeypatch, run_cli, fix, tmp_path, n, text):
    world = World(monkeypatch, fix, tmp_path, culprit=text)

    code, _, err = run_cli(fix, world.argv(n=n))

    assert (code, world.pushed, world.lock_held) == (1, [], False), err


@pytest.mark.parametrize("text", ["", "issue: 12\ncase: %s\tFAILED\n" % CASE, "red: %s\ncase: %s\tx\n" % (RED, CASE),
                                  "red: %s\nissue: 12\n" % RED])
def test_a_culprit_file_without_its_red_issue_or_case_lines_is_exit_2_pushing_nothing(
        monkeypatch, run_cli, fix, tmp_path, text):
    world = World(monkeypatch, fix, tmp_path, culprit=text)

    code, _, err = run_cli(fix, world.argv())

    assert (code, world.pushed) == (2, []), err


@pytest.mark.parametrize("argv", [["x12", RED, "f"], ["12", RED[:12], "f"], ["12", RED, "/no/such/file"], ["12", RED]])
def test_bad_arguments_or_an_unreadable_culprit_file_are_exit_2_before_the_lock(monkeypatch, run_cli, fix, tmp_path,
                                                                                 argv):
    world = World(monkeypatch, fix, tmp_path)

    code, _, err = run_cli(fix, argv)

    assert (code, world.pushed, world.scripts) == (2, [], []), err


@pytest.mark.parametrize("trailers, subject, code", [
    ([sha(1)], "fix: b's earlier fix (#12)", 1),
    ([sha(1)], "fix: c's fix (#13)", 0),
    ([], "fix: b again (#12)", 0),
])
def test_exits_1_pushing_nothing_when_a_commit_of_the_stack_already_carries_a_stack_fix_trailer_and_names_n(
        monkeypatch, run_cli, fix, tmp_path, trailers, subject, code):
    stack = [(sha(1), "feat: a (#11)"), (sha(2), "feat: b (#12)"), (sha(4), subject, trailers), (sha(3), "feat: c (#13)")]
    world = World(monkeypatch, fix, tmp_path, stack_subjects=stack)

    got, _, err = run_cli(fix, world.argv())

    assert (got, len(world.pushed), world.lock_held) == (code, 1 - code, False), err


def test_exits_3_pushing_nothing_when_stack_red_exits_3(monkeypatch, run_cli, fix, tmp_path):
    world = World(monkeypatch, fix, tmp_path, red_code=3)

    code, _, err = run_cli(fix, world.argv())

    assert (code, world.pushed, world.lock_held) == (3, [], False), err


@pytest.mark.parametrize("given", ["red 2", "red 1", "lock", "log", "no stack", "refused", "no origin stack"])
def test_exits_2_pushing_nothing_on_no_answer_from_stack_red_the_lock_the_reads_or_the_fetch(
        monkeypatch, run_cli, fix, tmp_path, given):
    kwargs = {"red 2": {"red_code": 2}, "red 1": {"red_code": 1}, "lock": {"lock": 2}, "log": {"log_fails": True},
              "refused": {"span": fix.stack_branch.Refused("the fetch got no answer (exit 128)")}}.get(given, {})
    world = World(monkeypatch, fix, tmp_path, **kwargs)
    if given == "no stack":
        monkeypatch.setattr(fix.stack_branch, "ahead", lambda root: None)
    if given == "no origin stack":
        monkeypatch.setattr(fix, "_rev", lambda ref: "" if "origin" in ref else HEAD)

    code, _, err = run_cli(fix, world.argv())

    assert (code, world.pushed, world.lock_held) == (2, [], False), err


@pytest.mark.parametrize("fixes, ancestor, code", [
    ([(HEAD, "fix: b's case (#12)", [RED]), (sha(10), "fix: b's other case (#12)", [RED])], True, 0),
    ([(HEAD, "fix: b's case", [RED])], True, 1),
    ([(HEAD, "fix: b's case (#12) and more", [RED])], True, 1),
    ([(HEAD, "fix: b's case (#13)", [RED])], True, 1),
    ([(HEAD, "fix: b's case (#12)", [])], True, 1),
    ([(HEAD, "fix: b's case (#12)", [sha(5)])], True, 1),
    ([(sha(10), "fix: b's case (#12)", [RED]), (HEAD, "fix: more (#12)", [])], True, 1),
    ([], True, 1),
    ([(HEAD, "fix: b's case (#12)", [RED])], False, 1),
    ([(HEAD, "fix: b's case (#12)", [RED])], None, 2),
])
def test_exits_1_pushing_nothing_unless_each_fix_commit_ends_its_subject_n_and_carries_stack_fix_red_sha_above_the_fetched_stack(
        monkeypatch, run_cli, fix, tmp_path, fixes, ancestor, code):
    world = World(monkeypatch, fix, tmp_path, fixes=fixes, ancestor=ancestor)

    got, _, err = run_cli(fix, world.argv())

    assert (got, len(world.pushed), world.lock_held) == (code, 1 if code == 0 else 0, False), err


@pytest.mark.parametrize("changed, named", [
    (("A", "tests/helpers.py"), "tests/helpers.py"),
    (("M", "pkg/test/data.json"), "pkg/test/data.json"),
    (("D", "spec/a_spec.rb"), "spec/a_spec.rb"),
    (("M", "web/__tests__/b.js"), "web/__tests__/b.js"),
    (("M", "src/test_util.py"), "src/test_util.py"),
    (("M", "src/util_test.go"), "src/util_test.go"),
    (("A", "src/util.test.js"), "src/util.test.js"),
    (("M", "src/util.spec.ts"), "src/util.spec.ts"),
    (("R100", "src/a.py", "tests/a.py"), "tests/a.py"),
    (("R087", "tests/a.py", "src/a.py"), "tests/a.py"),
    (("M", "chk/a_check.py"), "chk/a_check.py"),
    (("M", "src/contest.py"), None),
    (("M", "latest/testing.py"), None),
    (("R100", "src/a.py", "src/b.py"), None),
])
def test_a_test_file_the_diff_adds_changes_deletes_or_renames_is_exit_1_naming_it_and_so_is_a_named_cases_file(
        monkeypatch, run_cli, fix, tmp_path, changed, named):
    text = culprit_text(cases=("chk/a_check.py::test_c",))
    world = World(monkeypatch, fix, tmp_path, changed=(("M", "src/b.py"), changed), culprit=text)

    code, _, err = run_cli(fix, world.argv())

    assert (code, len(world.pushed), named is None or named in err) == ((1, 0, True) if named else (0, 1, True)), err


@pytest.mark.parametrize("alone, has, code", [
    ((0, "1 passed\n"), True, 0),
    ((1, "FAILED %s - assert 0\n" % CASE), True, 1),
    ((4, "ERROR: not found: %s\n" % CASE), True, 1),
    ((5, "collected 0 items\n"), True, 1),
    ((1, "1 failed\n"), True, 1),
    ((0, "1 passed\n"), False, 1),
    ((2, "FAILED %s - assert 0\nmake: *** [test] Error 1\n" % CASE), True, 1),
    ((2, "ERROR: not found: %s\nmake: *** [test] Error 4\n" % CASE), True, 1),
    ((0, "no tests ran in 0.01s\n"), True, 1),
    ((2, "make: *** [test] Error 2\n"), True, 2),
    ((3, ""), True, 2),
    ((None, ""), True, 2),
])
def test_each_named_case_runs_alone_at_head_a_red_absent_or_uncollected_one_is_exit_1_naming_it_no_answer_exit_2(
        monkeypatch, run_cli, fix, tmp_path, alone, has, code):
    world = World(monkeypatch, fix, tmp_path, alone=alone, has=has)

    got, _, err = run_cli(fix, world.argv())

    assert (got, len(world.pushed), code == 0 or CASE in err) == (code, 1 if code == 0 else 0, True), err
    assert world.runs[:1] == ([('make test TESTS="$1"', CASE)] if has else [])


def test_runs_every_named_case_alone_and_names_the_red_one(monkeypatch, run_cli, fix, tmp_path):
    second = "t/test_b.py::test_y"
    world = World(monkeypatch, fix, tmp_path, culprit=culprit_text(cases=(CASE, second)))
    monkeypatch.setattr(fix, "_run", lambda command, target=None: world.runs.append(target) or (
        (1, "FAILED %s\n" % target) if target == second else (0, "1 passed\n")))

    code, _, err = run_cli(fix, world.argv())

    assert (code, world.pushed, world.runs[:2], second in err) == (1, [], [CASE, second], True), err


@pytest.mark.parametrize("given", ["no one-file command", "dirty"])
def test_no_one_file_command_is_exit_2_and_uncommitted_changes_exit_1_since_the_runs_would_not_test_head(
        monkeypatch, run_cli, fix, tmp_path, given):
    world = World(monkeypatch, fix, tmp_path, one_file=None if given == "no one-file command" else 'make t "$1"',
                  dirty=" M src/a.py\n" if given == "dirty" else "")

    code, _, err = run_cli(fix, world.argv())

    assert (code, world.pushed, world.runs) == ({"dirty": 1}.get(given, 2), [], []), err


@pytest.mark.parametrize("given, code", [
    ({"fast": (1, "")}, 1),
    ({"fast": (2, "")}, 1),
    ({"fast": (None, "")}, 2),
    ({"fast_command": None}, 2),
    ({"owed": 1}, 1),
    ({"owed": 2}, 2),
    ({"head_after": sha(30)}, 2),
])
def test_a_red_fast_tier_or_a_unit_owing_a_grade_at_head_is_exit_1_and_no_answer_from_either_exit_2(
        monkeypatch, run_cli, fix, tmp_path, given, code):
    world = World(monkeypatch, fix, tmp_path, **given)

    got, _, err = run_cli(fix, world.argv())

    assert (got, world.pushed, world.lock_held) == (code, [], False), err


def test_the_fast_tier_and_prose_owed_run_at_head_in_the_fix_worktree(monkeypatch, run_cli, fix, tmp_path):
    world = World(monkeypatch, fix, tmp_path)

    run_cli(fix, world.argv())

    assert (("make unit", None) in world.runs, ("prose-owed.sh", TOP) in world.scripts) == (True, True)


@pytest.mark.parametrize("given", [
    {"red_now": sha(7)}, {"red_code": 2}, {"fixes": []}, {"changed": (("M", "tests/a.py"),)},
    {"alone": (1, "FAILED %s\n" % CASE)}, {"alone": (None, "")}, {"fast": (1, "")}, {"owed": 1},
    {"push": 1, "moved": sha(20)}, {"push": 1}, {"log_fails": True},
])
def test_every_exit_1_or_2_after_the_lock_pushes_nothing_frees_the_lock_and_keeps_the_fix_worktree_and_its_commits(
        monkeypatch, run_cli, fix, tmp_path, given):
    world = World(monkeypatch, fix, tmp_path, **given)
    git_calls = []
    monkeypatch.setattr(fix.git, "git", lambda *args, **kwargs: git_calls.append(args))
    monkeypatch.setattr(fix.git, "network", lambda *args, **kwargs: git_calls.append(args))

    code, _, err = run_cli(fix, world.argv())

    landed = [push for push in world.pushed if given.get("push") is None]
    assert (code in (1, 2), landed, world.scripts[0][:2], world.scripts[-1][:2], git_calls) == (
        True, [], ("merge-lock.sh", "take"), ("merge-lock.sh", "release"), []), err


@pytest.mark.parametrize("push, origin_after, code", [
    (1, sha(20), 1),
    (1, ONTO, 2),
    (124, sha(20), 1),
    (124, ONTO, 2),
    (124, HEAD, 0),
    (1, "no answer", 2),
])
def test_the_push_is_leased_to_the_fetched_tip_never_forced_and_a_refusal_because_origin_moved_is_exit_1(
        monkeypatch, run_cli, fix, tmp_path, push, origin_after, code):
    moved = fix.NoAnswer("the fetch got no answer") if origin_after == "no answer" else origin_after
    world = World(monkeypatch, fix, tmp_path, push=push, moved=moved)

    got, out, err = run_cli(fix, world.argv())

    assert (got, out, world.pushed, world.lock_held) == (
        code, HEAD + "\n" if code == 0 else "", [(HEAD, "stack", ONTO)], False), err
