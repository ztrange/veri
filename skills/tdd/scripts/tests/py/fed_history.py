"""fed_history: answers case_history's git queries from a table of named revisions, so a fast-tier case can
drive tests_frozen over a multi-commit history without git (PRD 017.5, R26, R27).

    history = fed_history(("base", "add the suite", {"tests/test_a.py": "def test_a():\n    pass\n"}),
                          ("red", "red: add test_b", {"tests/test_a.py": "...", ".tdd/issue-7.md": "..."}),
                          root=tmp_path, branch="tdd/7-x")

Each revision is `(name, subject, files)`, oldest first, one line of commits; HEAD is the last. `files` maps a path
(relative to `root`) to its text at that revision, or to None when that revision deletes it; a path it does not
name keeps its text from the revision before, as a commit does. A revision is named by its name (which is also its
sha: `commit_of` answers it), by `HEAD`, or by either followed by `~<n>`.

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
            "first_revision_with", "changed_test_files", "commit_of", "step_commits")
REV = re.compile(r"^(?P<name>[^~]+)(?:~(?P<back>\d+))?$")


class FedHistory:
    def __init__(self, revisions, root, branch):
        self.root, self.branch = str(root), branch
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

    def index(self, rev):
        found = REV.match(rev or "")
        if not found:
            return None
        name, back = found.group("name"), int(found.group("back") or 0)
        at = len(self.names) - 1 if name == "HEAD" else (self.names.index(name) if name in self.names else None)
        return at - back if at is not None and at - back >= 0 else None

    def tree(self, rev):
        at = self.index(rev)
        if at is None:
            raise OSError("fed_history: no revision %s" % rev)
        return self.trees[at]

    def touched(self, at, path):
        before = self.trees[at - 1].get(path) if at else None
        return self.trees[at].get(path) != before

    # case_history's answers, in its own signatures.
    def toplevel(self):
        return self.root

    def has_rev(self, rev):
        return self.index(rev) is not None

    def current_branch(self):
        return self.branch

    def text_at(self, rev, path, quiet=False):
        at = self.index(rev)
        return "" if at is None else self.trees[at].get(os.path.normpath(path), "")

    def cases_at(self, rev, path):
        text = self.tree(rev).get(os.path.normpath(path))
        return {} if text is None else dict(cut_cases(text))

    def revisions(self, path, since=None):
        path = os.path.normpath(path)
        start = 0 if since is None else self.index(since) + 1
        return [self.names[at] for at in range(len(self.names) - 1, start - 1, -1) if self.touched(at, path)]

    def first_revision_with(self, needle, path):
        path = os.path.normpath(path)
        for at, name in enumerate(self.names):
            before = self.trees[at - 1].get(path, "") if at else ""
            if self.trees[at].get(path, "").count(needle) != before.count(needle):
                return name
        return ""

    def commit_of(self, rev):
        at = self.index(rev)
        if at is None:
            raise OSError("fed_history: no commit %s" % rev)
        return self.names[at]

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
            text = self.tree(rev).get(os.path.normpath(path))
            if text is None:
                raise OSError("fed_history: %s absent at %s" % (path, rev))
            return ledger.ledger_items(text)

        saved = case_history._out, ledger.items_at
        case_history._out, ledger.items_at = out, items_at
        try:
            return real(step, issue)
        finally:
            case_history._out, ledger.items_at = saved


def unanswered(name):
    def query(*args, **kwargs):
        pytest.fail("fed_history does not answer case_history.%s" % name)
    return query


def feeder(monkeypatch, default_root):
    """The fed_history fixture's value: call it with the revisions to feed case_history from them."""
    def feed(*revisions, root=None, branch="main"):
        history = FedHistory(revisions, root or default_root, branch)
        for name, value in list(vars(case_history).items()):
            if callable(value) and not name.startswith("_") and getattr(value, "__module__", "") in ("case_history",
                                                                                                    __name__):
                monkeypatch.setattr(case_history, name,
                                    getattr(history, name) if name in ANSWERED else unanswered(name))
        return history
    return feed
