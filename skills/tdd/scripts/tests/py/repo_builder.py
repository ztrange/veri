"""Throwaway git repositories for process cases: `new_repo` makes one, `commit_all` commits what it holds,
`origin_head_at` gives it the origin/HEAD a run's worktree has.

Both run real git, so a case that calls them carries `@pytest.mark.process("git ...")`. `new_repo` sets no identity in the
repository (a case may prove what git does without one); `commit_all` supplies its own, so it works on any repository.
A builder that needs more (a bare repository, a remote, a worktree, a configured identity for plain `git commit`) stays
in its own test file.

`new_repo` runs `git init` once per branch per pytest worker, into a template under TEMPLATE_ROOT (conftest points it at
the worker's `--basetemp`, so the leg's clean-up removes it), and copies that template's `.git` for every later call:
each copy is its own files, never a link into the template (#3931). With no TEMPLATE_ROOT, every call runs `git init`.
"""
import itertools
import shutil
import subprocess

IDENTITY = ("-c", "user.name=veri", "-c", "user.email=veri@example.test")


def git(repo, *args):
    """The stripped stdout of `git -C <repo> <args>` as the identity veri@example.test; AssertionError with what git said on failure."""
    done = subprocess.run(["git", "-C", str(repo), *IDENTITY, *args], capture_output=True, text=True)
    assert done.returncode == 0, done.stderr + done.stdout
    return done.stdout.strip()


TEMPLATE_ROOT = None
_NUMBERS = itertools.count()
TEMPLATES = {}  # (TEMPLATE_ROOT, branch) -> the directory whose `.git` new_repo copies


def new_repo(path, branch="main"):
    """The repository `git init -q -b <branch>` makes, at <path>, made with its missing parents when it does not exist;
    returns <path>."""
    path.mkdir(parents=True, exist_ok=True)
    if TEMPLATE_ROOT is None or (path / ".git").exists():
        git(path, "init", "-q", "-b", branch)
        return path
    template = TEMPLATES.get((TEMPLATE_ROOT, branch))
    if template is None or not (template / ".git").is_dir():  # a new session's --basetemp may have wiped it
        template = TEMPLATE_ROOT / f"template-{next(_NUMBERS)}"
        template.mkdir(parents=True)
        git(template, "init", "-q", "-b", branch)
        TEMPLATES[(TEMPLATE_ROOT, branch)] = template
    shutil.copytree(template / ".git", path / ".git")
    return path


def commit_all(repo, message, *, allow_empty=False, **files):
    """Write each keyword as a file (the name's `__` is a `/`), commit everything in the tree; returns the new HEAD.

    A tree with nothing to commit fails, unless <allow_empty> asks for the empty commit (`allow_empty` is not a file name).
    """
    for name, text in files.items():
        target = repo / name.replace("__", "/")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", *(["--allow-empty"] if allow_empty else []), "-m", message)
    return git(repo, "rev-parse", "HEAD")


def origin_head_at(repo, rev="HEAD"):
    """Point <repo>'s refs/remotes/origin/main at <rev> and origin/HEAD at it, as a real run's worktree has them: outside
    veri's own tree a verifier reads its run lines at the merge base with origin/HEAD, and refuses without one (#4263)."""
    git(repo, "update-ref", "refs/remotes/origin/main", rev)
    git(repo, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")
