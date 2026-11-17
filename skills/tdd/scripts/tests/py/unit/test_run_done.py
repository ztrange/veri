"""In-process cases for veri/run_done.py, the module run-done.sh is a shim over (PRD 027.12, #4034)."""
import importlib
import os

import pytest


class Fake:
    """A run_script stand-in: records (basename, args, cwd, env, kw) and answers from <answers>, keyed by
    (basename, first argument or None) -> (code, stdout). stop-requested.sh exits 3 (no request) unless answered."""

    def __init__(self, answers=None):
        self.answers, self.calls = dict(answers or {}), []

    def __call__(self, name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        self.calls.append((base, args, cwd, env, kw))
        for (script, first), (code, out) in self.answers.items():
            if base == script and (first is None or args[:1] == (first,)):
                return code, out, ""
        if base == "stop-requested.sh" and not args:
            return 3, "", ""
        return 0, "", ""

    def names(self):
        return [c[0] for c in self.calls]


@pytest.fixture
def done(monkeypatch, run_cli, tmp_path):
    """done(answers=None, fake=None, missing=(), argv=None) runs run-done for issue 12 from the main tree, the run's
    worktree at .tdd/wt/12; returns (code, stdout, stderr, fake)."""
    fused = importlib.import_module("veri.fused")
    run_done = importlib.import_module("veri.run_done")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)

    def go(answers=None, fake=None, missing=(), argv=None):
        if "preflight" not in missing:
            (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
        fake = fake or Fake(answers)
        monkeypatch.setattr(fused, "run_script", fake)
        code, out, err = run_cli(run_done, list(argv if argv is not None else ("12",)), cwd=str(tmp_path))
        return code, out, err, fake

    go.wt = wt
    return go


def test_4034_no_argument_prints_the_usage_and_exits_2_with_no_inner_call(done):
    code, out, err, fake = done(argv=())

    assert (code, "run-done.sh <n>" in err, fake.calls) == (2, True, [])
    here = os.path.dirname(importlib.import_module("veri.run_done").__file__)
    assert os.path.exists(os.path.join(here, "..", "run-done.sh"))


def test_4034_a_missing_preflight_is_exit_2_before_any_inner_call_named_on_stderr(done):
    code, out, err, fake = done(missing=("preflight",))

    assert (code, fake.calls) == (2, [])
    assert ".tdd/issue-12-preflight" in err
