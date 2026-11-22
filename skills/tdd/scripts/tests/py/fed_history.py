"""fed_history: answers case_history's git queries from a table of named revisions, so a fast-tier case can
drive tests_frozen over a multi-commit history without git (PRD 017.5, R26, R27).

    history = fed_history(("base", "add the suite", {"tests/test_a.py": "def test_a():\n    pass\n"}),
                          ("red", "red: add test_b", {"tests/test_a.py": "...", ".tdd/issue-7.md": "..."}),
                          root=tmp_path, branch="tdd/7-x")

Each revision is `(name, subject, files)`, oldest first, one line of commits; HEAD is the last. `files` maps a path
(relative to `root`) to its text at that revision, or to None when that revision deletes it; a path it does not
name keeps its text from the revision before, as a commit does. A query may name a path absolute under `root`, as
git takes it. A revision is named by its name (which is also its
sha: `commit_of` answers it), by `HEAD`, or by either followed by `~<n>` or by `^` (`~1`, its first
parent); `subject` answers its subject.
`refs={"origin/main": "<name>"}` names a revision of the line by a ref as well; `detached={"<name>": (subject,
{path: text}[, parent])}` adds revisions off the line, each holding exactly the files it names (a commit a rebase left
behind), readable by name (and through `parent`, a revision name, by `^` and `~<n>`) but in no `revisions` answer; `default="main"` is what `default_branch` answers, and
without it `default_branch` is not answered.

The work tree is the real directory `root` (default the case's tmp_path): the case writes the files it holds,
and `changed_test_files` compares them with HEAD as `git diff HEAD` plus untracked files would, skipping `.git/`
and `.tdd/`.

Every public function of case_history the table does not answer fails the case naming it, through
`pytest.fail`, which no `except Exception` in the code under test swallows.
"""
import os
import re

import pytest

import case_history
import ledger
from case_reader import cut_cases, is_js_test_file, is_test_path

ANSWERED = ("toplevel", "has_rev", "current_branch", "text_at", "cases_at", "revisions",
            "first_revision_with", "changed_test_files", "commit_of", "step_commits", "subject", "default_branch",
            "paths_at")
REV = re.compile(r"^(?P<name>[^~^]+)(?:~(?P<back>\d+)|(?P<parent>\^))?$")


class FedHistory:
    def __init__(self, revisions, root, branch, refs=None, detached=None, default=None):
        self.root, self.branch, self.refs, self.default = str(root), branch, dict(refs or {}), default
        self.detached = {name: {os.path.normpath(path): text for path, text in spec[1].items()}
                         for name, spec in (detached or {}).items()}
        self.parents = {name: spec[2] for name, spec in (detached or {}).items() if len(spec) > 2}
        self.names, self.subjects, self.trees = [], {}, []
        tree = {}
        for name, subject, files in revisions:
            tree = dict(tree)
            for path, text in files.items():
                if text is None:
                    tree.pop(os.path.normpath(path), None)
                else:
                    tree[os.path.normpath(path)] = text
            self.names.append(name)
            self.subjects[name] = subject
            self.trees.append(tree)
        self.subjects.update((name, spec[0]) for name, spec in (detached or {}).items())

    def parse(self, rev):
        """(name, back) of `rev`: its ref resolved, `^` as one generation back; None when it is not a revision."""
        found = REV.match(rev or "")
        if not found:
            return None
        return (self.refs.get(found.group("name"), found.group("name")),
                1 if found.group("parent") else int(found.group("back") or 0))

    def index(self, rev):
        parsed = self.parse(rev)
        if parsed is None:
            return None
        name, back = parsed
        at = len(self.names) - 1 if name == "HEAD" else (self.names.index(name) if name in self.names else None)
        return at - back if at is not None and at - back >= 0 else None

    def lookup(self, rev):
        """(name, tree) of the revision `rev` names, on the line or detached (walking a detached revision's parents
        for `^` and `~<n>`); None when it names none."""
        parsed = self.parse(rev)
        if parsed is None:
            return None
        name, back = parsed
        while name in self.detached:
            if not back:
                return name, self.detached[name]
            name, back = self.parents.get(name), back - 1
        at = self.index("%s~%d" % (name, back)) if name else None
        return None if at is None else (self.names[at], self.trees[at])

    def tree(self, rev):
        found = self.lookup(rev)
        if found is None:
            raise OSError("fed_history: no revision %s" % rev)
        return found[1]

    def path(self, path):
        """The repository-relative path git reads for `path`: an absolute one under the root is taken relative to it."""
        return os.path.normpath(os.path.relpath(path, self.root) if os.path.isabs(path) else path)

    def touched(self, at, path):
        before = self.trees[at - 1].get(path) if at else None
        return self.trees[at].get(path) != before

    # case_history's answers, in its own signatures.
    def toplevel(self):
        return self.root

    def has_rev(self, rev):
        return self.lookup(rev) is not None

    def default_branch(self):
        if self.default is None:
            pytest.fail("fed_history does not answer case_history.default_branch")
        return self.default

    def current_branch(self):
        return self.branch

    def text_at(self, rev, path, quiet=False):
        found = self.lookup(rev)
        return "" if found is None else found[1].get(self.path(path), "")

    def paths_at(self, rev, directory):
        """The repository-relative files directly in `directory` at `rev`, sorted as git ls-tree lists them; [] for a
        revision the table does not hold."""
        found = self.lookup(rev)
        directory = self.path(directory).rstrip(os.sep) if directory else ""
        directory = "" if directory == "." else directory
        return [] if found is None else sorted(path for path in found[1] if os.path.dirname(path) == directory)

    def cases_at(self, rev, path):
        text = self.tree(rev).get(self.path(path))
        return {} if text is None else dict(cut_cases(text))

    def revisions(self, path, since=None):
        """With `since` naming no revision of the line (unknown, or detached: the table holds no ancestry for it),
        [] as case_history answers when git log fails."""
        path = self.path(path)
        if since and self.index(since) is None:
            return []
        start = self.index(since) + 1 if since else 0
        return [self.names[at] for at in range(len(self.names) - 1, start - 1, -1) if self.touched(at, path)]

    def first_revision_with(self, needle, path):
        path = self.path(path)
        for at, name in enumerate(self.names):
            before = self.trees[at - 1].get(path, "") if at else ""
            if self.trees[at].get(path, "").count(needle) != before.count(needle):
                return name
        return ""

    def commit_of(self, rev):
        found = self.lookup(rev)
        if found is None:
            raise OSError("fed_history: no commit %s" % rev)
        return found[0]

    def subject(self, rev):
        """As `git log -1 --format=%s <rev>` prints it: the subject and a newline; "" for a revision it does not hold,
        as case_history answers when git log fails."""
        found = self.lookup(rev)
        return "" if found is None else self.subjects[found[0]] + "\n"

    def changed_test_files(self):
        head = self.trees[-1] if self.trees else {}
        on_disk = {}
        for top, dirs, files in os.walk(self.root):
            dirs[:] = [d for d in dirs if not (top == self.root and d in (".git", ".tdd"))]
            for file in files:
                path = os.path.relpath(os.path.join(top, file), self.root)
                with open(os.path.join(top, file), encoding="utf-8", errors="replace") as handle:
                    on_disk[path] = handle.read()
        tracked = sorted(path for path in head if on_disk.get(path) != head[path])
        untracked = sorted(path for path in on_disk if path not in head)
        return [path for path in tracked + untracked
                if is_test_path(path.encode()) or is_js_test_file(os.path.basename(path), os.path.dirname(path))]

    def step_commits(self, step, issue, real=case_history.step_commits):
        """case_history's own step_commits, its two git reads (`_out`, `ledger.items_at`) answered from the table."""
        def out(*argv):
            if argv[:3] == ("log", "--reverse", "--format=%H") and argv[3] == "--":
                return "\n".join(reversed(self.revisions(argv[4]))) + "\n"
            if argv[0] == "rev-list":
                low, high = (self.index(rev) for rev in argv[1].split(".."))
                return "\n".join(self.names[at] for at in range(high, low, -1)) + "\n"
            pytest.fail("fed_history does not answer case_history._out%r" % (argv,))

        def items_at(rev, path):
            text = self.tree(rev).get(self.path(path))
            if text is None:
                raise OSError("fed_history: %s absent at %s" % (path, rev))
            return ledger.ledger_items(text)

        saved = case_history._out, ledger.items_at
        case_history._out, ledger.items_at = out, items_at
        try:
            return real(step, issue)
        finally:
            case_history._out, ledger.items_at = saved


class FedCommits:
    """A git index and commit log over the work tree `root`, every commit fed to case_history through `feed`, so a
    case ports `git add`, `git commit [-a]` and `git mv` one call each, and a rebase as `checkout` of the revision it
    starts from, the commits on top, and `ref("origin/<default>")`. Revisions are named c1, c2, ... in order."""

    def __init__(self, feed, root, branch, default=None):
        self.feed, self.root, self.branch, self.default = feed, str(root), branch, default
        self.revisions, self.tree, self.index = [], {}, {}
        self.snapshots, self.refs, self.detached = {}, {}, {}
        self._feed()

    def _feed(self):
        self.feed(*self.revisions, root=self.root, branch=self.branch, refs=self.refs, detached=self.detached,
                  default=self.default)

    @property
    def head(self):
        return self.revisions[-1][0] if self.revisions else ""

    def _on_disk(self, path):
        full = os.path.join(self.root, path)
        if os.path.isfile(full):
            return [os.path.normpath(path)]
        return [os.path.relpath(os.path.join(top, file), self.root) for top, _, files in os.walk(full) for file in files]

    def _read(self, path):
        with open(os.path.join(self.root, path), encoding="utf-8", errors="replace") as handle:
            return handle.read()

    def add(self, *paths):
        """As `git add <paths>`: each file under a path is staged as it reads now; a staged one gone from disk is unstaged."""
        for path in paths:
            prefix = os.path.normpath(path)
            for name in [n for n in self.index if n == prefix or n.startswith(prefix + os.sep)]:
                if not os.path.isfile(os.path.join(self.root, name)):
                    del self.index[name]
            for name in self._on_disk(path):
                self.index[name] = self._read(name)

    def mv(self, source, target):
        """As `git mv <source> <target>`."""
        os.makedirs(os.path.dirname(os.path.join(self.root, target)) or self.root, exist_ok=True)
        os.rename(os.path.join(self.root, source), os.path.join(self.root, target))
        self.index[os.path.normpath(target)] = self.index.pop(os.path.normpath(source))

    def commit(self, subject, all=False):
        """As `git commit [-a] -m <subject>`; returns the new revision's name."""
        if all:
            self.add(*list(self.index))
        files = {name: text for name, text in self.index.items() if self.tree.get(name) != text}
        files.update({name: None for name in self.tree if name not in self.index})
        self.tree = dict(self.index)
        name = "c%d" % (len(self.snapshots) + 1)
        self.revisions.append((name, subject, files))
        self.snapshots[name] = (subject, dict(self.tree))
        self._feed()
        return self.head

    def checkout(self, rev):
        """As `git checkout` of a branch whose tip is the revision `rev` of this log: the log is cut back to `rev`, each
        later revision staying readable by its name (detached, as the commits a rebase replaces stay), and the index
        and the work tree's tracked files are set to `rev`'s tree; untracked files are left alone."""
        names = [name for name, _, _ in self.revisions]
        for parent, name in zip(names[names.index(rev):], names[names.index(rev) + 1:]):
            self.detached[name] = self.snapshots[name] + (parent,)
        self.revisions = self.revisions[:names.index(rev) + 1]
        old, self.tree = self.tree, dict(self.snapshots[rev][1])
        self.index = dict(self.tree)
        for path in old:
            if path not in self.tree and os.path.isfile(os.path.join(self.root, path)):
                os.remove(os.path.join(self.root, path))
        for path, text in self.tree.items():
            os.makedirs(os.path.dirname(os.path.join(self.root, path)), exist_ok=True)
            with open(os.path.join(self.root, path), "w", encoding="utf-8") as handle:
                handle.write(text)
        self._feed()

    def ref(self, name):
        """As `git push origin <default>` then `git fetch`: the ref `name` (e.g. origin/main) names this log's head."""
        self.refs[name] = self.head
        self._feed()

    def git_answers(self):
        """fake_processes answers for the git calls of frozen_record's pass marker: .tdd not ignored, the work-tree
        hash `fed-tree`, and HEAD this log's head (unborn before the first commit)."""
        return {"git check-ignore": (1, "", ""), "git add -A": (0, "", ""), "git write-tree": (0, "fed-tree\n", ""),
                "git rev-parse HEAD": lambda line, **kwargs: (0, self.head + "\n", "") if self.head
                else (128, "", "fatal: ambiguous argument 'HEAD'\n")}


def unanswered(name):
    def query(*args, **kwargs):
        pytest.fail("fed_history does not answer case_history.%s" % name)
    return query


def feeder(monkeypatch, default_root):
    """The fed_history fixture's value: call it with the revisions to feed case_history from them."""
    def feed(*revisions, root=None, branch="main", refs=None, detached=None, default=None):
        history = FedHistory(revisions, root or default_root, branch, refs, detached, default)
        for name, value in list(vars(case_history).items()):
            if callable(value) and not name.startswith("_") and getattr(value, "__module__", "") in ("case_history",
                                                                                                    __name__):
                monkeypatch.setattr(case_history, name,
                                    getattr(history, name) if name in ANSWERED else unanswered(name))
        return history
    return feed
