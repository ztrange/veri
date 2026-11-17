"""Where a veri run lives on disk: the one module that spells the layout.

    <main>/.tdd/                      the main working tree's state: locks, role-*.state,
                                      status-last, report-cache.json, ...      main_file()
    <main>/.tdd/wt/                   every run's worktree                      worktrees()
    <main>/.tdd/wt/<n>/              the run of issue <n> (a git worktree)     worktree()
    <run>/.tdd/<name>                 a run's own state: events.jsonl, stop,
                                      restart-pending, pinned-scripts, ...      run_file()
    <run>/.tdd/issue-<n><suffix>      per-issue records: issue-<n>.md (the
                                      ledger), -spec.md, -skill-commit,
                                      -released, -timeout, ...                  issue_file(), ledger()

`<main>` is the repository's main working tree (main_tree()); `<run>` is any directory that
holds a `.tdd/`, normally a worktree() but also the main tree itself. Paths are str; nothing
here touches the disk except main_tree(), which asks git and raises NoMainTree when it cannot, and
main_tree_from_files(), which reads `.git` files and starts no process.
"""
import os
import re
import subprocess


class NoMainTree(Exception):
    """git gave no main working tree: not in a repository, git missing, or the directory unusable."""


_RAISE = object()


def main_tree(cwd=None, *, missing=_RAISE):
    """The repository's main working tree (the first `git worktree list --porcelain` entry), as a str.

    Asks git from `cwd` (default: the current directory); a first line without the `worktree `
    prefix is taken as the tree itself, as the copies this replaced did. When git is missing, `cwd` is
    unusable or git names no worktree, raises NoMainTree, or returns `missing` (any value,
    "" and None included) when the caller gave one; never returns bytes."""
    try:
        answer = subprocess.run(["git", "worktree", "list", "--porcelain"], cwd=cwd, capture_output=True, text=True)
    except OSError as error:
        if missing is not _RAISE:
            return missing
        raise NoMainTree(str(error)) from error
    first = answer.stdout.split("\n", 1)[0]
    if answer.returncode or not first:
        if missing is not _RAISE:
            return missing
        raise NoMainTree(f"git names no main working tree from {cwd or os.getcwd()}")
    return first.removeprefix("worktree ")


def main_tree_from_files(start=None):
    """The main working tree above `start` (default: the current directory), found by reading `.git`
    files, starting no process: walks up to the first `.git`; a directory is the tree itself, a file
    names a gitdir whose `commondir` leads to the main tree. No `.git` up to the root answers
    `start` itself. OSError when a linked gitdir has no readable `commondir`."""
    start = os.getcwd() if start is None else start
    directory = os.path.abspath(start)
    while True:
        dotgit = os.path.join(directory, ".git")
        if os.path.isdir(dotgit):
            return directory
        if os.path.isfile(dotgit):
            with open(dotgit) as f:
                gitdir = f.read().strip().removeprefix("gitdir:").strip()
            gitdir = os.path.join(directory, gitdir)
            with open(os.path.join(gitdir, "commondir")) as f:
                common = os.path.join(gitdir, f.read().strip())
            return os.path.dirname(os.path.normpath(common))
        parent = os.path.dirname(directory)
        if parent == directory:
            return os.path.abspath(start)
        directory = parent


def worktree_root_from_files(start=None):
    """The working tree holding `start` (default: the current directory), a linked worktree's own root included,
    found by walking up to the first `.git` (directory or file), starting no process; no `.git` up to the root
    answers `start` itself. str, never raises."""
    start = os.getcwd() if start is None else start
    directory = os.path.abspath(start)
    while not os.path.exists(os.path.join(directory, ".git")):
        parent = os.path.dirname(directory)
        if parent == directory:
            return os.path.abspath(start)
        directory = parent
    return directory


def main_file(main, name):
    """`<main>/.tdd/<name>`: a file of the main working tree's own state. str, never raises."""
    return os.path.join(main, ".tdd", name)


def worktrees(main):
    """`<main>/.tdd/wt`: the directory holding every run's worktree. str, never raises."""
    return main_file(main, "wt")


def worktree(main, issue):
    """`<main>/.tdd/wt/<issue>`: the run of an issue (int or str). str, never raises."""
    return os.path.join(worktrees(main), str(issue))


def branch_issue(name):
    """The issue a run's branch `tdd/<n>-<slug>` names, as a str, or None for any other branch name. Never raises."""
    found = re.fullmatch(r"tdd/(\d+)-.+", name or "")
    return found.group(1) if found else None


def main_of_worktree(run):
    """The main working tree a run directory sits under, read from the layout alone
    (`<main>/.tdd/wt/<n>` gives `<main>`), or None for any other directory. str, never raises."""
    wt = os.path.dirname(os.path.normpath(run))
    state = os.path.dirname(wt)
    if os.path.basename(wt) == "wt" and os.path.basename(state) == ".tdd":
        return os.path.dirname(state)
    return None


def run_file(run, name):
    """The path of `name` inside `run`'s .tdd/ directory. str, never raises."""
    return os.path.join(run, ".tdd", name)


def issue_file(run, issue, suffix=""):
    """`<run>/.tdd/issue-<issue><suffix>`; the suffix carries its own dash or extension. str, never raises."""
    return run_file(run, f"issue-{issue}{suffix}")


def ledger(run, issue):
    """`<run>/.tdd/issue-<issue>.md`: the run's committed ledger. str, never raises."""
    return issue_file(run, issue, ".md")
