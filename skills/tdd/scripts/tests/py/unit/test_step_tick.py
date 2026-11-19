"""In-process cases for veri/step_tick.py, the module step-tick.sh is a shim over (PRD 038.3, #4435)."""
import importlib
import os

import pytest

STEP = "the prompt says so ⟦diff-checked⟧ ⟦criterion 1⟧"
LEDGER = "# Plan for #12\n\n- [x] zero ⟦criterion 1⟧\n- [ ] %s\n- [ ] two ⟦criterion 2⟧\n"
BODY = "## Acceptance criteria\n\n- [ ] the prompt says so\n- [ ] two\n"
LEDGER_ROWS = "1\tdone\tstep\tzero\n2\tdone\tstep\tthe prompt says so\n3\topen\tstep\ttwo\n"


class Fake:
    """A run_script stand-in: records (basename, args, cwd, env, kw) and answers from <answers>, keyed by
    (basename, first argument or None) -> (code, stdout)."""

    def __init__(self, answers=None):
        self.answers, self.calls = dict(answers or {}), []

    def __call__(self, name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        self.calls.append((base, args, cwd, env, kw))
        for (script, first), (code, out) in self.answers.items():
            if base == script and (first is None or args[:1] == (first,)):
                return code, out, ""
        if base == "ledger-steps.sh" and args[:1] == ("last-done",):
            return 0, STEP + "\n", ""
        if base == "ledger-steps.sh" and args[:1] == ("criterion",):
            return 0, "the prompt says so\n", ""
        if base == "ledger-steps.sh":
            return 0, LEDGER_ROWS, ""
        if base == "gh":
            return 0, BODY, ""
        if base == "stop-requested.sh":
            return 3, "", ""
        return 0, "", ""

    def names(self):
        return [c[0] for c in self.calls]

    def call(self, base, first=None):
        return next(c for c in self.calls if c[0] == base and (first is None or c[1][:1] == (first,)))


@pytest.fixture
def tick(monkeypatch, run_cli, tmp_path):
    """tick(answers=None, missing=(), argv=None, ledger=None) runs step-tick for issue 12 from the main tree, the run's
    worktree at .tdd/wt/12; returns (code, stdout, stderr, fake)."""
    fused = importlib.import_module("veri.fused")
    step_tick = importlib.import_module("veri.step_tick")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)

    def go(answers=None, missing=(), argv=None, ledger=None):
        files = {"preflight": (wt / ".tdd" / "issue-12-preflight", "worktree=%s\nfast_cmd=make unit\n" % wt),
                 "ledger": (wt / ".tdd" / "issue-12.md", ledger or LEDGER % STEP),
                 "receipt": (wt / ".tdd" / "pin-recheck-ok", "e" * 40 + "\n")}
        for key, (path, text) in files.items():
            if key not in missing and not path.exists():
                path.write_text(text)
        fake = Fake(answers)
        monkeypatch.setattr(fused, "run_script", fake)
        code, out, err = run_cli(step_tick, list(argv if argv is not None else ("12",)), cwd=str(tmp_path))
        return code, out, err, fake

    go.wt = wt
    return go


def test_4435_it_ticks_commits_under_the_diff_checked_subject_pushes_asks_the_stop_mirrors_and_ends_on_next(tick):
    """DST6: the close of a non-cycle step, in order, its last line the next stop."""
    code, out, err, fake = tick()

    assert code == 0, err
    assert [(c[0], c[1]) for c in fake.calls[:5]] == [
        ("tick-ledger.sh", (".tdd/issue-12.md", STEP)),
        ("git", ("add", "-A")),
        ("git", ("commit", "-m", "chore: diff-checked — the prompt says so (#12)")),
        ("push-branch.sh", ()),
        ("stop-requested.sh", ())]
    names = fake.names()
    assert names.index("comment.sh") < names.index("criterion-finished.sh") < names.index("tick-issue-criterion.sh")
    assert fake.call("comment.sh")[1] == ("12", "step-done")
    assert fake.call("tick-issue-criterion.sh")[1] == ("12", "the prompt says so")
    mark = fake.call("event.sh")
    assert (mark[1], mark[3]["VERI_STEP"]) == (("step-done",), STEP)
    assert names.index("tick-issue-criterion.sh") < names.index("event.sh") < names.index("next-unchecked.sh")
    assert out.splitlines()[-1] == "next=cycle"
