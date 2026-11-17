"""In-process cases for veri/pr_finish.py, the module pr-finish.sh is a shim over (PRD 027.11, #4033)."""
import importlib
import os

import pytest

URL = "https://github.com/o/r/pull/42"
HEAD = "b" * 40
LEDGER = ("# Plan for #12\n\n- [x] one ⟦criterion 1⟧\n- [ ] the full suite is green ⟦full-suite⟧ ⟦criterion 2⟧\n"
          "- [ ] the full suite is green on the rebased tip ⟦full-suite⟧ ⟦criterion 3⟧\n")
BODY = "## Acceptance criteria\n\n- [x] one\n- [ ] two\n- [ ] three\n"


class Fake:
    """A run_script stand-in: records (basename, args, cwd, env, kw) and answers from <answers>, keyed by
    (basename, first argument or None) -> (code, stdout) or (code, stdout, {redirected path: its text}). tick-ledger.sh
    exits 0 <ticks> times, then 3."""

    def __init__(self, answers=None, mode="ci", ticks=2):
        self.answers, self.calls, self.mode, self.ticks = dict(answers or {}), [], mode, ticks

    def __call__(self, name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        self.calls.append((base, args, cwd, env, kw))
        for (script, first), answer in self.answers.items():
            if base == script and (first is None or args[:1] == (first,)):
                for path, text in (answer[2] if len(answer) > 2 else {}).items():
                    with open(os.path.join(cwd, path), "w") as f:
                        f.write(text)
                return answer[0], answer[1], ""
        if base == "gh":
            return 0, (BODY if "issues/12" in args[1] else URL + "\n"), ""
        if base == "git" and args[:1] == ("branch",):
            return 0, "tdd/12-thing\n", ""
        if base == "git" and args[:1] == ("rev-parse",):
            return 0, HEAD + "\n", ""
        if base == "branch-suite.sh":
            return 0, self.mode + "\n", ""
        if base == "tick-ledger.sh":
            self.ticks -= 1
            return (0 if self.ticks >= 0 else 3), "", ""
        if base == "ledger-steps.sh" and args[:1] == ("criterion",):
            return 0, {"2": "two", "3": "three"}[args[1]] + "\n", ""
        if base == "metrics.sh":
            with open(os.path.join(cwd, kw["out"]), "w") as f:
                f.write("## Metrics\n")
            return 0, "", ""
        if base == "refactor-owed.sh":
            return 0, "## Refactor owed\n\n- extract it\n", ""
        return 0, "", ""

    def names(self):
        return [c[0] for c in self.calls]

    def made(self, base, first=None):
        return [c for c in self.calls if c[0] == base and (first is None or c[1][:1] == (first,))]


@pytest.fixture
def finish(monkeypatch, run_cli, tmp_path):
    """finish(answers=None, fake=None, missing=(), argv=None, ledger=LEDGER) runs pr-finish for issue 12 from the main
    tree, the run's worktree at .tdd/wt/12; returns (code, stdout, stderr, fake)."""
    fused = importlib.import_module("veri.fused")
    pr_finish = importlib.import_module("veri.pr_finish")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)

    def go(answers=None, fake=None, missing=(), argv=None, ledger=LEDGER):
        files = {"preflight": (wt / ".tdd" / "issue-12-preflight", "worktree=%s\nfast_cmd=make unit\n" % wt),
                 "ledger": (wt / ".tdd" / "issue-12.md", ledger)}
        for key, (path, text) in files.items():
            if key not in missing:
                path.write_text(text)
        fake = fake or Fake(answers)
        monkeypatch.setattr(fused, "run_script", fake)
        code, out, err = run_cli(pr_finish, list(argv if argv is not None else ("12",)), cwd=str(tmp_path))
        return code, out, err, fake

    go.wt = wt
    return go


def test_4033_no_argument_prints_the_usage_and_exits_2_with_no_inner_call(finish):
    code, out, err, fake = finish(argv=())

    assert (code, "pr-finish.sh <n>" in err, fake.calls) == (2, True, [])
    here = os.path.dirname(importlib.import_module("veri.pr_finish").__file__)
    assert os.path.exists(os.path.join(here, "..", "pr-finish.sh"))


@pytest.mark.parametrize("missing, named", [("preflight", ".tdd/issue-12-preflight"), ("ledger", ".tdd/issue-12.md")])
def test_4033_a_missing_input_is_exit_2_before_any_inner_call_named_on_stderr(finish, missing, named):
    code, out, err, fake = finish(missing=(missing,))

    assert (code, fake.calls) == (2, [])
    assert named in err
