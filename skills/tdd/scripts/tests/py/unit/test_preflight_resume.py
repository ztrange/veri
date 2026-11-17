"""In-process cases for the resume path of veri/preflight.py (PRD 027.2, #4023)."""
import importlib
import json
import os

import pytest

PRE = "a" * 40
POST = "b" * 40


class Fake:
    """A run_script stand-in: records every call as (script basename, args, cwd, env) and answers from <answers>,
    keyed by (basename, first argument or None) -> (code, stdout)."""

    def __init__(self, wt, answers=None):
        self.wt, self.answers, self.calls = wt, dict(answers or {}), []

    def __call__(self, name, *args, cwd=None, env=None):
        base = os.path.basename(name)
        self.calls.append((base, args, cwd, env))
        for (script, first), (code, out) in self.answers.items():
            if base == script and (first is None or args[:1] == (first,)):
                return code, out, ""
        if base == "issue-worktree.sh":
            return 0, str(self.wt) + "\n", ""
        if base == "detect-test-command.sh":
            return 0, {"fast": "make unit\n", "all": "make test\n"}.get(args[1], "make test TESTS=$1\n"), ""
        if base == "baseline-full-tier.sh":
            return 0, "run\n", ""
        if base == "gh" and args[-1] == ".default_branch":
            return 0, "main\n", ""
        if base == "gh" and args[-1] == ".body":
            return 0, "BODY\n", ""
        if base == "rebase-onto-default.sh":
            return 0, PRE + "\n", ""
        if base == "git" and args == ("rev-parse", "HEAD"):
            return 0, POST + "\n", ""
        if base == "git" and args == ("rev-parse", "--abbrev-ref", "HEAD"):
            return 0, "tdd/12-my-slug\n", ""
        return 0, "", ""

    def names(self):
        return [c[0] for c in self.calls]

    def call(self, base, first=None):
        return next(c for c in self.calls if c[0] == base and (first is None or c[1][:1] == (first,)))


@pytest.fixture
def drive(monkeypatch, run_cli, tmp_path):
    """drive(ledger=False, handed_back=False, answers=None) runs preflight for issue 12 in a worktree a conductor's
    launch made; returns (code, stdout, fake)."""
    preflight = importlib.import_module("veri.preflight")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)

    def go(ledger=False, handed_back=False, answers=None, fake=None):
        if ledger:
            (wt / ".tdd" / "issue-12.md").write_text("- [ ] a step\n")
        if handed_back:
            (wt / ".tdd" / "handed-back").write_text("")
        fake = fake or Fake(wt, answers)
        monkeypatch.setattr(preflight, "run_script", fake)
        code, out, _ = run_cli(preflight, ["12", "my-slug"], cwd=str(tmp_path))
        return code, out, fake

    go.wt = wt
    return go


def test_4023_a_worktree_holding_a_ledger_after_issue_worktree_is_resumed_without_the_claim(drive):
    code, out, fake = drive(ledger=True)

    assert code == 0
    assert "unlabel-issue.sh" not in fake.names()
    assert fake.call("requirements-preflight.sh")[1][1:] == (".tdd/issue-12.md",)


def test_4023_a_branch_only_origin_held_whose_ledger_appears_with_issue_worktree_is_resumed(drive):
    wt = drive.wt

    class Recreating(Fake):
        def __call__(self, name, *args, cwd=None, env=None):
            if os.path.basename(name) == "issue-worktree.sh":
                (wt / ".tdd" / "issue-12.md").write_text("- [ ] a step\n")
            return super().__call__(name, *args, cwd=cwd, env=env)

    code, out, fake = drive(fake=Recreating(wt))

    assert code == 0
    assert "unlabel-issue.sh" not in fake.names()
    assert len(fake.call("requirements-preflight.sh")[1]) == 2


def test_4023_a_fresh_run_still_claims_and_passes_no_ledger(drive):
    code, out, fake = drive()

    assert code == 0
    assert "unlabel-issue.sh" in fake.names()
    assert len(fake.call("requirements-preflight.sh")[1]) == 1
