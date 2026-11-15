"""Throwaway git repositories for process cases: `new_repo` makes one, `commit_all` commits what it holds.

Both run real git, so a case that calls them carries `@pytest.mark.process("git ...")`. `new_repo` sets no identity in the
repository (a case may prove what git does without one); `commit_all` supplies its own, so it works on any repository.
A builder that needs more (a bare repository, a remote, a worktree, a configured identity for plain `git commit`) stays
in its own test file.
"""
import subprocess

IDENTITY = ("-c", "user.name=veri", "-c", "user.email=veri@example.test")


def git(repo, *args):
    """The stripped stdout of `git -C <repo> <args>` as the identity veri@example.test; AssertionError with what git said on failure."""
    done = subprocess.run(["git", "-C", str(repo), *IDENTITY, *args], capture_output=True, text=True)
    assert done.returncode == 0, done.stderr + done.stdout
    return done.stdout.strip()


def new_repo(path, branch="main"):
    """`git init` on <branch> at <path>, made with its missing parents when it does not exist; returns <path>."""
    path.mkdir(parents=True, exist_ok=True)
    git(path, "init", "-q", "-b", branch)
    return path


def commit_all(repo, message, **files):
    """Write each keyword as a file (the name's `__` is a `/`), commit everything in the tree; returns the new HEAD."""
    for name, text in files.items():
        target = repo / name.replace("__", "/")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", message)
    return git(repo, "rev-parse", "HEAD")
