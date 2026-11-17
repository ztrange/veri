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


def _handed_back_calls(fake):
    names = fake.names()
    start = names.index("worktree-setup.sh") + 1
    end = names.index("gh", start)
    return [(c[0], c[1]) for c in fake.calls[start:end]]


@pytest.mark.parametrize("ledger", [True, False], ids=["resume", "fresh"])
def test_4023_a_handed_back_worktree_cleans_rebases_marks_and_rerecords_before_reading_the_body(drive, ledger):
    code, out, fake = drive(ledger=ledger, handed_back=True)

    assert code == 0
    assert _handed_back_calls(fake) == [
        ("resume-clean.sh", ()), ("rebase-onto-default.sh", ()), ("git", ("rev-parse", "HEAD")),
        ("event.sh", ("resume-rebase", "from=" + PRE, "rebased=" + POST)),
        ("tests-frozen.sh", ("rerecord-rebased", ".tdd/issue-12.md", PRE))]
    env = fake.call("event.sh", "resume-rebase")[3]
    assert (env["VERI_ISSUE"], env["VERI_ACTOR"]) == ("12", "conductor")


@pytest.mark.parametrize("rebase", [1, 3])
def test_4023_a_rebase_that_did_not_move_the_branch_goes_on_with_no_event_and_no_rerecord(drive, rebase):
    code, out, fake = drive(ledger=True, handed_back=True, answers={("rebase-onto-default.sh", None): (rebase, "")})

    assert code == 0
    assert [c[0] for c in _handed_back_calls(fake)] == ["resume-clean.sh", "rebase-onto-default.sh"]


def test_4023_a_rebase_exit_2_stops_preflight_at_3_with_no_later_call(drive):
    code, out, fake = drive(ledger=True, handed_back=True, answers={("rebase-onto-default.sh", None): (2, "")})

    assert (code, out.splitlines()[-1], fake.names()[-1]) == (2, "stopped at 3 rebase-onto-default.sh",
                                                             "rebase-onto-default.sh")


@pytest.mark.parametrize("rerecord, stops", [(3, False), (1, True)])
def test_4023_rerecord_rebased_exit_3_goes_on_and_any_other_failure_stops(drive, rerecord, stops):
    code, out, fake = drive(ledger=True, handed_back=True, answers={("tests-frozen.sh", None): (rerecord, "")})

    assert (code, fake.names()[-1] == "tests-frozen.sh") == ((1, True) if stops else (0, False))


def test_4023_a_worktree_not_handed_back_runs_none_of_the_handed_back_calls(drive):
    code, out, fake = drive(ledger=True)

    assert _handed_back_calls(fake) == []
