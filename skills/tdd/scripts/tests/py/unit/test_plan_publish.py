"""In-process cases for veri/plan_publish.py, the module plan-publish.sh is a shim over (PRD 027.3, #4025)."""
import importlib
import json
import os

import pytest

PLAN_SHA = "c" * 40
PR_URL = "https://github.com/o/r/pull/77"
TITLE = "WIP: feat: a thing (#12)"
LEDGER = "# Plan for #12\n\n- [ ] one ⟦criterion 1⟧\n- [ ] two ⟦criterion 2⟧\n"


class Fake:
    """A run_script stand-in: records (basename, args, cwd, env, kw) and answers from <answers>, keyed by
    (basename, first argument or None) -> (code, stdout)."""

    def __init__(self, answers=None, porcelain=" M .tdd/issue-12.md\n", pr=""):
        self.answers, self.calls, self.porcelain, self.pr = dict(answers or {}), [], porcelain, pr

    def __call__(self, name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        self.calls.append((base, args, cwd, env, kw))
        for (script, first), (code, out) in self.answers.items():
            if base == script and (first is None or args[:1] == (first,)):
                return code, out, ""
        if base == "ledger-steps.sh":
            return 0, "1\topen\tstep\t0\t0\t1\tone\n2\topen\tstep\t0\t0\t2\ttwo\n", ""
        if base == "git" and args == ("status", "--porcelain"):
            return 0, self.porcelain, ""
        if base == "git" and args == ("rev-parse", "HEAD"):
            return 0, PLAN_SHA + "\n", ""
        if base == "git" and args == ("branch", "--show-current"):
            return 0, "tdd/12-a-thing\n", ""
        if base == "stack-branch.sh":
            return 3, "", ""
        if base == "gh" and args[1].startswith("repos/{owner}/{repo}/pulls?head="):
            return 0, self.pr, ""
        if base == "gh" and args[1] == "repos/{owner}/{repo}/pulls":
            return 0, PR_URL + "\n", ""
        if base == "stop-requested.sh":
            return 3, "", ""
        return 0, "", ""

    def names(self):
        return [c[0] for c in self.calls]

    def call(self, base, first=None):
        return next(c for c in self.calls if c[0] == base and (first is None or c[1][:1] == (first,)))


@pytest.fixture
def publish(monkeypatch, run_cli, tmp_path):
    """publish(answers=None, fake=None, missing=()) runs plan-publish for issue 12 from the main tree, the run's
    worktree at .tdd/wt/12; returns (code, stdout, stderr, fake)."""
    fused = importlib.import_module("veri.fused")
    plan_publish = importlib.import_module("veri.plan_publish")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    title = tmp_path / "title.txt"

    def go(answers=None, fake=None, missing=(), argv=None):
        files = {"preflight": (wt / ".tdd" / "issue-12-preflight",
                               "worktree=%s\nfast_cmd=make unit\ndefault_branch=main\nrun=fresh\n" % wt),
                 "ledger": (wt / ".tdd" / "issue-12.md", LEDGER), "title": (title, TITLE + "\n")}
        for key, (path, text) in files.items():
            if key not in missing and not path.exists():
                path.write_text(text)
        fake = fake or Fake(answers)
        monkeypatch.setattr(fused, "run_script", fake)
        code, out, err = run_cli(plan_publish, list(argv if argv is not None else ("12", str(title))),
                                 cwd=str(tmp_path))
        return code, out, err, fake

    go.wt, go.title = wt, title
    return go


def test_4025_no_argument_prints_the_usage_and_exits_2_with_no_inner_call(publish):
    code, out, err, fake = publish(argv=())

    assert (code, "plan-publish.sh <n> <title-file>" in err, fake.calls) == (2, True, [])
    here = os.path.dirname(importlib.import_module("veri.plan_publish").__file__)
    assert os.path.exists(os.path.join(here, "..", "plan-publish.sh"))


@pytest.mark.parametrize("missing, named", [("preflight", ".tdd/issue-12-preflight"), ("ledger", ".tdd/issue-12.md"),
                                            ("title", "title.txt")])
def test_4025_a_missing_input_is_exit_2_before_any_inner_call_named_on_stderr(publish, missing, named):
    code, out, err, fake = publish(missing=(missing,))

    assert (code, fake.calls) == (2, [])
    assert named in err
