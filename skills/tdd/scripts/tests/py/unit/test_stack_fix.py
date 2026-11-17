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
                 push=0, moved=False, ancestor=True, pulls=1, lock=0, culprit=None, fetch=True, span=None,
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
            return ("stack", "trunk", list(stack)) if span is None else span

        def rev(ref):
            if ref == "HEAD":
                return head_after if head_after and self.runs else self.head
            return ONTO if ref.endswith("/stack") else ""

        def log(rev_range):
            if log_fails:
                raise fix.NoAnswer("git log %s failed (exit 128)" % rev_range)
            if rev_range.startswith("refs/remotes/origin/trunk"):
                return [(commit, subject, []) for commit, subject in stack]
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
        monkeypatch.setattr(fix, "_fetch", lambda: fetch)
        monkeypatch.setattr(fix, "_moved", lambda stack_name, onto: moved)
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
