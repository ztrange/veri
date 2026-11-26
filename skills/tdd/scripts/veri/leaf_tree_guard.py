"""Did a leaf change the repository, and put it back: the verifier's tree guard.

A verifier leaf must change nothing. `verify` snapshots the repository before the leaf runs, asks the guard
what changed after each run, and has the guard put a changed tree back before relaunching or refusing.
The guard returns values and prints nothing; the refusal lines are `verify`'s.

Interface:
- `snapshot()` -> `Guard`, or `Unreadable` / `ConfigUnreadable` when the before-state cannot be read.
- `Guard.tree`: the before tree's sha, "" when none was taken (not a repository, git missing, a failing
  `add`): then no tree, HEAD or untracked check is made.
- `Guard.changes()` -> the first finding, in this order: `Unreadable(detail)` (the tree after cannot be
  written), `Changed(paths, before, after)`, `ConfigUnreadable(path, strerror)`, `ConfigChanged(path)`;
  None when nothing changed.
- `Guard.restore(changed)` -> False when a moved HEAD could not be put back, else True.
- `Guard.restore_unreadable()` -> git's complaint naming the file that cannot be read.

Semantics:

| What | How |
|---|---|
| tree | `git add -A` then `git write-tree` into a temporary `GIT_INDEX_FILE` (a fresh directory outside the repo per call); "" when either fails |
| tree unreadable | an empty before tree whose `git add -A` (`LC_ALL=C`) fails saying `Permission denied`; its stderr is the detail |
| HEAD | `git rev-parse --verify HEAD` |
| untracked | `git ls-files --others --exclude-standard -z` |
| config | the bytes of `$HOME/.gitconfig`, None when absent; any other read error is `ConfigUnreadable` |
| changed paths | `git diff-tree -r -z --name-only --no-commit-id <before> <after>`, then `HEAD` when it moved |
| mode flip | a path whose only change is 100644 <-> 100755 (`git diff --raw -z --no-renames`) is chmod-ed back on the spot and not reported |
| unreadable after | a non-empty before tree and an empty after tree |
| restore (changed) | `read-tree -u --reset <before>` in a temporary index (after `add -A` into it), then `git update-ref HEAD <head-before>` when HEAD moved |
| restore (unreadable) | `read-tree <before>` and `checkout-index -a -f` in a temporary index, read the complaint, then remove each path untracked now but not before |
| config changed | the bytes differ; never restored |
"""
import contextlib
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass


@dataclass
class Unreadable:
    """The tree cannot be written: `detail` is git's complaint ("" after the leaf: restore_unreadable reads it)."""
    detail: str = ""


@dataclass
class Changed:
    """The leaf changed these paths (`HEAD` last when it moved) between trees `before` and `after`."""
    paths: list
    before: str
    after: str
    head: str


@dataclass
class ConfigUnreadable:
    """`$HOME/.gitconfig` exists but cannot be read."""
    path: str
    strerror: str


@dataclass
class ConfigChanged:
    """`$HOME/.gitconfig` differs from its bytes before the leaf."""
    path: str


def start(args, **kwargs):
    try:
        return subprocess.run(args, **kwargs)
    except OSError:
        return subprocess.CompletedProcess(args, 127, b"")


def git(*args, env=None):
    return start(["git", *args], env=env, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)


@contextlib.contextmanager
def temp_index_env():
    folder = tempfile.mkdtemp()
    try:
        yield {**os.environ, "GIT_INDEX_FILE": os.path.join(folder, "index")}
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def in_temp_index(*args):
    """`git <args>` over a temporary index holding the work tree (`add -A`); its stdout, "" on any failure."""
    with temp_index_env() as env:
        if git("add", "-A", env=env).returncode:
            return ""
        out = git(*args, env=env)
        return out.stdout.decode().rstrip("\n") if out.returncode == 0 else ""


def unreadable_file_in_tree():
    with temp_index_env() as env:
        env = {**env, "LC_ALL": "C"}
        added = start(["git", "add", "-A"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        if added.returncode == 0 or b"Permission denied" not in (added.stderr or b""):
            return ""
        return (added.stderr or b"").decode("utf-8", "replace").strip()


def restore_tree(tree):
    with temp_index_env() as env:
        git("read-tree", tree, env=env)
        git("checkout-index", "-a", "-f", env=env)


def untracked_paths():
    out = git("ls-files", "--others", "--exclude-standard", "-z")
    return set(out.stdout.decode("utf-8", "surrogateescape").split("\0")) - {""}


def head_snapshot():
    return git("rev-parse", "--verify", "HEAD").stdout.decode().rstrip("\n")


def changed_paths(tree_before, head_before):
    if not tree_before:
        return [], head_before, ""
    tree_after = in_temp_index("write-tree")
    head_after = head_snapshot()
    diff = git("diff-tree", "-r", "-z", "--name-only", "--no-commit-id", tree_before, tree_after)
    paths = [p for p in diff.stdout.decode("utf-8", "surrogateescape").split("\0") if p] if diff.returncode == 0 else []
    if paths:
        # -z: git quotes a non-ASCII or odd name otherwise, and os.chmod would get the quoted text (#3087).
        raw = git("diff", "--raw", "-z", "--no-renames", tree_before, tree_after)
        fields_and_paths = raw.stdout.decode("utf-8", "surrogateescape").split("\0") if raw.returncode == 0 else []
        for meta, path in zip(fields_and_paths[0::2], fields_and_paths[1::2], strict=False):
            fields = meta[1:].split()
            if len(fields) == 5 and fields[4] == "M" and fields[2] == fields[3] and path in paths \
                    and {fields[0], fields[1]} == {"100755", "100644"}:
                os.chmod(path, 0o755 if fields[0] == "100755" else 0o644)
                paths.remove(path)
    if head_after != head_before:
        paths.append("HEAD")
    return paths, head_after, tree_after


def gitconfig_snapshot(path):
    try:
        with open(path, "rb") as config:
            return config.read()
    except FileNotFoundError:
        return None


class Guard:
    """The before-state of one leaf; see the module docstring."""

    def __init__(self, tree, head, untracked, config, config_before):
        self.tree, self.head, self.untracked = tree, head, untracked
        self.config, self.config_before = config, config_before

    def changes(self):
        paths, head_after, tree_after = changed_paths(self.tree, self.head)
        if self.tree and not tree_after:
            return Unreadable()
        if paths:
            return Changed(paths, self.tree, tree_after, head_after)
        try:
            config_after = gitconfig_snapshot(self.config)
        except OSError as error:
            return ConfigUnreadable(self.config, error.strerror)
        if config_after != self.config_before:
            return ConfigChanged(self.config)
        return None

    def restore(self, changed):
        in_temp_index("read-tree", "-u", "--reset", self.tree)
        if self.head and self.head != changed.head:
            return start(["git", "update-ref", "HEAD", self.head]).returncode == 0
        return True

    def restore_unreadable(self):
        restore_tree(self.tree)
        unreadable = unreadable_file_in_tree()
        for added in untracked_paths() - self.untracked:
            os.remove(added)
        return unreadable


def snapshot():
    tree = in_temp_index("write-tree")
    if not tree:
        unreadable = unreadable_file_in_tree()
        if unreadable:
            return Unreadable(unreadable)
    head = head_snapshot()
    untracked = untracked_paths()
    config = os.environ["HOME"] + "/.gitconfig"
    try:
        config_before = gitconfig_snapshot(config)
    except OSError as error:
        return ConfigUnreadable(config, error.strerror)
    return Guard(tree, head, untracked, config, config_before)
