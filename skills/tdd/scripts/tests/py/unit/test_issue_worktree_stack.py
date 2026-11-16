"""In-process cases for veri/issue_worktree.py in a repository whose CLAUDE.md names a stack branch (PRD 034.1b)."""
import importlib

import pytest

STACK_TIP = "5555555555555555555555555555555555555555"


@pytest.fixture(autouse=True)
def case_works_in_its_scratch_tree(tmp_path, monkeypatch):
    """issue_worktree.py runs git with no cwd; from the case's own tmp_path the git guard sees every call."""
    monkeypatch.chdir(tmp_path)


@pytest.fixture
def issue_worktree():
    return importlib.import_module("veri.issue_worktree")


class Origin:
    """origin as the fake git sees it: which branches it holds, and how each network call answers."""

    def __init__(self, stack=True, push=(0, "", ""), fetch=(0, "", ""), listing=None, created_meanwhile=False):
        self.stack = stack
        self.push = push
        self.fetch = fetch
        self.listing = listing
        self.created_meanwhile = created_meanwhile


def stacked_world(fake_processes, tmp_path, origin, stack_line="veri: stack branch: stack\n"):
    """A main clone at <tmp_path>/repo whose CLAUDE.md holds <stack_line>, origin/HEAD naming trunk, no branch for
    issue 7 anywhere, and <origin> answering the stack's ls-remote, push and fetch. Returns (fake, worktree path)."""
    main_tree = tmp_path / "repo"
    main_tree.mkdir()
    (main_tree / "CLAUDE.md").write_text(stack_line)
    path = "%s/.tdd/wt/7" % main_tree
    registry = "worktree %s\nHEAD 1111111111111111111111111111111111111111\nbranch refs/heads/trunk\n\n" % main_tree

    def ls_stack(line, **_):
        if origin.listing is not None:
            return origin.listing
        return 0, ("%s\trefs/heads/stack\n" % STACK_TIP) if origin.stack else "", ""

    def push(line, **_):
        if origin.created_meanwhile:
            origin.stack = True
        elif origin.push[0] == 0:
            origin.stack = True
        return origin.push

    def ls_after_push(line, **_):
        origin.listing = None
        return ls_stack(line)

    fake = fake_processes.answers({
        "git worktree list --porcelain": (0, registry, ""),
        "git show-ref --verify --quiet": (1, "", ""),
        "git for-each-ref": (0, "", ""),
        "git remote get-url origin": (0, "/srv/origin.git\n", ""),
        "git ls-remote --heads origin refs/heads/tdd/7-*": (0, "", ""),
        "git check-ref-format --branch": lambda line, **_: (0, line.rsplit(" ", 1)[-1] + "\n", ""),
        "git symbolic-ref --quiet --short refs/remotes/origin/HEAD": (0, "origin/trunk\n", ""),
        "git ls-remote --heads origin refs/heads/stack": ls_stack,
        "git fetch -q origin +refs/heads/trunk:refs/remotes/origin/trunk": lambda line, **_: origin.fetch,
        "git push origin refs/remotes/origin/trunk:refs/heads/stack": push,
        "git fetch -q origin +refs/heads/stack:refs/remotes/origin/stack": lambda line, **_: origin.fetch,
        "git worktree add": (0, "", ""),
        "git fetch -q origin trunk": (0, "", ""),
    })
    return fake, path


def added(fake):
    return [c for c in fake.calls if c.startswith("git worktree add")]


def pushes(fake):
    return [c for c in fake.calls if c.startswith("git push")]


def test_cuts_a_new_runs_branch_from_origin_stack_as_just_fetched(fake_processes, tmp_path, capsys, issue_worktree):
    fake, path = stacked_world(fake_processes, tmp_path, Origin(stack=True))

    code = issue_worktree.main(["7", "slug"])

    fetched = fake.calls.index("git fetch -q origin +refs/heads/stack:refs/remotes/origin/stack")
    cut = fake.calls.index("git worktree add -q --no-track -b tdd/7-slug %s origin/stack" % path)
    assert (code, capsys.readouterr().out, fetched < cut, pushes(fake)) == (0, path + "\n", True, [])


def test_with_no_stack_on_origin_pushes_it_at_the_default_branchs_tip_unforced_then_cuts_from_it(
        fake_processes, tmp_path, capsys, issue_worktree):
    fake, path = stacked_world(fake_processes, tmp_path, Origin(stack=False))

    code = issue_worktree.main(["7", "slug"])

    order = [c for c in fake.calls if c.startswith(("git fetch", "git push", "git worktree add"))]
    assert (code, capsys.readouterr().out, order) == (0, path + "\n", [
        "git fetch -q origin +refs/heads/trunk:refs/remotes/origin/trunk",
        "git push origin refs/remotes/origin/trunk:refs/heads/stack",
        "git fetch -q origin +refs/heads/stack:refs/remotes/origin/stack",
        "git worktree add -q --no-track -b tdd/7-slug %s origin/stack" % path])


@pytest.mark.parametrize("push", [(1, "", " ! [rejected] (fetch first)\n"), (124, "", "no answer after 600s\n")])
def test_a_refused_or_unanswered_push_of_the_stack_exits_2_with_no_branch_and_no_worktree(
        fake_processes, tmp_path, capsys, issue_worktree, push):
    fake, path = stacked_world(fake_processes, tmp_path, Origin(stack=False, push=push))

    code = issue_worktree.main(["7", "slug"])

    out, err = capsys.readouterr()
    assert (code, out, added(fake), "stack" in err) == (2, "", [], True)


def test_a_push_refused_because_another_machine_created_the_stack_fetches_it_and_cuts_from_it(
        fake_processes, tmp_path, capsys, issue_worktree):
    origin = Origin(stack=False, push=(1, "", " ! [rejected] stack (fetch first)\n"), created_meanwhile=True)
    fake, path = stacked_world(fake_processes, tmp_path, origin)

    code = issue_worktree.main(["7", "slug"])

    after_push = fake.calls[fake.calls.index("git push origin refs/remotes/origin/trunk:refs/heads/stack") + 1:]
    assert (code, capsys.readouterr().out, after_push[-2:]) == (0, path + "\n", [
        "git fetch -q origin +refs/heads/stack:refs/remotes/origin/stack",
        "git worktree add -q --no-track -b tdd/7-slug %s origin/stack" % path])


@pytest.mark.parametrize("claude_md", ["# no stack named here\n", "The `veri: stack branch:` line is not stated here.\n"])
def test_with_no_stack_branch_named_the_cut_is_from_origin_default_and_nothing_is_pushed(
        fake_processes, tmp_path, capsys, issue_worktree, claude_md):
    fake, path = stacked_world(fake_processes, tmp_path, Origin(stack=False), stack_line=claude_md)

    code = issue_worktree.main(["7", "slug"])

    assert (code, capsys.readouterr().out, pushes(fake), added(fake)) == (
        0, path + "\n", [], ["git worktree add -q --no-track -b tdd/7-slug %s origin/trunk" % path])
