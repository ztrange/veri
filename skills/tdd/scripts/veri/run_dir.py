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
here touches the disk except main_tree(), which asks git and raises NoMainTree when it cannot.
"""
import os
import subprocess


class NoMainTree(Exception):
    """git gave no main working tree: not in a repository, git missing, or the directory unusable."""


def main_tree(cwd=None):
    """The repository's main working tree (the first `git worktree list --porcelain` entry), as a str.

    Asks git from `cwd` (default: the current directory). Raises NoMainTree when git is
    missing, `cwd` is unusable, or git names no worktree; never returns "" or bytes."""
    try:
        answer = subprocess.run(["git", "worktree", "list", "--porcelain"], cwd=cwd, capture_output=True, text=True)
    except OSError as error:
        raise NoMainTree(str(error)) from error
    first = answer.stdout.split("\n", 1)[0]
    if answer.returncode or not first.startswith("worktree "):
        raise NoMainTree(f"git names no main working tree from {cwd or os.getcwd()}")
    return first.removeprefix("worktree ")


def main_file(main, name):
    """`<main>/.tdd/<name>`: a file of the main working tree's own state. str, never raises."""
    return os.path.join(main, ".tdd", name)


def worktrees(main):
    """`<main>/.tdd/wt`: the directory holding every run's worktree. str, never raises."""
    return main_file(main, "wt")


def worktree(main, issue):
    """`<main>/.tdd/wt/<issue>`: the run of an issue (int or str). str, never raises."""
    return os.path.join(worktrees(main), str(issue))


def run_file(run, name):
    """The path of `name` inside `run`'s .tdd/ directory. str, never raises."""
    return os.path.join(run, ".tdd", name)


def issue_file(run, issue, suffix=""):
    """`<run>/.tdd/issue-<issue><suffix>`; the suffix carries its own dash or extension. str, never raises."""
    return run_file(run, f"issue-{issue}{suffix}")


def ledger(run, issue):
    """`<run>/.tdd/issue-<issue>.md`: the run's committed ledger. str, never raises."""
    return issue_file(run, issue, ".md")
