"""In-process cases for veri/step_close.py, the module step-close.sh is a shim over (PRD 027.8, #4029)."""
import importlib
import os

import pytest

STEP = "one thing works ⟦criterion 1⟧"
LEDGER = "# Plan for #12\n\n- [x] %s ⟂ refactor pending\n- [ ] two ⟦criterion 2⟧\n"
GREEN_SHA = "d" * 40
BASE_SHA = "c" * 40
REFACTOR_HALF = ("step=%s\ngreen_sha=" + GREEN_SHA + "\ncount=1\nbudget=5\nstopped=nothing-left\n"
                 "touched=src/a.py,tests/test_a.py\n")
BODY = "## Acceptance criteria\n\n- [ ] one thing works\n- [ ] two\n"
LEDGER_ROWS = "1\tdone\tstep\tone thing works\n2\topen\tstep\ttwo\n3\topen\tfull-suite\tfull\n"


class Fake:
    """A run_script stand-in: records (basename, args, cwd, env, kw) and answers from <answers>, keyed by
    (basename, first argument or None) -> (code, stdout)."""

    def __init__(self, answers=None, porcelain="", pins=""):
        self.answers, self.calls, self.porcelain, self.pins = dict(answers or {}), [], porcelain, pins

    def __call__(self, name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        self.calls.append((base, args, cwd, env, kw))
        for (script, first), (code, out) in self.answers.items():
            if base == script and (first is None or args[:1] == (first,)):
                return code, out, ""
        if base == "git" and args[:1] == ("rev-parse",):
            return 0, BASE_SHA + "\n", ""
        if base == "git" and args == ("status", "--porcelain"):
            return 0, self.porcelain, ""
        if base == "pin-recheck.sh":
            return 0, self.pins, ""
        if base == "ledger-steps.sh" and args[:1] == ("last-done",):
            return 0, STEP + "\n", ""
        if base == "ledger-steps.sh" and args[:1] == ("criterion",):
            return 0, "one thing works\n", ""
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
def close(monkeypatch, run_cli, tmp_path):
    """close(answers=None, fake=None, missing=(), step=STEP, half=None, argv=None) runs step-close for issue 12 from
    the main tree, the run's worktree at .tdd/wt/12; returns (code, stdout, stderr, fake)."""
    fused = importlib.import_module("veri.fused")
    step_close = importlib.import_module("veri.step_close")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)

    def go(answers=None, fake=None, missing=(), step=STEP, half=None, argv=None, ledger=None):
        files = {"preflight": (wt / ".tdd" / "issue-12-preflight", "worktree=%s\nfast_cmd=make unit\n" % wt),
                 "ledger": (wt / ".tdd" / "issue-12.md", ledger or LEDGER % step),
                 "refactor-half": (wt / ".tdd" / "issue-12-refactor-half", half or REFACTOR_HALF % step),
                 "stage": (wt / ".tdd" / "stage-rl.t", "100\n")}
        for key, (path, text) in files.items():
            if key not in missing and not path.exists():
                path.write_text(text)
        fake = fake or Fake(answers)
        monkeypatch.setattr(fused, "run_script", fake)
        code, out, err = run_cli(step_close, list(argv if argv is not None else ("12",)), cwd=str(tmp_path))
        return code, out, err, fake

    go.wt = wt
    return go


def test_4029_no_argument_prints_the_usage_and_exits_2_with_no_inner_call(close):
    code, out, err, fake = close(argv=())

    assert (code, "step-close.sh <n>" in err, fake.calls) == (2, True, [])
    here = os.path.dirname(importlib.import_module("veri.step_close").__file__)
    assert os.path.exists(os.path.join(here, "..", "step-close.sh"))


@pytest.mark.parametrize("missing, named", [("preflight", ".tdd/issue-12-preflight"), ("ledger", ".tdd/issue-12.md"),
                                            ("refactor-half", ".tdd/issue-12-refactor-half")])
def test_4029_a_missing_input_is_exit_2_before_any_inner_call_named_on_stderr(close, missing, named):
    code, out, err, fake = close(missing=(missing,))

    assert (code, fake.calls) == (2, [])
    assert named in err


def test_4029_a_refactor_half_file_naming_another_step_is_exit_2_before_any_inner_call(close):
    code, out, err, fake = close(half=REFACTOR_HALF % "zero ⟦criterion 1⟧")

    assert (code, fake.calls) == (2, [])
    assert "another step" in err


def test_4029_no_refactor_pending_step_is_exit_2_before_any_inner_call(close):
    code, out, err, fake = close(ledger="# Plan\n\n- [x] %s\n- [ ] two ⟦criterion 2⟧\n" % STEP)

    assert (code, fake.calls) == (2, [])


def test_4029_an_uncovered_spec_line_stops_it_with_exit_1_before_any_inner_call(close):
    code, out, err, fake = close(half=REFACTOR_HALF % STEP + "uncovered_spec=empty input returns 0\n")

    assert (code, fake.calls) == (1, [])
    assert out.splitlines()[-1] == "stopped at 6 uncovered_spec=empty input returns 0"
