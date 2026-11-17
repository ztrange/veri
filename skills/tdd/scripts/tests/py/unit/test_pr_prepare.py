"""In-process cases for veri/pr_prepare.py, the module pr-prepare.sh is a shim over (PRD 027.9, #4031)."""
import importlib
import json
import os

import pytest

LEDGER = "# Plan for #12\n\n- [x] one ⟦criterion 1⟧\n- [ ] the full suite is green ⟦full-suite⟧ ⟦criterion 2⟧\n"
PRE = "a" * 40
BASE = "b" * 40
FULL = "make test"
GRADED_DIFF = ("+++ b/skills/tdd/GRADED\n+skills/tdd/SKILL.md 1234 2026-11-17 x y\n"
               "+++ b/GRADED\n+README.md 99 2026-11-17 x y\n")


class Fake:
    """A run_script stand-in: records (basename, args, cwd, env, kw) and answers from <answers>, keyed by
    (basename, first argument or None) -> (code, stdout)."""

    def __init__(self, answers=None, porcelain=("", ""), mode="local"):
        self.answers, self.calls, self.mode = dict(answers or {}), [], mode
        self.porcelain = list(porcelain)

    def __call__(self, name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        self.calls.append((base, args, cwd, env, kw))
        for (script, first), (code, out) in self.answers.items():
            if base == script and (first is None or args[:1] == (first,)):
                return code, out, ""
        if base == "git" and args[:2] == ("status", "--porcelain"):
            return 0, self.porcelain.pop(0) if self.porcelain else "", ""
        if base == "git" and args[:1] == ("merge-base",):
            return 0, BASE + "\n", ""
        if base == "git" and args[:1] == ("diff",):
            return 0, GRADED_DIFF, ""
        if base == "git" and args[:1] == ("branch",):
            return 0, "tdd/12-x\n", ""
        if base == "git" and args[:1] == ("symbolic-ref",):
            return 0, "origin/main\n", ""
        if base == "next-pending-refactor.sh":
            return 3, "", ""
        if base == "rebase-onto-default.sh":
            return 0, PRE + "\nrebased onto origin/main\n", ""
        if base == "rebased-tip-suite.sh":
            return 0, self.mode + "\n", ""
        if base == "detect-test-command.sh":
            return 0, FULL + "\n", ""
        if base == "detach-command.sh" and args[:1] == ("wait",):
            return 0, "PASSED 812\n", ""
        if base == "refactor-owed.sh":
            return 3, "", ""
        return 0, "", ""

    def names(self):
        return [c[0] for c in self.calls]

    def call(self, base, first=None):
        return next(c for c in self.calls if c[0] == base and (first is None or c[1][:1] == (first,)))


@pytest.fixture
def prep(monkeypatch, run_cli, tmp_path):
    """prep(answers=None, fake=None, missing=(), argv=None) runs pr-prepare for issue 12 from the main tree, the
    run's worktree at .tdd/wt/12; returns (code, stdout, stderr, fake)."""
    fused = importlib.import_module("veri.fused")
    pr_prepare = importlib.import_module("veri.pr_prepare")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)

    def go(answers=None, fake=None, missing=(), argv=None):
        files = {"preflight": (wt / ".tdd" / "issue-12-preflight", "worktree=%s\nfast_cmd=make unit\n" % wt),
                 "ledger": (wt / ".tdd" / "issue-12.md", LEDGER)}
        for key, (path, text) in files.items():
            if key not in missing:
                path.write_text(text)
        fake = fake or Fake(answers)
        monkeypatch.setattr(fused, "run_script", fake)
        code, out, err = run_cli(pr_prepare, list(argv if argv is not None else ("12",)), cwd=str(tmp_path))
        return code, out, err, fake

    go.wt = wt
    return go


def test_4031_no_argument_prints_the_usage_and_exits_2_with_no_inner_call(prep):
    code, out, err, fake = prep(argv=())

    assert (code, "pr-prepare.sh <n>" in err, fake.calls) == (2, True, [])
    here = os.path.dirname(importlib.import_module("veri.pr_prepare").__file__)
    assert os.path.exists(os.path.join(here, "..", "pr-prepare.sh"))


@pytest.mark.parametrize("missing, named", [("preflight", ".tdd/issue-12-preflight"), ("ledger", ".tdd/issue-12.md")])
def test_4031_a_missing_input_is_exit_2_before_any_inner_call_named_on_stderr(prep, missing, named):
    code, out, err, fake = prep(missing=(missing,))

    assert (code, fake.calls) == (2, [])
    assert named in err


def test_4031_a_dirty_tree_stops_it_with_exit_1_before_any_other_call(prep):
    code, out, err, fake = prep(fake=Fake(porcelain=(" M src/a.py\n",)))

    assert (code, out.splitlines()[-1]) == (1, "stopped at 1 tree-check")
    assert [c[0] for c in fake.calls] == ["git"]


def test_4031_a_step_still_only_green_stops_it_with_exit_1_before_the_rebase(prep):
    code, out, err, fake = prep(answers={("next-pending-refactor.sh", None): (0, "one ⟦criterion 1⟧\n")})

    assert (code, out.splitlines()[-1]) == (1, "stopped at 1 next-pending-refactor.sh exit 0")
    assert fake.names() == ["git", "next-pending-refactor.sh"]
    assert fake.call("next-pending-refactor.sh")[4]["stdin"] == LEDGER


def test_4031_a_next_pending_refactor_with_no_answer_stops_it_with_exit_2(prep):
    code, out, err, fake = prep(answers={("next-pending-refactor.sh", None): (2, "")})

    assert (code, fake.names()[-1]) == (2, "next-pending-refactor.sh")
