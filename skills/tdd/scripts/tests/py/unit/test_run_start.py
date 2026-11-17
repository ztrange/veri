"""In-process cases for veri/run_start.py, the module run-start.sh is a shim over (PRD 027.13, #4024)."""
import importlib
import os

import pytest


class Fake:
    """A run_script stand-in: records (basename, args, cwd, env) and answers from <answers>, keyed by
    (basename, first argument or None) -> (code, stdout)."""

    def __init__(self, answers=None, porcelain=" M .gitignore\n"):
        self.answers, self.calls, self.porcelain = dict(answers or {}), [], porcelain

    def __call__(self, name, *args, cwd=None, env=None):
        base = os.path.basename(name)
        self.calls.append((base, args, cwd, env))
        for (script, first), (code, out) in self.answers.items():
            if base == script and (first is None or args[:1] == (first,)):
                return code, out, ""
        if base == "leaf-timeout.sh":
            return 0, "1800\n", ""
        if base == "capture-spec.sh":
            return 0, "# spec of 12\n", ""
        if base == "ensure-run-state-ignored.sh":
            return 0, "added\n", ""
        if base == "git" and args == ("status", "--porcelain"):
            return 0, self.porcelain, ""
        return 0, "", ""

    def names(self):
        return [c[0] for c in self.calls]


@pytest.fixture
def start(monkeypatch, run_cli, tmp_path):
    """start(ledger=False, answers=None, fake=None, preflight=True) runs run-start for issue 12 from the main tree,
    the run's worktree at .tdd/wt/12; returns (code, stdout, stderr, fake)."""
    fused = importlib.import_module("veri.fused")
    run_start = importlib.import_module("veri.run_start")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)

    def go(ledger=False, answers=None, fake=None, preflight=True, argv=("12",)):
        if preflight:
            (wt / ".tdd" / "issue-12-preflight").write_text(
                "worktree=%s\nfast_cmd=make unit\nbaseline=8\nfull=95\ntimeout=1800\nrun=fresh\n" % wt)
        if ledger:
            (wt / ".tdd" / "issue-12.md").write_text("- [ ] a step\n")
        fake = fake or Fake(answers)
        monkeypatch.setattr(fused, "run_script", fake)
        code, out, err = run_cli(run_start, list(argv), cwd=str(tmp_path))
        return code, out, err, fake

    go.wt = wt
    return go


def test_4024_no_argument_prints_the_usage_and_exits_2_with_no_inner_call(start):
    code, out, err, fake = start(argv=())

    assert (code, "run-start.sh <n>" in err, fake.calls) == (2, True, [])
    here = os.path.dirname(importlib.import_module("veri.run_start").__file__)
    assert os.path.exists(os.path.join(here, "..", "run-start.sh"))


def test_4024_a_missing_preflight_file_is_exit_2_before_any_inner_call_named_on_stderr(start):
    code, out, err, fake = start(preflight=False)

    assert (code, fake.calls) == (2, [])
    assert ".tdd/issue-12-preflight" in err
