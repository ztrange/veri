"""In-process cases for veri/run_step.py, the module run-step.sh is a shim over (PRD 038.2, #4343): each stage is
spied on in-process through fused.run_script, so no stage script runs."""
import importlib
import os

import pytest

STEP = "one thing works ⟦criterion 1⟧"
LEDGER = "# Plan for #12\n\n- [x] zero ⟦criterion 1⟧\n- [ ] %s\n- [ ] two ⟦criterion 2⟧\n"
STAGES = ("red-half.sh", "green-half.sh", "refactor-half.sh", "step-close.sh")


class Stages:
    """A run_script stand-in for the four stages: records (basename, args, cwd) and answers from <answers>, keyed by
    basename -> (code, stdout); a stage not named answers 0 with a line of its own, step-close a `next=` line."""

    def __init__(self, answers=None):
        self.answers, self.calls = dict(answers or {}), []

    def __call__(self, name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        self.calls.append((base, args, cwd, name))
        if base in self.answers:
            code, out = self.answers[base]
            return code, out, ""
        if base == "step-close.sh":
            return 0, "next=cycle\nowed_pin=none\n", ""
        return 0, "%s settled\n" % base, ""

    def names(self):
        return [c[0] for c in self.calls]


@pytest.fixture
def step(monkeypatch, run_cli, tmp_path):
    """step(answers=None, argv=None, ledger=LEDGER % STEP, stages=None) runs run-step for issue 12 from the main tree,
    the run's worktree at .tdd/wt/12; returns (code, stdout, stderr, stages)."""
    fused = importlib.import_module("veri.fused")
    run_step = importlib.import_module("veri.run_step")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)

    def go(answers=None, argv=None, ledger=LEDGER % STEP, stages=None):
        (wt / ".tdd" / "issue-12.md").write_text(ledger)
        stages = stages or Stages(answers)
        monkeypatch.setattr(fused, "run_script", stages)
        code, out, err = run_cli(run_step, list(argv if argv is not None else ("12",)), cwd=str(tmp_path))
        return code, out, err, stages

    go.wt = wt
    return go


def test_4343_a_cycle_step_runs_the_four_stages_in_order_and_ends_on_step_closes_next_line(step):
    code, out, err, stages = step()

    assert code == 0, err
    assert stages.names() == list(STAGES)
    scripts = os.path.dirname(os.path.realpath(importlib.import_module("veri.fused").__file__))
    assert [os.path.dirname(c[3]) for c in stages.calls] == [os.path.normpath(os.path.join(scripts, ".."))] * 4
    assert [c[1] for c in stages.calls] == [("12",)] * 4
    assert out.splitlines()[-1] == "next=cycle"


RED = "SKILL.md#Red — one failing test (developer leaf), then verify-red (blind)"
GREEN = "SKILL.md#Green — minimum implementation (developer leaf), then verify-green (blind)"
REFACTOR = "SKILL.md#Refactor loop — one leaf applies the step's transforms, then verify-refactor (blind, once)"


@pytest.mark.parametrize("code, next_", [(1, GREEN), (2, GREEN), (3, "run-step.sh 12")])
def test_4343_the_first_stage_exiting_nonzero_stops_it_on_a_seam_line_with_that_code(step, code, next_):
    code_, out, err, stages = step(answers={"green-half.sh": (code, "stopped at 2 something\n")})

    assert stages.names() == ["red-half.sh", "green-half.sh"]
    assert out.splitlines()[-1] == "seam=green-half code=%d next=%s" % (code, next_)
    assert code_ == code
