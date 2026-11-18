"""In-process cases for veri/stop_settle.py, the module stop-settle.sh is a shim over (PRD 038.5, #4388)."""
import importlib
import os

import pytest

LEDGER = "# Plan for #12\n\n- [ ] one ⟦criterion 1⟧\n"


class Fake:
    """A run_script stand-in: records (basename, args, cwd, env, kw) and answers from <answers>, keyed by
    (basename, first argument or None) -> (code, stdout, stderr)."""

    def __init__(self, answers=None, porcelain="", ledger=LEDGER):
        self.answers, self.calls, self.porcelain, self.ledger = dict(answers or {}), [], porcelain, ledger

    def __call__(self, name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        self.calls.append((base, args, cwd, env, kw))
        for (script, first), answer in self.answers.items():
            if base == script and (first is None or args[:1] == (first,)):
                return answer
        if base == "git" and args[:1] == ("status",):
            return 0, self.porcelain, ""
        if base == "git" and args[:2] == ("rev-parse", "--git-path"):
            return 0, ".git/" + args[2] + "\n", ""
        if base == "git" and args[:2] == ("rev-parse", "-q"):
            return 1, "", ""
        if base == "git" and args[:1] == ("show",):
            return (0, self.ledger, "") if self.ledger is not None else (128, "", "fatal: no such path\n")
        return 0, "", ""

    def names(self):
        return [c[0] for c in self.calls]

    def call(self, base, first=None):
        return next(c for c in self.calls if c[0] == base and (first is None or c[1][:1] == (first,)))


@pytest.fixture
def stop(monkeypatch, run_cli, tmp_path):
    """stop(answers=None, fake=None, argv=None, preflight=True) runs stop-settle for issue 12 from the main tree, the
    run's worktree at .tdd/wt/12; returns (code, stdout, stderr, fake)."""
    fused = importlib.import_module("veri.fused")
    stop_settle = importlib.import_module("veri.stop_settle")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)

    def go(answers=None, fake=None, argv=None, preflight=True):
        if preflight:
            (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
        fake = fake or Fake(answers)
        monkeypatch.setattr(fused, "run_script", fake)
        code, out, err = run_cli(stop_settle, list(argv if argv is not None else ("12", "at-ledger")),
                                 cwd=str(tmp_path))
        return code, out, err, fake

    go.wt = wt
    return go


@pytest.mark.parametrize("argv", [(), ("12",), ("x", "now"), ("12", "later"), ("12", "now", "--force"),
                                  ("12", "now", "--drop", "--drop")])
def test_4388_bad_arguments_print_the_usage_and_exit_2_with_no_call(stop, argv):
    code, out, err, fake = stop(argv=argv)

    assert (code, "stop-settle.sh <n> <mode> [--drop]" in err, fake.calls) == (2, True, [])
    here = os.path.dirname(importlib.import_module("veri.stop_settle").__file__)
    assert os.path.exists(os.path.join(here, "..", "stop-settle.sh"))


def test_4388_a_missing_preflight_file_is_exit_2_before_any_call_named_on_stderr(stop):
    code, out, err, fake = stop(preflight=False)

    assert (code, fake.calls) == (2, [])
    assert ".tdd/issue-12-preflight" in err
