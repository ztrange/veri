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


REVISE = "REVISE.md#Revising on a REJECT"
REJECTED = '{"conductor": null, "at": "verdict-green", "values": {}, "step": "%s"}' % STEP


@pytest.mark.parametrize("revised, names, last", [
    (0, ["red-half.sh", "green-half.sh", "revise.sh", "green-half.sh", "refactor-half.sh", "step-close.sh"],
     "next=cycle"),
    (1, ["red-half.sh", "green-half.sh", "revise.sh"], "seam=revise code=1 next=" + REVISE),
    (2, ["red-half.sh", "green-half.sh", "revise.sh"], "seam=revise code=2 next=" + REVISE)])
def test_a_half_stopped_by_a_verdict_reject_calls_revise_then_the_stage_again_on_its_0_4433(step, revised, names, last):
    """PRD 038.9 criterion 9: `.tdd/verdict-<phase>.exit` holding 1 is a REJECT revise.sh takes."""
    (step.wt / ".tdd" / "verdict-green.exit").write_text("1\n")

    class Rejected(Stages):
        def __call__(self, name, *args, **kw):
            code, out, err = super().__call__(name, *args, **kw)
            if os.path.basename(name) == "green-half.sh" and self.names().count("green-half.sh") == 1:
                return 1, "stopped at 2 wait-leaf.sh verdict-green exit 1\n", ""
            return code, out, err

    code, out, err, stages = step(stages=Rejected({"revise.sh": (revised, "")}))

    assert (code, stages.names(), out.splitlines()[-1]) == (revised, names, last)
    assert stages.calls[2][1] == ("12", "green")


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
    code, out, err, stages = step(answers={"green-half.sh": (1, "stopped at 2 wait-leaf.sh verdict-green exit 1\n")},
                                  argv=("12", "--hand", "revise"))

    assert (code, stages.names(), out.splitlines()[-1]) == (
        1, ["red-half.sh", "green-half.sh"], "seam=revise code=1 reason=hand next=" + REVISE)
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
