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


def test_4510_a_planned_diff_checked_step_right_after_the_refactor_pending_step_leaves_it_to_refactor_half(step):
    """A ⟦diff-checked⟧ step of the plan waits for the refactor-pending step's close."""
    ledger = "# Plan for #12\n\n- [x] %s ⟂ refactor pending\n- [ ] the prompt says so ⟦diff-checked⟧ ⟦criterion 2⟧\n" % STEP

    code, out, err, stages = step(ledger=ledger)

    assert (code, stages.names()) == (0, ["refactor-half.sh", "step-close.sh"]), err


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
    ("repairs the fixture 'f' in tests/test_a.py ⟦fixture-repair⟧ ⟦criterion 1⟧", RED),
    ("the interface moves ⟦phases: expand, migrate⟧ ⟦criterion 1⟧",
     "SKILL.md#A `⟦phases: …⟧` step — each listed phase, a developer leaf then a blind verifier"),
])
def test_4343_a_step_that_is_not_a_cycle_step_exits_1_on_a_kind_seam_calling_no_stage(step, text, next_):
    code, out, err, stages = step(ledger=LEDGER % text)

    assert (code, stages.names(), out) == (1, [], "seam=none code=1 reason=kind next=%s\n" % next_), err
    assert not (step.wt / ".tdd" / "issue-12-step").exists()


def test_4621_a_special_kind_step_under_a_refactor_spec_keeps_its_own_kind_route_not_the_refactor_kind_seam(step):
    text = "repairs the fixture 'f' in tests/test_a.py ⟦fixture-repair⟧ ⟦criterion 1⟧"
    (step.wt / ".tdd" / "issue-12-spec.md").write_text("## Refactor\n\nExtract Function loadPlanInputs.\n")

    code, out, err, stages = step(ledger=LEDGER % text)

    assert (code, stages.names(), out) == (1, [], "seam=none code=1 reason=kind next=%s\n" % RED), err


def test_4621_an_ordinary_open_step_under_a_refactor_spec_calls_no_stage_and_stops_on_the_refactor_kind_seam(step):
    (step.wt / ".tdd" / "issue-12-spec.md").write_text("Split runPlan.\n\n## Refactor\n\nRun kind: refactor.\n")

    code, out, err, stages = step()

    assert (code, stages.names(), out) == (1, [], "seam=none code=1 reason=kind next=REFACTOR-KIND.md\n"), err


def test_4621_a_spec_heading_that_only_starts_with_refactor_is_no_refactor_section_so_the_cycle_still_runs(step):
    (step.wt / ".tdd" / "issue-12-spec.md").write_text("Fix the parser.\n\n## Refactoring notes\n\nNone.\n\n### Refactor\n\nNone.\n")

    code, out, err, stages = step()

    assert (code, stages.names()) == (0, list(STAGES)), out + err


def test_4621_a_spec_with_no_refactor_section_still_runs_red_half_first(step):
    (step.wt / ".tdd" / "issue-12-spec.md").write_text("Fix the parser.\n\n## Bug\n\n- What happened\n")

    code, out, err, stages = step()

    assert (code, stages.names()[:1]) == (0, ["red-half.sh"]), out + err


RECORD ="seam=green-half code=1 reason=record next=seam-settle.sh 12 red-half test_path=… target_test=…"


@pytest.mark.parametrize("reason, kw, last", [
    ("hand", {"argv": ("12", "--hand", "refactor-half")}, "seam=refactor-half code=1 reason=hand next=" + REFACTOR),
    ("unmodelled", {"ledger": LEDGER % "CI passes ⟦ci-repair⟧"},
     "seam=green-half code=1 reason=unmodelled next=" + GREEN),
    ("record", {"answers": {"green-half.sh": (1, RECORD + "\n")}}, RECORD),
    ("kind", {"ledger": LEDGER % "repairs the fixture 'f' in tests/test_a.py ⟦fixture-repair⟧"},
     "seam=none code=1 reason=kind next=" + RED),
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
    anchors = [anchor for anchor, _ in run_step.STAGES.values()] + [run_step.KINDS[k][0] for k in run_step.KINDS]
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


REVISE = "REVISE.md#Revising on a REJECT"
REJECTED = '{"conductor": null, "at": "verdict-green", "values": {}, "step": "%s"}' % STEP


@pytest.mark.parametrize("revised, names, last", [
    (0, ["red-half.sh", "green-half.sh", "reroute.sh", "revise.sh", "green-half.sh", "refactor-half.sh",
         "step-close.sh"], "next=cycle"),
    (1, ["red-half.sh", "green-half.sh", "reroute.sh", "revise.sh"], "seam=revise code=1 next=" + REVISE),
    (2, ["red-half.sh", "green-half.sh", "reroute.sh", "revise.sh"], "seam=revise code=2 next=" + REVISE)])
def test_a_half_stopped_by_a_verdict_reject_calls_revise_then_the_stage_again_on_its_0_4433(step, revised, names, last):
    """PRD 038.9 criterion 9: `.tdd/verdict-<phase>.exit` holding 1 is a REJECT revise.sh takes; on green, after
    reroute.sh answers `route=revise phase=green` (PRD 038.10 RRT8)."""
    (step.wt / ".tdd" / "verdict-green.exit").write_text("1\n")

    class Rejected(Stages):
        def __call__(self, name, *args, **kw):
            code, out, err = super().__call__(name, *args, **kw)
            if os.path.basename(name) == "green-half.sh" and self.names().count("green-half.sh") == 1:
                return 1, "stopped at 2 wait-leaf.sh verdict-green exit 1\n", ""
            return code, out, err

    code, out, err, stages = step(stages=Rejected({"revise.sh": (revised, ""),
                                                   "reroute.sh": (1, "route=revise phase=green\n")}))

    assert (code, stages.names(), out.splitlines()[-1]) == (revised, names, last)
    assert stages.calls[3][1] == ("12", "green")


def test_a_half_stopping_with_1_without_a_verdict_reject_calls_no_revise_4433(step):
    (step.wt / ".tdd" / "verdict-green.exit").write_text("0\n")
    code, out, err, stages = step(answers={"green-half.sh": (1, "stopped at 1 tree-check\n")})

    assert (code, stages.names()) == (1, ["red-half.sh", "green-half.sh"])
    assert out.splitlines()[-1] == "seam=green-half code=1 next=" + GREEN


def test_a_revise_exit_3_is_called_again_through_run_step_which_resumes_at_revise_while_the_rejected_record_stands_4433(
        step):
    """revise.sh is sliced: its 3 means call again, and run-step.sh called again goes back to it, not to the half
    (whose wait record fused.wait moved to `<stage>-rejected`)."""
    (step.wt / ".tdd" / "verdict-green.exit").write_text("1\n")
    (step.wt / ".tdd" / "issue-12-green-half-rejected-wait").write_text(REJECTED)
    first = step(answers={"green-half.sh": (1, "stopped at 2 wait-leaf.sh verdict-green exit 1\n"),
                          "revise.sh": (3, "waiting on revise-green-1\n")})
    (step.wt / ".tdd" / "issue-12-green-half-rejected-wait").write_text(REJECTED)
    code, out, err, stages = step(answers={"revise.sh": (3, "waiting on verdict-green\n")})

    assert (first[0], first[1].splitlines()[-1]) == (3, "seam=revise code=3 next=run-step.sh 12")
    assert (code, stages.names(), out.splitlines()[-1]) == (3, ["revise.sh"], "seam=revise code=3 next=run-step.sh 12")


def test_hand_revise_stops_at_the_reject_never_calling_revise_and_revise_is_a_stage_outside_the_series_4433(step):
    """PRD 038.9 criterion 10: `--hand revise` leaves the REJECT to REVISE.md's prose; `--from revise` is no start."""
    run_step = importlib.import_module("veri.run_step")
    (step.wt / ".tdd" / "verdict-green.exit").write_text("1\n")
    code, out, err, stages = step(answers={"green-half.sh": (1, "stopped at 2 wait-leaf.sh verdict-green exit 1\n"),
                                           "reroute.sh": (1, "route=revise phase=green\n")},
                                  argv=("12", "--hand", "revise"))

    assert (code, stages.names(), out.splitlines()[-1]) == (
        1, ["red-half.sh", "green-half.sh", "reroute.sh"], "seam=revise code=1 reason=hand next=" + REVISE)
    assert ("revise" in run_step.STAGES, run_step.CALLS) == (True, STAGES)
    assert step(argv=("12", "--from", "revise"))[0] == 2


def test_a_rejected_record_naming_another_step_sends_no_call_to_revise_and_is_dropped_4433(step):
    """Records are caches (S1): a `<stage>-rejected` record a revise that stopped left behind names its step, so on a
    later step the half runs, not revise.sh, and the stale record is removed."""
    stale = step.wt / ".tdd" / "issue-12-green-half-rejected-wait"
    stale.write_text('{"conductor": null, "at": "verdict-green", "values": {}, "step": "%s"}' % STEP)
    ledger = "# Plan for #12\n\n- [x] zero ⟦criterion 1⟧\n- [x] %s\n- [ ] two ⟦criterion 2⟧\n" % STEP

    code, out, err, stages = step(ledger=ledger)

    assert (code, stages.names()) == (0, list(STAGES)), err
    assert not stale.exists()


@pytest.mark.parametrize("text", ['{"conductor": null, "at": "verdict-green", "values": {}}', '{"conductor": nu'])
def test_a_rejected_record_naming_no_step_or_unreadable_sends_no_call_to_revise_and_is_dropped_4433(step, text):
    """Records are caches (S1): a record with no `step` (an older one) or one that is not JSON names no open step, so
    the half runs and the record is removed, with no traceback."""
    stale = step.wt / ".tdd" / "issue-12-green-half-rejected-wait"
    stale.write_text(text)

    code, out, err, stages = step()

    assert (code, stages.names(), err) == (0, list(STAGES), "")
    assert not stale.exists()


DIFF_STEPS = ["the prompt says so ⟦diff-checked⟧ ⟦criterion 1⟧",
              "lint passes ⟦lint-repair⟧ ⟦diff-checked⟧ ⟦criterion 1⟧",
              "a weak test is strengthened ⟦test-quality⟧ ⟦diff-checked⟧ ⟦criterion 1⟧"]


@pytest.mark.parametrize("text", DIFF_STEPS)
def test_4435_a_diff_checked_step_runs_diff_step_as_its_one_stage_and_ends_on_its_next_line(step, text):
    """DST8: in place of `seam=none … reason=kind`."""
    code, out, err, stages = step(ledger=LEDGER % text, answers={"diff-step.sh": (0, "step-tick.sh 12 exit 0\nnext=cycle\n")})

    assert (code, stages.names(), out.splitlines()[-1]) == (0, ["diff-step.sh"], "next=cycle"), err
    assert stages.calls[0][1] == ("12",)
    scripts = os.path.dirname(os.path.dirname(os.path.realpath(importlib.import_module("veri.fused").__file__)))
    assert stages.calls[0][3] == os.path.join(scripts, "diff-step.sh")


def test_4435_hand_diff_step_stops_before_it_on_the_diff_checked_anchor(step):
    """DST8: `--hand diff-step` keeps the prose path, its next= the anchor KINDS names for ⟦diff-checked⟧."""
    code, out, err, stages = step(ledger=LEDGER % DIFF_STEPS[0], argv=("12", "--hand", "diff-step"))

    assert (code, stages.names(), out.splitlines()[-1]) == (1, [], "seam=diff-step code=1 reason=hand next=" + DIFF)


@pytest.mark.parametrize("code_, last", [(3, "seam=diff-step code=3 next=run-step.sh 12"),
                                         (2, "seam=diff-step code=2 next=" + DIFF)])
def test_4435_a_diff_step_exit_other_than_0_ends_on_its_seam(step, code_, last):
    code, out, err, stages = step(ledger=LEDGER % DIFF_STEPS[0], answers={"diff-step.sh": (code_, "")})

    assert (code, out.splitlines()[-1]) == (code_, last)


def test_4435_a_diff_step_reject_calls_revise_with_phase_diff_then_diff_step_again(step):
    """DST7: the rejected record diff-step leaves sends its exit 1 to revise.sh <n> diff."""
    import json
    record = step.wt / ".tdd" / "issue-12-diff-step-rejected-wait"

    class Rejecting(Stages):
        def __call__(self, name, *args, **kw):
            if os.path.basename(name) == "diff-step.sh" and "diff-step.sh" not in self.names():
                self.calls.append(("diff-step.sh", args, None, name))
                record.write_text(json.dumps({"conductor": None, "at": "verdict-diff", "values": {},
                                              "step": DIFF_STEPS[0]}))
                return 1, "stopped at verify wait-leaf.sh verdict-diff exit 1\n", ""
            if os.path.basename(name) == "revise.sh":
                record.unlink()
            return super().__call__(name, *args, **kw)

    code, out, err, stages = step(ledger=LEDGER % DIFF_STEPS[0], stages=Rejecting(
        {"diff-step.sh": (0, "next=cycle\n")}))

    assert (code, [(c[0], c[1]) for c in stages.calls]) == (0, [("diff-step.sh", ("12",)), ("revise.sh", ("12", "diff")),
                                                                ("diff-step.sh", ("12",))]), err


def test_4435_from_a_cycle_stage_on_a_diff_checked_step_is_exit_2_calling_nothing(step):
    code, out, err, stages = step(ledger=LEDGER % DIFF_STEPS[0], argv=("12", "--from", "green-half"))

    assert (code, stages.names(), err) == (2, [], "run-step.sh: --from green-half: not a stage of this step\n")


@pytest.mark.parametrize("text, code_, names", [(DIFF_STEPS[0], 0, ["diff-step.sh"]), (STEP, 2, [])])
def test_4435_from_diff_step_runs_it_on_a_diff_checked_step_and_is_exit_2_on_a_cycle_step(step, text, code_, names):
    code, out, err, stages = step(ledger=LEDGER % text, argv=("12", "--from", "diff-step"),
                                  answers={"diff-step.sh": (0, "next=cycle\n")})

    assert (code, stages.names()) == (code_, names), err


class Sequenced(Stages):
    """Stages whose <script> answers come from a list, one per call, the last repeated; others as Stages."""

    def __init__(self, answers=None, sequence=None):
        super().__init__(answers)
        self.sequence = {k: list(v) for k, v in (sequence or {}).items()}

    def __call__(self, name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        if base in self.sequence:
            self.calls.append((base, args, cwd, name))
            got = self.sequence[base]
            code, out = got.pop(0) if len(got) > 1 else got[0]
            return code, out, ""
        return super().__call__(name, *args, cwd=cwd, env=env, **kw)


@pytest.mark.parametrize("line", ["stopped at 1 WRONG_TEST: the case asserts the old rule",
                                  "stopped at 1 SUPERSEDED: tests/test_c.py::test_x"])
def test_a_green_half_stop_on_a_wrong_test_or_superseded_line_calls_reroute_on_the_green_report_then_green_half_4434(
        step, line):
    """PRD 038.10 RRT8: two of green_half.ROUTES; after reroute's 0, green-half relaunches develop-green."""
    stages = Sequenced(sequence={"green-half.sh": [(1, line + "\n"), (0, "green-half settled\n")]})
    code, out, err, stages = step(stages=stages)

    assert (code, out.splitlines()[-1]) == (0, "next=cycle"), err
    assert stages.names() == ["red-half.sh", "green-half.sh", "reroute.sh", "green-half.sh", "refactor-half.sh",
                              "step-close.sh"]
    assert stages.calls[2][1] == ("12", ".tdd/develop-green.out")


@pytest.mark.parametrize("line", ["stopped at 1 SPLIT: two steps", "stopped at 1 TIDY_FIRST: a seam first"])
def test_a_green_half_stop_on_split_or_tidy_first_keeps_its_existing_seam_with_no_reroute_4434(step, line):
    code, out, err, stages = step(answers={"green-half.sh": (1, line + "\n")})

    assert (code, stages.names(), out.splitlines()[-1]) == (
        1, ["red-half.sh", "green-half.sh"], "seam=green-half code=1 next=" + GREEN)


REJECTED_GREEN = ("stopped at 2 wait-leaf.sh verdict-green exit 1\n")


def test_a_verify_green_reject_goes_to_reroute_on_its_reason_first_and_on_its_0_green_half_runs_afresh_4434(step):
    """PRD 038.10 RRT8, PRD 038.9 RVS9 ("on green, 038.10's reroute goes first"): the answered REJECT's exit file
    and green-half's rejected record are cleared, so the relaunched green is not taken for a second REJECT."""
    (step.wt / ".tdd" / "verdict-green.exit").write_text("1\n")
    rejected = step.wt / ".tdd" / "issue-12-green-half-rejected-wait"
    stages = Sequenced(sequence={"green-half.sh": [(1, REJECTED_GREEN), (0, "green-half settled\n")]})

    class Answered(Sequenced):
        def __call__(self, name, *args, **kw):
            if os.path.basename(name) == "green-half.sh" and not self.names().count("green-half.sh"):
                rejected.write_text(REJECTED)
            return super().__call__(name, *args, **kw)

    stages.__class__ = Answered
    code, out, err, stages = step(stages=stages)

    assert (code, out.splitlines()[-1]) == (0, "next=cycle"), err
    assert stages.names() == ["red-half.sh", "green-half.sh", "reroute.sh", "green-half.sh", "refactor-half.sh",
                              "step-close.sh"]
    assert stages.calls[2][1] == ("12", ".tdd/verify-green.reason")
    assert not (step.wt / ".tdd" / "verdict-green.exit").exists() and not rejected.exists()


def test_a_reroutes_route_revise_green_calls_revise_green_then_green_half_again_4434(step):
    """PRD 038.10 RRT5: `route=revise phase=green` is exit 1, never 3, and the runner calls revise.sh <n> green."""
    (step.wt / ".tdd" / "verdict-green.exit").write_text("1\n")
    stages = Sequenced({"reroute.sh": (1, "route=revise phase=green\n"), "revise.sh": (0, "")},
                       sequence={"green-half.sh": [(1, REJECTED_GREEN), (0, "green-half settled\n")]})
    code, out, err, stages = step(stages=stages)

    assert (code, out.splitlines()[-1]) == (0, "next=cycle"), err
    assert stages.names() == ["red-half.sh", "green-half.sh", "reroute.sh", "revise.sh", "green-half.sh",
                              "refactor-half.sh", "step-close.sh"]
    assert stages.calls[3][1] == ("12", "green")


@pytest.mark.parametrize("code", [1, 2, 3])
def test_any_other_reroute_exit_is_its_seam_recorded_at_green_half_4434(step, code):
    """PRD 038.10 RRT4, RRT6: a stop naming an answer (1), no answer (2), a wait (3, call again)."""
    (step.wt / ".tdd" / "verdict-green.exit").write_text("1\n")
    code_, out, err, stages = step(answers={"green-half.sh": (1, REJECTED_GREEN),
                                            "reroute.sh": (code, "stopped at route later two\n")})

    assert (code_, stages.names()) == (code, ["red-half.sh", "green-half.sh", "reroute.sh"])
    assert out.splitlines()[-1] == "seam=reroute code=%d next=%s" % (code, "run-step.sh 12" if code == 3 else GREEN)
    assert "stage=green-half" in (step.wt / ".tdd" / "issue-12-step").read_text().splitlines()


@pytest.mark.parametrize("line", ["stopped at 3 WRONG_TEST: still the old rule", "stopped at 3 SUPERSEDED: t::x"])
def test_a_revise_green_stop_on_a_revise_green_route_calls_reroute_on_that_attempts_report_4434(step, line):
    """PRD 038.10 RRT8, PRD 038.9 RVS7: the report is `.tdd/revise-green-<k>.out`, k the step's green revise marks."""
    import json
    (step.wt / ".tdd" / "verdict-green.exit").write_text("1\n")
    marks = [{"event": "revise", "actor": "conductor", "step": STEP, "phase": "green", "attempt": str(k),
              "budget": "2"} for k in (1, 2)]
    other = {"event": "revise", "actor": "conductor", "step": STEP, "phase": "red", "attempt": "1", "budget": "2"}
    (step.wt / ".tdd" / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in marks + [other]))
    stages = Sequenced({"revise.sh": (1, line + "\n")},
                       sequence={"green-half.sh": [(1, REJECTED_GREEN), (0, "green-half settled\n")],
                                 "reroute.sh": [(1, "route=revise phase=green\n"), (0, "")]})
    code, out, err, stages = step(stages=stages)

    assert (code, out.splitlines()[-1]) == (0, "next=cycle"), err
    assert stages.names() == ["red-half.sh", "green-half.sh", "reroute.sh", "revise.sh", "reroute.sh",
                              "green-half.sh", "refactor-half.sh", "step-close.sh"]
    assert stages.calls[4][1] == ("12", ".tdd/revise-green-2.out")


def test_a_revise_green_stop_on_impossible_keeps_the_revise_seam_with_no_reroute_4434(step):
    (step.wt / ".tdd" / "verdict-green.exit").write_text("1\n")
    code, out, err, stages = step(answers={"green-half.sh": (1, REJECTED_GREEN),
                                           "reroute.sh": (1, "route=revise phase=green\n"),
                                           "revise.sh": (1, "stopped at 3 OUTCOME: IMPOSSIBLE\n")})

    assert (code, stages.names(), out.splitlines()[-1]) == (
        1, ["red-half.sh", "green-half.sh", "reroute.sh", "revise.sh"], "seam=revise code=1 next=" + REVISE)


def test_a_reroutes_route_revise_red_goes_back_to_red_half_whose_rejected_record_sends_it_to_revise_red_4434(step):
    """PRD 038.10 RRT5: a verify-red REJECT of a rerouted case is revise.sh <n> red's; its 0 finishes red-half, and
    green-half then starts afresh, the green REJECT the reroute answered cleared."""
    rejected = step.wt / ".tdd" / "issue-12-red-half-rejected-wait"
    (step.wt / ".tdd" / "verdict-green.exit").write_text("1\n")

    class RedRevise(Sequenced):
        def __call__(self, name, *args, **kw):
            base = os.path.basename(name)
            if base == "reroute.sh":
                rejected.write_text(REJECTED.replace("verdict-green", "verdict-red"))
            if base == "revise.sh":
                rejected.unlink()
            return super().__call__(name, *args, **kw)

    stages = RedRevise({"reroute.sh": (1, "route=revise phase=red\n")},
                       sequence={"green-half.sh": [(1, REJECTED_GREEN), (0, "green-half settled\n")]})
    code, out, err, stages = step(stages=stages)

    assert (code, out.splitlines()[-1]) == (0, "next=cycle"), err
    assert stages.names() == ["red-half.sh", "green-half.sh", "reroute.sh", "revise.sh", "red-half.sh",
                              "green-half.sh", "refactor-half.sh", "step-close.sh"]
    assert stages.calls[3][1] == ("12", "red")
    assert not (step.wt / ".tdd" / "verdict-green.exit").exists()


def test_a_call_after_a_reroute_to_red_recorded_at_green_half_calls_revise_red_first_never_starting_at_green_4613(
        step):
    """#4613 criterion 2: reroute.sh's `route=revise phase=red` outside this call left red-half's rejected record
    naming the step while the step seam still says green-half; red is revised first, never skipped."""
    rejected = step.wt / ".tdd" / "issue-12-red-half-rejected-wait"
    rejected.write_text(REJECTED.replace("verdict-green", "verdict-red"))
    (step.wt / ".tdd" / "issue-12-step").write_text("stage=green-half\nstep=%s\n" % STEP)

    class RedRevise(Stages):
        def __call__(self, name, *args, **kw):
            if os.path.basename(name) == "revise.sh":
                rejected.unlink()
            return super().__call__(name, *args, **kw)

    code, out, err, stages = step(stages=RedRevise())

    assert (code, out.splitlines()[-1]) == (0, "next=cycle"), err
    assert stages.names() == ["revise.sh"] + list(STAGES)
    assert stages.calls[0][1] == ("12", "red")


def test_a_stale_green_half_rejected_record_after_a_reroute_to_red_never_revises_green_4613(step):
    """#4613 criterion 1: a reroute to red left red-half's rejected record naming the step beside an older green-half
    rejected record also naming it; red is revised, then green-half runs afresh, never revise.sh <n> green."""
    rejected = step.wt / ".tdd" / "issue-12-red-half-rejected-wait"
    rejected.write_text(REJECTED.replace("verdict-green", "verdict-red"))
    (step.wt / ".tdd" / "issue-12-green-half-rejected-wait").write_text(REJECTED)

    class RedRevise(Stages):
        def __call__(self, name, *args, **kw):
            if os.path.basename(name) == "revise.sh":
                rejected.unlink(missing_ok=True)
            return super().__call__(name, *args, **kw)

    code, out, err, stages = step(stages=RedRevise())

    assert (code, out.splitlines()[-1]) == (0, "next=cycle"), err
    assert stages.names() == ["revise.sh"] + list(STAGES)
    assert [call[1] for call in stages.calls if os.path.basename(call[0]) == "revise.sh"] == [("12", "red")]


def test_a_red_half_rejected_record_beside_a_refactor_pending_step_never_answers_green_or_restarts_at_red_4613(step):
    """#4613: the red-half override is for a step still being developed; a step waiting for its refactor keeps
    green's REJECT files and resumes at refactor-half, never back at red-half."""
    (step.wt / ".tdd" / "issue-12-red-half-rejected-wait").write_text(REJECTED.replace("verdict-green", "verdict-red"))
    green_rejected = step.wt / ".tdd" / "issue-12-green-half-rejected-wait"
    green_rejected.write_text(REJECTED)
    green_exit = step.wt / ".tdd" / "verdict-green.exit"
    green_exit.write_text("1\n")

    code, out, err, stages = step(ledger=PENDING)

    assert (code, stages.names()) == (0, ["refactor-half.sh", "step-close.sh"]), err
    assert (green_rejected.exists(), green_exit.exists()) == (True, True)


def _reroute_wait(step, text):
    (step.wt / ".tdd" / "issue-12-reroute-wait").write_text(
        '{"conductor": null, "at": "verdict-red", "values": {"report": ".tdd/revise-green-1.out", "step": "%s"}}'
        % text)
    (step.wt / ".tdd" / "issue-12-step").write_text("stage=green-half\nstep=%s\n" % STEP)


def test_a_reroute_exit_3_is_called_again_through_run_step_which_goes_back_to_reroute_on_the_same_report_4434(step):
    """PRD 038.10 RRT6: reroute.sh is sliced; its wait record names the report and the step."""
    _reroute_wait(step, STEP)
    code, out, err, stages = step(answers={"reroute.sh": (3, "waiting on verdict-red\n")})

    assert (code, stages.names(), out.splitlines()[-1]) == (3, ["reroute.sh"], "seam=reroute code=3 next=run-step.sh 12")
    assert stages.calls[0][1] == ("12", ".tdd/revise-green-1.out")


def test_a_reroute_wait_record_naming_another_step_is_not_resumed_4434(step):
    _reroute_wait(step, "zero ⟦criterion 1⟧")
    code, out, err, stages = step()

    assert (code, stages.names()) == (0, ["green-half.sh", "refactor-half.sh", "step-close.sh"]), err


@pytest.mark.parametrize("line", ["stopped at 1 WRONG_TEST: the case asserts the old rule", REJECTED_GREEN.strip()])
def test_hand_reroute_stops_where_reroute_would_run_never_calling_it_and_reroute_is_outside_the_series_4434(
        step, line):
    """PRD 038.10 RRT8, S2: `--hand reroute` keeps SKILL.md's Green prose path."""
    run_step = importlib.import_module("veri.run_step")
    (step.wt / ".tdd" / "verdict-green.exit").write_text("1\n")
    code, out, err, stages = step(answers={"green-half.sh": (1, line + "\n")}, argv=("12", "--hand", "reroute"))

    assert (code, stages.names(), out.splitlines()[-1]) == (
        1, ["red-half.sh", "green-half.sh"], "seam=reroute code=1 reason=hand next=" + GREEN)
    assert "stage=green-half" in (step.wt / ".tdd" / "issue-12-step").read_text().splitlines()
    assert ("reroute" in run_step.STAGES, run_step.CALLS) == (True, STAGES)
    assert step(argv=("12", "--from", "reroute"))[0] == 2


@pytest.mark.parametrize("said", ["route=revise phase=green", "route=revise phase=red"])
def test_a_route_revise_line_with_an_exit_other_than_1_is_the_reroute_seam_never_a_revise_4434(step, said):
    """Exit codes are the API: only reroute.sh's 1 carries a route; its 2 is no answer, whatever its last line."""
    (step.wt / ".tdd" / "verdict-green.exit").write_text("1\n")
    code, out, err, stages = step(answers={"green-half.sh": (1, REJECTED_GREEN), "reroute.sh": (2, said + "\n")})

    assert (code, stages.names(), out.splitlines()[-1]) == (
        2, ["red-half.sh", "green-half.sh", "reroute.sh"], "seam=reroute code=2 next=" + GREEN)


GO_RED_STEP = "Go-red guard: probe `src/run.py` `if stacked:` → `if False:` on `t.py::c` ⟦go-red⟧ ⟦criterion 1⟧"


def test_4443_a_go_red_step_runs_go_red_step_as_its_one_stage_and_ends_on_its_next_line(step):
    code, out, err, stages = step(ledger=LEDGER % GO_RED_STEP,
                                  answers={"go-red-step.sh": (0, "step-tick.sh 12 exit 0\nnext=cycle\n")})

    assert (code, [(c[0], c[1]) for c in stages.calls], out.splitlines()[-1]) == (
        0, [("go-red-step.sh", ("12",))], "next=cycle"), err


GO_RED = "GO-RED.md#A `⟦go-red⟧` step — a mutation probe on its named case"


@pytest.mark.parametrize("argv, text, code_, names, last", [
    (("12", "--hand", "go-red-step"), GO_RED_STEP, 1, [], "seam=go-red-step code=1 reason=hand next=" + GO_RED),
    (("12", "--from", "go-red-step"), GO_RED_STEP, 0, ["go-red-step.sh"], "next=cycle"),
    (("12", "--from", "go-red-step"), STEP, 2, [], None),
    (("12", "--from", "red-half"), GO_RED_STEP, 2, [], None),
])
def test_4443_hand_and_from_go_red_step_and_a_from_across_kinds_is_exit_2(step, argv, text, code_, names, last):
    code, out, err, stages = step(ledger=LEDGER % text, argv=argv, answers={"go-red-step.sh": (0, "next=cycle\n")})

    assert (code, stages.names()) == (code_, names), err
    if last is not None:
        assert out.splitlines()[-1] == last


@pytest.mark.parametrize("code_, last", [(1, "seam=go-red-step code=1 next=" + GO_RED),
                                         (2, "seam=go-red-step code=2 next=" + GO_RED),
                                         (3, "seam=go-red-step code=3 next=run-step.sh 12")])
def test_4443_a_go_red_step_exit_other_than_0_ends_on_its_seam_calling_no_revise(step, code_, last):
    code, out, err, stages = step(ledger=LEDGER % GO_RED_STEP, answers={"go-red-step.sh": (code_, "")})

    assert (code, stages.names(), out.splitlines()[-1]) == (code_, ["go-red-step.sh"], last), err


@pytest.mark.parametrize("text", [
    "SKILL.md routes a `⟦go-red⟧` step to go-red-step.sh ⟦criterion 1⟧",
    "⟦go-red⟧ Go-red guard: probe `src/run.py` `if stacked:` → `if False:` on `t.py::c` ⟦criterion 1⟧",
], ids=["backticked-mention", "leading-marker-only"])
def test_4443_a_step_mentioning_go_red_without_the_trailing_marker_runs_as_a_cycle_step(step, text):
    code, out, err, stages = step(ledger=LEDGER % text)

    assert (code, tuple(stages.names())) == (0, STAGES), err


SKILL_EDIT_STEP = "Edit the unit `skills/tdd/SKILL-EDIT.md` ⟦skill-edit⟧ ⟦criterion 1⟧"


def test_4450_a_skill_edit_step_runs_skill_edit_half_as_its_one_stage_never_passing_change(step):
    run_step = importlib.import_module("veri.run_step")
    code, out, err, stages = step(ledger=LEDGER % SKILL_EDIT_STEP,
                                  answers={"skill-edit-half.sh": (0, "step-tick.sh 12 exit 0\nnext=cycle\n")})

    assert (code, [(c[0], c[1]) for c in stages.calls], out.splitlines()[-1]) == (
        0, [("skill-edit-half.sh", ("12",))], "next=cycle"), err
    assert "skill-edit-half" in run_step.STAGES and "skill-edit-half" not in run_step.PHASES
    assert run_step.KINDS["⟦skill-edit⟧"] == ("SKILL-EDIT.md#The skill-edit step", "skill-edit-half")


def test_4450_hand_skill_edit_half_stops_before_it_on_a_skill_edit_step_never_calling_it(step):
    code, out, err, stages = step(ledger=LEDGER % SKILL_EDIT_STEP, argv=("12", "--hand", "skill-edit-half"))

    assert (code, stages.names(), out.splitlines()[-1]) == (
        1, [], "seam=skill-edit-half code=1 reason=hand next=SKILL-EDIT.md#The skill-edit step"), err


def test_4450_from_skill_edit_half_on_a_skill_edit_step_starts_at_it_and_calls_it(step):
    code, out, err, stages = step(ledger=LEDGER % SKILL_EDIT_STEP, argv=("12", "--from", "skill-edit-half"),
                                  answers={"skill-edit-half.sh": (0, "step-tick.sh 12 exit 0\nnext=cycle\n")})

    assert (code, [(c[0], c[1]) for c in stages.calls], out.splitlines()[-1]) == (
        0, [("skill-edit-half.sh", ("12",))], "next=cycle"), err


def test_4450_a_skill_edit_half_exit_1_ends_on_its_seam_exiting_1_and_calling_no_revise(step):
    code, out, err, stages = step(ledger=LEDGER % SKILL_EDIT_STEP,
                                  answers={"skill-edit-half.sh": (1, "skill-edit-step.sh exit 1\n")})

    assert (code, stages.names(), out.splitlines()[-1]) == (
        1, ["skill-edit-half.sh"], "seam=skill-edit-half code=1 next=SKILL-EDIT.md#The skill-edit step"), err


def test_4450_a_skill_edit_half_exit_2_names_its_out_file_with_refusal_yes_on_the_line_before_its_seam(step):
    (step.wt / ".tdd" / "skill-edit-12.out").write_text(
        "Requirements heading names no existing unit: skills/tdd/NOPE.md\n")

    code, out, err, stages = step(ledger=LEDGER % SKILL_EDIT_STEP,
                                  answers={"skill-edit-half.sh": (2, "stopped at 2 skill-edit-step.sh exit 2\n")})

    assert (code, out.splitlines()[-2:]) == (
        2, ["out=.tdd/skill-edit-12.out refusal=yes",
            "seam=skill-edit-half code=2 next=SKILL-EDIT.md#The skill-edit step"]), err


def test_4450_a_skill_edit_half_exit_2_with_no_out_file_prints_refusal_no_on_the_line_before_its_seam(step):
    code, out, err, stages = step(ledger=LEDGER % SKILL_EDIT_STEP,
                                  answers={"skill-edit-half.sh": (2, "stopped at 2 skill-edit-step.sh exit 2\n")})

    assert (code, out.splitlines()[-2:]) == (
        2, ["out=.tdd/skill-edit-12.out refusal=no",
            "seam=skill-edit-half code=2 next=SKILL-EDIT.md#The skill-edit step"]), err


def test_4450_a_skill_edit_half_exit_2_with_an_out_file_holding_no_refusal_line_prints_refusal_no(step):
    (step.wt / ".tdd" / "skill-edit-12.out").write_text("author notes\nnot a Requirements heading names no existing unit: x\n")

    code, out, err, stages = step(ledger=LEDGER % SKILL_EDIT_STEP,
                                  answers={"skill-edit-half.sh": (2, "stopped at 2 skill-edit-step.sh exit 2\n")})

    assert (code, out.splitlines()[-2:]) == (
        2, ["out=.tdd/skill-edit-12.out refusal=no",
            "seam=skill-edit-half code=2 next=SKILL-EDIT.md#The skill-edit step"]), err


def test_4450_a_skill_edit_half_exit_2_with_an_out_file_holding_another_requirements_refusal_prints_refusal_yes(step):
    (step.wt / ".tdd" / "skill-edit-12.out").write_text("a ## Requirements row is under no ### unit heading\n")

    code, out, err, stages = step(ledger=LEDGER % SKILL_EDIT_STEP,
                                  answers={"skill-edit-half.sh": (2, "stopped at 2 skill-edit-step.sh exit 2\n")})

    assert (code, out.splitlines()[-2:]) == (
        2, ["out=.tdd/skill-edit-12.out refusal=yes",
            "seam=skill-edit-half code=2 next=SKILL-EDIT.md#The skill-edit step"]), err


@pytest.mark.parametrize("refusal", [
    "rows for skills/tdd/SKILL.md are not under ## Requirements",
    "## Requirements has no ### heading for unit: skills/tdd/SKILL.md",
    "## Requirements table for skills/tdd/SKILL.md lacks its header: | ID |",
])
def test_4450_a_skill_edit_half_exit_2_with_an_out_file_holding_a_remaining_requirements_refusal_prints_refusal_yes(step, refusal):
    (step.wt / ".tdd" / "skill-edit-12.out").write_text(refusal + "\n")

    code, out, err, stages = step(ledger=LEDGER % SKILL_EDIT_STEP,
                                  answers={"skill-edit-half.sh": (2, "stopped at 2 skill-edit-step.sh exit 2\n")})

    assert (code, out.splitlines()[-2:]) == (
        2, ["out=.tdd/skill-edit-12.out refusal=yes",
            "seam=skill-edit-half code=2 next=SKILL-EDIT.md#The skill-edit step"]), err


@pytest.mark.parametrize("refusal", [
    "Requirement row SC1 splits into 4 cells, not ID, Requirement and Why: escape an unescaped | as \\|",
    "Requirement row SC1 splits into 2 cells, not ID, Requirement and Why",
    "Requirement row SC2<reword> states the full text the unit already holds under SC1",
])
def test_4752_a_skill_edit_half_exit_2_with_an_out_file_holding_a_requirement_row_refusal_prints_refusal_yes(step, refusal):
    (step.wt / ".tdd" / "skill-edit-12.out").write_text(refusal + "\n")

    code, out, err, stages = step(ledger=LEDGER % SKILL_EDIT_STEP,
                                  answers={"skill-edit-half.sh": (2, "stopped at 2 skill-edit-step.sh exit 2\n")})

    assert (code, out.splitlines()[-2:]) == (
        2, ["out=.tdd/skill-edit-12.out refusal=yes",
            "seam=skill-edit-half code=2 next=SKILL-EDIT.md#The skill-edit step"]), err


def test_4450_a_skill_edit_half_exit_2_with_an_out_file_holding_a_guard_refusal_line_prints_refusal_yes(step):
    (step.wt / ".tdd" / "skill-edit-12.out").write_text("skill-edit-guard.sh: refusing to edit skills/tdd/SKILL.md\n")

    code, out, err, stages = step(ledger=LEDGER % SKILL_EDIT_STEP,
                                  answers={"skill-edit-half.sh": (2, "stopped at 2 skill-edit-step.sh exit 2\n")})

    assert (code, out.splitlines()[-2:]) == (
        2, ["out=.tdd/skill-edit-12.out refusal=yes",
            "seam=skill-edit-half code=2 next=SKILL-EDIT.md#The skill-edit step"]), err


def test_4450_another_stages_exit_2_prints_no_skill_edit_out_line_before_its_seam(step):
    """SKH18: the `out=… refusal=` line belongs to skill-edit-half's exit 2 only; a cycle stage's 2 ends on its seam."""
    (step.wt / ".tdd" / "skill-edit-12.out").write_text("skill-edit-guard.sh: refusing to edit skills/tdd/SKILL.md\n")

    code, out, err, stages = step(ledger=LEDGER % STEP, answers={"red-half.sh": (2, "stopped at 1 x exit 2\n")})

    assert (code, stages.names(), [line for line in out.splitlines() if line.startswith("out=")]) == (
        2, ["red-half.sh"], []), (out, err)


def test_4547_a_step_replaced_instead_of_by_a_same_text_added_step_runs_red_half_not_the_replaced_steps_revise(
        step, fake_processes):
    """#4547: ledger.same_step drops ⟦added⟧, so the step add-ledger-step.sh instead-of puts in place of a rejected one
    would read its `<stage>-rejected` record and go straight to the spent revise; the replacement starts fresh."""
    add_ledger_step = importlib.import_module("veri.add_ledger_step")
    ledger = step.wt / ".tdd" / "issue-12.md"
    ledger.write_text(LEDGER % STEP)
    fake_processes.answers({"git log --format=%H %s": (0, "beef plan: scope #12 into 3 steps (#12)\n", ""),
                            "git show beef:./": (0, LEDGER % STEP, "")})
    (step.wt / ".tdd" / "issue-12-green-half-rejected-wait").write_text(
        '{"conductor": null, "at": "verdict-green", "values": {}, "step": "%s"}' % STEP)

    assert add_ledger_step.add(str(ledger), "instead-of", "one thing works", ["one thing works"]) == 0
    code, out, err, stages = step(ledger=ledger.read_text())

    assert "one thing works ⟦added⟧" in ledger.read_text()
    assert (code, stages.names()) == (0, list(STAGES)), err


def test_4682_a_skill_edit_step_whose_reword_row_states_text_held_under_another_id_ends_on_exit_2_unticked_with_no_step_done(
        step, monkeypatch, fake_processes):
    """The real skill_edit_half and skill_edit_step run in-process under run_step; only the process boundaries (gh, git,
    detach-command.sh, step-tick.sh, the grader and the author) are faked (#4682 criterion 2)."""
    skill_edit_half = importlib.import_module("veri.skill_edit_half")
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    wt = step.wt
    listing = ("## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
               "| X1 | The widget is blue. | because |\n| X2 | The widget is red. | since |\n")
    (wt / "unit.md").write_text("The widget is painted a deep blue.\n")
    (wt / "REQUIREMENTS.md").write_text(listing)
    (wt / "GRADED").write_text("")
    body = ("## Problem\n\nText.\n\n## Requirements\n\n### unit.md\n\n"
            "| ID | Requirement | Why |\n|---|---|---|\n| X2<reword> | The widget is blue. | because |\n")
    fake_processes.answers({}, default=lambda line, **_: (0, "abc1234\n", ""))
    monkeypatch.setattr(importlib.import_module("veri.leaf"), "launch", lambda *a, **k: 0)
    monkeypatch.setattr(skill_edit_step, "_grade", lambda *a: (0, ""))
    monkeypatch.setattr(skill_edit_step, "_author", lambda *a: 0)
    detached, ticks = [], []

    def boundary(name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        if base == "skill-edit-half.sh":
            return skill_edit_half.main(list(args)), "", ""
        if base == "gh":
            return 0, body, ""
        if base == "git":
            return (1 if "ls-files" in args else 0), "", ""
        if base == "detach-command.sh" and args[0] == "start":
            detached.append(list(args[3:]))
            return 0, "", ""
        if base == "detach-command.sh" and args[0] == "wait":
            here = os.getcwd()
            os.chdir(cwd)
            try:
                code = skill_edit_step.main(detached[-1])
            finally:
                os.chdir(here)
            return (0, "", "") if code == 0 else (1, "%d\n" % code, "")
        if base == "step-tick.sh":
            ticks.append(args)
            return 0, "", ""
        raise AssertionError("unexpected process: %s %s" % (name, args))

    ledger = LEDGER % "reword the rows of `unit.md` ⟦skill-edit⟧ ⟦criterion 1⟧"
    code, out, err, _ = step(ledger=ledger, stages=boundary)

    assert detached and detached[-1][-1] == "unit.md", detached
    assert (code, ticks) == (2, []), (code, ticks, out, err)
    assert "X2" in err and "X1" in err, err
    assert (wt / ".tdd" / "issue-12.md").read_text() == ledger
    assert (wt / "REQUIREMENTS.md").read_text() == listing
    events = [p for p in (wt, wt.parent.parent.parent) if (p / ".tdd" / "events.jsonl").exists()]
    assert not any("step-done" in (p / ".tdd" / "events.jsonl").read_text() for p in events), events


def test_4709_a_step_that_only_quotes_diff_checked_in_its_prose_runs_the_cycle_series_not_diff_step(step):
    text = "appends a repair step carrying `⟦branch-repair⟧` and no `⟦diff-checked⟧` ⟦criterion 1⟧"
    code, out, err, stages = step(ledger=LEDGER % text)

    assert (code, stages.names()) == (0, list(STAGES)), err


def test_4709_a_step_only_quoting_a_green_half_unhandled_mark_in_its_prose_does_not_stop_unmodelled(step):
    code, out, err, stages = step(ledger=LEDGER % "document the `⟦ci-repair⟧` mark in `a.md` ⟦criterion 1⟧")

    assert "reason=unmodelled" not in out, out


def test_4707_a_branch_repair_step_without_diff_checked_runs_the_red_green_series_not_diff_step(step):
    text = "fix what verify-branch rejected: criterion 3 has no case MISSING_TEST: a gear meshes ⟦branch-repair⟧"
    code, out, err, stages = step(ledger=LEDGER % text)

    assert (code, stages.names()) == (0, list(STAGES)), out + err
