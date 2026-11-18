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


def test_4343_called_again_it_resumes_at_the_seam_recorded_in_the_step_file_never_rerunning_red_half(step):
    step(answers={"green-half.sh": (1, "stopped at 2 REJECT\n")})
    recorded = (step.wt / ".tdd" / "issue-12-step").read_text()

    code, out, err, stages = step()

    assert ("stage=green-half" in recorded.splitlines(), code) == (True, 0), err
    assert stages.names() == ["green-half.sh", "refactor-half.sh", "step-close.sh"]


PENDING = "# Plan for #12\n\n- [x] %s ⟂ refactor pending\n- [ ] two ⟦criterion 2⟧\n" % STEP


def test_4343_a_refactor_pending_step_with_no_seam_record_starts_at_refactor_half_not_the_next_steps_red(step):
    code, out, err, stages = step(ledger=PENDING)

    assert code == 0, err
    assert stages.names() == ["refactor-half.sh", "step-close.sh"]


@pytest.mark.parametrize("argv, code, called", [
    (("12", "--from", "refactor-half"), 0, ["refactor-half.sh", "step-close.sh"]),
    (("12", "--from", "green-half"), 0, ["green-half.sh", "refactor-half.sh", "step-close.sh"]),
    (("12", "--from", "blue-half"), 2, []),
    (("12", "--from"), 2, []),
    (("12", "--from", "red-half", "--from", "green-half"), 2, []),
    (("12", "--sideways"), 2, []),
    (("x",), 2, []),
])
def test_4343_from_starts_at_the_named_stage_and_an_unknown_stage_or_bad_argument_is_exit_2_with_no_call(
        step, argv, code, called):
    code_, out, err, stages = step(argv=argv)

    assert (code_, stages.names()) == (code, called), err
    assert ("usage: run-step.sh <n> [--from <stage>] [--hand <stage>]…" in err) == (code == 2)


@pytest.mark.parametrize("argv, called, last", [
    (("12", "--hand", "green-half", "--hand", "step-close"), ["red-half.sh"],
     "seam=green-half code=1 reason=hand next=" + GREEN),
    (("12", "--hand", "step-close", "--from", "refactor-half", "--hand", "green-half"), ["refactor-half.sh"],
     "seam=step-close code=1 reason=hand next=" + REFACTOR),
    (("12", "--hand", "red-half"), [], "seam=red-half code=1 reason=hand next=" + RED),
])
def test_4343_hand_repeated_stops_before_each_named_stage_without_calling_it_exit_1(step, argv, called, last):
    code, out, err, stages = step(argv=argv)

    assert (code, stages.names(), out.splitlines()[-1]) == (1, called, last), err


@pytest.mark.parametrize("text", ["port: replaces 'a' in tests/py/test_x.py ⟦replaces-case⟧ ⟦criterion 1⟧",
                                  "CI's job passes again ⟦ci-repair⟧"])
def test_4343_a_step_green_half_does_not_handle_stops_before_it_unmodelled_without_calling_it(step, text):
    code, out, err, stages = step(ledger=LEDGER % text)

    assert (code, stages.names()) == (1, ["red-half.sh"]), err
    assert out.splitlines()[-1] == "seam=green-half code=1 reason=unmodelled next=" + GREEN


DIFF = "DIFF-CHECKED.md#A `⟦diff-checked⟧` step — develop-diff, then verify-diff (blind)"


@pytest.mark.parametrize("text, next_", [
    ("the prompt says so ⟦diff-checked⟧ ⟦criterion 1⟧", DIFF),
    ("lint passes ⟦lint-repair⟧ ⟦diff-checked⟧ ⟦criterion 1⟧", DIFF),
    ("a weak test is strengthened ⟦test-quality⟧ ⟦diff-checked⟧ ⟦criterion 1⟧", DIFF),
    ("`skills/tdd/SKILL.md#Red` says so ⟦skill-edit⟧ ⟦criterion 1⟧", "SKILL-EDIT.md#The skill-edit step"),
    ("repairs the fixture 'f' in tests/test_a.py ⟦fixture-repair⟧ ⟦criterion 1⟧", RED),
    ("the interface moves ⟦phases: expand, migrate⟧ ⟦criterion 1⟧",
     "SKILL.md#A `⟦phases: …⟧` step — each listed phase, a developer leaf then a blind verifier"),
])
def test_4343_a_step_that_is_not_a_cycle_step_exits_1_on_a_kind_seam_calling_no_stage(step, text, next_):
    code, out, err, stages = step(ledger=LEDGER % text)

    assert (code, stages.names(), out) == (1, [], "seam=none code=1 reason=kind next=%s\n" % next_), err
    assert not (step.wt / ".tdd" / "issue-12-step").exists()


RECORD = "seam=green-half code=1 reason=record next=seam-settle.sh 12 red-half test_path=… target_test=…"


@pytest.mark.parametrize("reason, kw, last", [
    ("hand", {"argv": ("12", "--hand", "refactor-half")}, "seam=refactor-half code=1 reason=hand next=" + REFACTOR),
    ("unmodelled", {"ledger": LEDGER % "CI passes ⟦ci-repair⟧"},
     "seam=green-half code=1 reason=unmodelled next=" + GREEN),
    ("record", {"answers": {"green-half.sh": (1, RECORD + "\n")}}, RECORD),
    ("kind", {"ledger": LEDGER % "says so ⟦skill-edit⟧"},
     "seam=none code=1 reason=kind next=SKILL-EDIT.md#The skill-edit step"),
])
def test_4343_every_designed_stop_hand_unmodelled_record_kind_exits_1_never_2(step, reason, kw, last):
    code, out, err, stages = step(**kw)

    assert (code, out.splitlines()[-1]) == (1, last), err
    assert " reason=%s " % reason in last


@pytest.mark.parametrize("answers", [{}, {"refactor-half.sh": (2, "stopped at 5 wait-leaf.sh verdict-refactor exit 2\n")}])
def test_4343_it_prints_each_stages_call_line_with_its_exit_code_and_never_a_leaf_or_suite_output_file(step, answers):
    for name in ("develop-red.out", "develop-green.out", "verify-refactor.log", "test-runs/make-unit.out"):
        (step.wt / ".tdd" / name).parent.mkdir(exist_ok=True)
        (step.wt / ".tdd" / name).write_text("MARKER-4343 leaf output\n")

    code, out, err, stages = step(answers=answers)

    assert "MARKER-4343" not in out + err
    lines = out.splitlines()
    assert [line for line in lines if line.split(" ")[0] in STAGES and " exit " in line] == ["%s 12 exit %d" % (name, (answers.get(name) or (0,))[0])
                                                           for name in stages.names()]


def headings(path):
    """The text of each heading line of <path>, after its #s, fenced blocks skipped."""
    found, fenced = set(), False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("```"):
            fenced = not fenced
        elif not fenced and line.startswith("#"):
            found.add(line.lstrip("#").strip())
    return found


def test_4343_every_next_value_run_step_can_print_is_a_script_or_an_anchor_naming_a_heading_in_its_file():
    run_step = importlib.import_module("veri.run_step")
    skill = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(run_step.__file__)), "..", ".."))
    anchors = [anchor for anchor, _ in run_step.STAGES.values()] + [run_step.KINDS[k] for k in run_step.KINDS]
    from pathlib import Path

    missing = [a for a in anchors if a.split("#", 1)[1] not in headings(Path(skill, a.split("#", 1)[0]))]

    assert (sorted(run_step.KINDS), missing) == (sorted(importlib.import_module("veri.red_half").REFUSED), [])
    assert all(os.path.isfile(os.path.join(skill, "scripts", s)) for s in run_step.NEXT_SCRIPTS)


def test_4343_its_calls_are_the_four_stage_scripts_and_never_a_leaf_launcher(step):
    run_step = importlib.import_module("veri.run_step")
    _, _, _, stages = step()

    assert run_step.CALLS == STAGES == tuple(stages.names())
    assert not {"run-leaf.sh", "detach-leaf.sh", "supervise.sh"} & set(run_step.CALLS)


def test_4343_a_step_close_exit_0_with_no_next_line_is_exit_2_named_on_stderr(step):
    code, out, err, stages = step(answers={"step-close.sh": (0, "owed_pin=none\n")})

    assert (code, err) == (2, "run-step.sh: step-close.sh exited 0 with no next= line\n")
    assert "stage=step-close" in (step.wt / ".tdd" / "issue-12-step").read_text().splitlines()


def test_4343_a_ledger_with_no_open_or_refactor_pending_step_exits_3_with_no_call(step):
    code, out, err, stages = step(ledger="# Plan for #12\n\n- [x] zero ⟦criterion 1⟧\n")

    assert (code, stages.names(), out) == (3, [], "")
    assert err == "run-step.sh: no open step in .tdd/issue-12.md\n"


def test_4343_a_clean_run_from_a_seam_removes_the_seam_record(step):
    (step.wt / ".tdd" / "issue-12-step").write_text("stage=green-half\nstep=%s\n" % STEP)

    code, out, err, stages = step()

    assert (code, stages.names()[0]) == (0, "green-half.sh"), err
    assert not (step.wt / ".tdd" / "issue-12-step").exists()


def test_4343_a_missing_preflight_file_is_exit_2_before_any_call(step, tmp_path):
    (tmp_path / ".tdd" / "issue-12-preflight").unlink()

    code, out, err, stages = step()

    assert (code, stages.names()) == (2, [])
    assert ".tdd/issue-12-preflight" in err


def test_4343_a_seam_record_naming_another_step_is_not_resumed(step):
    (step.wt / ".tdd" / "issue-12-step").write_text("stage=step-close\nstep=zero ⟦criterion 1⟧\n")

    code, out, err, stages = step()

    assert (code, stages.names()) == (0, list(STAGES)), err


@pytest.mark.parametrize("raw", [127, -9, 4])
def test_4343_a_stage_exit_outside_0_to_3_is_exit_2_naming_the_stage_and_its_code_on_stderr(step, raw):
    code, out, err, stages = step(answers={"green-half.sh": (raw, "")})

    assert stages.names() == ["red-half.sh", "green-half.sh"]
    assert (code, err) == (2, "run-step.sh: green-half.sh exited %d\n" % raw)
    assert out.splitlines()[-1] == "seam=green-half code=2 next=%s" % GREEN
    assert "stage=green-half" in (step.wt / ".tdd" / "issue-12-step").read_text().splitlines()
