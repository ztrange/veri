"""In-process cases for veri/step_close.py, the module step-close.sh is a shim over (PRD 027.8, #4029)."""
import hashlib
import importlib
import os

import pytest

STEP = "one thing works ⟦criterion 1⟧"
LEDGER = "# Plan for #12\n\n- [x] %s ⟂ refactor pending\n- [ ] two ⟦criterion 2⟧\n"
GREEN_SHA = "d" * 40
BASE_SHA = "c" * 40
VERDICT_LOG = "FLAGS: none\nVERDICT: PASS\n"
REFACTOR_HALF = ("step=%s\ngreen_sha=" + GREEN_SHA + "\ncount=1\nbudget=5\nstopped=nothing-left\n"
                 "verdict_log=" + hashlib.sha256(VERDICT_LOG.encode()).hexdigest() + "\n"
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
        if base == "git" and args[:2] == ("status", "--porcelain"):
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
                 "stage": (wt / ".tdd" / "stage-rl.t", "100\n"),
                 "verdict": (wt / ".tdd" / "verify-refactor.log", VERDICT_LOG)}
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


@pytest.mark.parametrize("log", ["FLAGS: uncovered-spec | a later verdict's flag\nVERDICT: PASS\n", None],
                         ids=["a later verdict", "no verdict log"])
def test_4029_a_refactor_half_file_from_an_earlier_verdict_is_exit_2_before_any_inner_call(close, log):
    if log is not None:
        (close.wt / ".tdd" / "verify-refactor.log").write_text(log)
    code, out, err, fake = close(missing=("verdict",) if log is None else ())

    assert (code, fake.calls) == (2, [])
    assert "another verdict" in err


def test_4029_a_refactor_half_file_from_a_skipped_verify_names_no_verdict_log(close):
    code, out, err, fake = close(half=REFACTOR_HALF.replace(
        "verdict_log=" + hashlib.sha256(VERDICT_LOG.encode()).hexdigest(), "verdict_log=none") % STEP,
        missing=("verdict",))

    assert code == 0


def _named(fake):
    return [(c[0], c[1][:1]) for c in fake.calls]


def test_4029_it_checks_graded_units_and_pins_rerecords_checks_the_tree_clears_commits_and_pushes_in_order(close):
    code, out, err, fake = close()

    assert _named(fake)[:11] == [
        ("graded-changed.sh", (GREEN_SHA,)), ("git", ("rev-parse",)), ("pin-recheck.sh", (BASE_SHA,)),
        ("tests-frozen.sh", ("rerecord-refactored",)), ("git", ("status",)),
        ("clear-refactor-pending.sh", (".tdd/issue-12.md",)), ("git", ("add",)), ("git", ("commit",)),
        ("push-branch.sh", ()), ("event.sh", ("stage-end",)), ("stop-requested.sh", ())]
    assert fake.call("git", "rev-parse")[1] == ("rev-parse", GREEN_SHA + "~1")
    assert fake.call("pin-recheck.sh")[1] == (BASE_SHA,)
    assert fake.call("tests-frozen.sh")[1] == ("rerecord-refactored", ".tdd/issue-12.md", GREEN_SHA)
    assert fake.call("clear-refactor-pending.sh")[1] == (".tdd/issue-12.md", STEP)
    assert fake.call("git", "add")[1] == ("add", "-A")
    assert fake.call("git", "commit")[1] == ("commit", "-m", "chore: refactor verified for one thing works (#12)")
    assert all(c[2] == str(close.wt) for c in fake.calls)


def test_4029_the_stage_ends_with_status_0_after_the_push_and_before_the_stop_ask(close, monkeypatch):
    monkeypatch.setattr("time.time", lambda: 160.0)
    code, out, err, fake = close()

    stage = fake.call("event.sh", "stage-end")
    assert stage[1] == ("stage-end", "stage=refactor-loop", "status=0", "secs=60")
    assert stage[3]["VERI_ISSUE"] == "12"


def test_4029_an_unreadable_stage_start_time_stops_it_with_exit_2_after_the_push(close):
    code, out, err, fake = close(missing=("stage",))

    assert (code, out.splitlines()[-1], fake.calls[-1][0]) == (2, "stopped at 6 no .tdd/stage-rl.t", "push-branch.sh")


@pytest.mark.parametrize("script, first, inner", [
    ("graded-changed.sh", None, 1), ("graded-changed.sh", None, 2), ("pin-recheck.sh", None, 1),
    ("pin-recheck.sh", None, 2), ("tests-frozen.sh", None, 1), ("tests-frozen.sh", None, 2),
    ("tests-frozen.sh", None, 3), ("clear-refactor-pending.sh", None, 2), ("git", "commit", 1),
    ("push-branch.sh", None, 1), ("push-branch.sh", None, 2)])
def test_4029_a_check_clear_commit_or_push_that_is_not_clean_stops_it_with_its_code_and_runs_nothing_later(
        close, script, first, inner):
    code, out, err, fake = close(answers={(script, first): (inner, "")})

    assert code == (inner if inner not in (0, 3) else 1)
    last = fake.calls[-1]
    assert (last[0], last[1][:1] if first else ()) == (script, (first,) if first else ())
    assert out.splitlines()[-1].startswith("stopped at 6 " + script)
    assert out.splitlines()[-1].endswith(" exit %d" % inner)


def test_4029_a_re_record_failure_stops_before_the_clear(close):
    code, out, err, fake = close(answers={("tests-frozen.sh", None): (1, "")})

    assert "clear-refactor-pending.sh" not in fake.names() and ("git", ("commit",)) not in _named(fake)


@pytest.mark.parametrize("porcelain, clean", [
    (" M .tdd/issue-12.md\n?? .tdd/issue-12-added.md\n?? .tdd/issue-12-refactor-owed.md\n", True),
    (" M src/a.py\n", False), ("?? .tdd/issue-12.md.orig\n", False), (" D tests/test_a.py\n", False)])
def test_4029_immediately_before_the_clear_a_path_beyond_the_ledger_files_stops_it_with_exit_1_committing_nothing(
        close, porcelain, clean):
    code, out, err, fake = close(fake=Fake(porcelain=porcelain))

    if clean:
        assert code == 0
        return
    assert (code, out.splitlines()[-1]) == (1, "stopped at 6 tree-check")
    assert fake.calls[-1][:2] == ("git", ("status", "--porcelain", "--untracked-files=all"))
    assert "clear-refactor-pending.sh" not in fake.names()


@pytest.mark.parametrize("inner, said", [(0, "at-ledger"), (0, "now"), (2, "")])
def test_4029_the_stop_ask_after_the_push_stops_it_on_exit_0_or_2(close, inner, said):
    code, out, err, fake = close(answers={("stop-requested.sh", None): (inner, said + "\n")})

    assert code == (inner if inner else 1)
    assert fake.calls[-1][0] == "stop-requested.sh"
    assert out.splitlines()[-1].startswith("stopped at 6 stop-requested.sh exit %d" % inner)


def test_4029_after_the_stop_ask_it_mirrors_the_step_ticks_its_finished_criterion_and_marks_step_done(close):
    code, out, err, fake = close()

    tail = [(c[0], c[1]) for c in fake.calls[fake.names().index("stop-requested.sh") + 1:]]
    assert tail[:6] == [("comment.sh", ("12", "step-done")), ("criterion-finished.sh", ("1",)),
                        ("gh", ("api", "repos/{owner}/{repo}/issues/12", "-q", ".body")),
                        ("ledger-steps.sh", ("criterion", "1")), ("tick-issue-criterion.sh", ("12", "one thing works")),
                        ("ledger-steps.sh", ("last-done",))]
    assert tail[6] == ("event.sh", ("step-done",))
    assert fake.call("criterion-finished.sh")[4]["stdin"] == (close.wt / ".tdd" / "issue-12.md").read_text()
    assert fake.call("criterion-finished.sh")[4]["err"] == ".tdd/criterion-finished.err"
    assert fake.call("ledger-steps.sh", "criterion")[4]["stdin"] == BODY
    done = fake.call("event.sh", "step-done")[3]
    assert (done["VERI_ISSUE"], done["VERI_ACTOR"], done["VERI_STEP"]) == ("12", "conductor", STEP)


def test_4029_a_criterion_not_yet_finished_ticks_nothing(close):
    code, out, err, fake = close(answers={("criterion-finished.sh", None): (3, "")})

    assert code == 0
    assert "tick-issue-criterion.sh" not in fake.names() and "gh" not in fake.names()


@pytest.mark.parametrize("inner", [1, 2])
def test_4029_an_unreadable_criterion_stops_it_with_its_code_before_the_step_done_mark(close, inner):
    code, out, err, fake = close(answers={("criterion-finished.sh", None): (inner, "")})

    assert (code, out.splitlines()[-1]) == (inner, "stopped at 6 criterion-finished.sh 1 2> .tdd/criterion-finished.err exit %d" % inner)
    assert fake.calls[-1][0] == "criterion-finished.sh"


def test_4029_a_step_with_no_criterion_asks_nothing(close):
    code, out, err, fake = close(step="one thing works")

    assert code == 0
    assert not {"criterion-finished.sh", "tick-issue-criterion.sh", "gh"} & set(fake.names())
    assert "event.sh" in fake.names()[fake.names().index("comment.sh"):]


def test_4029_a_step_with_two_criteria_asks_each_in_order(close):
    code, out, err, fake = close(step="one thing works ⟦criterion 1⟧ ⟦criterion 3⟧")

    assert [c[1] for c in fake.calls if c[0] == "criterion-finished.sh"] == [("1",), ("3",)]


def test_4029_no_unchecked_step_left_settles_next_draft_pr_without_asking_the_budget(close):
    code, out, err, fake = close(answers={("next-unchecked.sh", None): (3, "")})

    assert (code, out.splitlines()[-1]) == (0, "next=draft-pr")
    assert "run-affordable.sh" not in fake.names()
    assert (close.wt / ".tdd" / "issue-12-step-close").read_text() == "next=draft-pr\n"


@pytest.mark.parametrize("inner", [0, 3])
def test_4029_an_affordable_run_settles_next_cycle_counting_the_open_steps_only(close, inner):
    code, out, err, fake = close(answers={("run-affordable.sh", None): (inner, "")})

    assert (code, out.splitlines()[-1]) == (0, "next=cycle")
    assert fake.call("run-affordable.sh")[1] == ("1",)
    assert fake.names()[-3:] == ["next-unchecked.sh", "ledger-steps.sh", "run-affordable.sh"]
    assert fake.call("next-unchecked.sh")[4]["stdin"] == (close.wt / ".tdd" / "issue-12.md").read_text()


@pytest.mark.parametrize("script, inner", [("run-affordable.sh", 1), ("run-affordable.sh", 2),
                                           ("next-unchecked.sh", 2)])
def test_4029_an_unaffordable_or_unanswered_next_step_stops_it_settling_nothing(close, script, inner):
    code, out, err, fake = close(answers={(script, None): (inner, "")})

    assert code == inner and out.splitlines()[-1].startswith("stopped at 6 " + script)
    assert not (close.wt / ".tdd" / "issue-12-step-close").exists()
    assert "comment.sh" in fake.names() and not [c for c in fake.calls if c[0] == "comment.sh" and c[1][1] != "step-done"]


def test_4029_the_pins_needing_a_look_are_settled_as_owed_pin_lines_and_printed_last(close):
    pins = "needs a look: a.mut (old text gone)\nstale: r.mut a.py\nneeds a look: 2 pins b.mut (base run failed)\n"
    code, out, err, fake = close(fake=Fake(pins=pins))

    settled = "next=cycle\nowed_pin=needs a look: a.mut (old text gone)\nowed_pin=needs a look: 2 pins b.mut (base run failed)\n"
    assert code == 0
    assert out.endswith(settled)
    assert (close.wt / ".tdd" / "issue-12-step-close").read_text() == settled


READ = ("git", "pin-recheck.sh", "ledger-steps.sh", "gh")  # stdout read as a value


def test_4029_every_inner_call_prints_its_name_and_exit_then_its_stdout_and_its_stderr(close):
    class Marked(Fake):
        def __call__(self, name, *args, **kw):
            code, out, err = super().__call__(name, *args, **kw)
            if os.path.basename(name) in READ:
                return code, out, err
            return code, "OUT<%d>\n" % len(self.calls) + out, "ERR<%d>\n" % len(self.calls)

    code, out, err, fake = close(fake=Marked())

    lines = out.splitlines()
    assert code == 0
    for i, c in enumerate(fake.calls, 1):
        if c[0] in READ:
            assert any(line.startswith(c[0]) and line.endswith(" exit 0") for line in lines)
            continue
        named = lines[lines.index("OUT<%d>" % i) - 1]
        assert named.startswith(c[0]) and named.endswith(" exit %d" % (3 if c[0] == "stop-requested.sh" else 0))
        assert "ERR<%d>" % i in err or c[4].get("err")


# Inner calls the Refactor loop section does not name, each by name with its reason: none.
NAMED_ELSEWHERE = {}


def test_4029_every_inner_call_in_the_ordered_list_is_a_script_the_refactor_loop_section_names():
    from pathlib import Path
    step_close = importlib.import_module("veri.step_close")
    skill = (Path(step_close.__file__).resolve().parents[2] / "SKILL.md").read_text()
    section = skill[skill.index("#### Refactor loop — one leaf"):skill.index("#### A `⟦diff-checked⟧` step")]

    assert [name for name in step_close.CALLS if "$S/" + name not in section and name not in NAMED_ELSEWHERE] == []


@pytest.mark.parametrize("site", ["settle", "ledger_text"])
def test_4029_an_exception_after_the_push_is_a_stop_at_6_with_exit_2_naming_it(close, monkeypatch, site):
    module = importlib.import_module("veri.fused" if site == "settle" else "veri.step_close")

    def broken(*args, **kw):
        raise OSError("disk full")

    monkeypatch.setattr(module, site, broken)
    code, out, err, fake = close()

    assert code == 2 and "push-branch.sh" in fake.names()
    assert out.splitlines()[-1].startswith("stopped at 6 ") and "disk full" in out.splitlines()[-1]


def test_4029_a_clean_run_makes_the_calls_of_the_ordered_list_in_its_order(close):
    step_close = importlib.import_module("veri.step_close")
    code, out, err, fake = close()

    made = [c[0] for c in fake.calls if c[0] not in ("git", "gh")]
    assert code == 0
    assert set(made) == set(step_close.CALLS)
    firsts = [made.index(name) for name in step_close.CALLS]
    assert firsts == sorted(firsts)


def test_4029_it_writes_no_bail_classifies_nothing_resets_nothing_and_grows_no_plan(close):
    for answers in ({("push-branch.sh", None): (2, "")}, {}):
        code, out, err, fake = close(answers=answers)
        assert not {"classify-bail.sh", "preflight-refused.sh", "add-ledger-step.sh", "detach-leaf.sh",
                    "supervise.sh", "pin-reject-route.sh", "adjudicate.sh"} & set(fake.names())
        assert not [c for c in fake.calls if c[0] == "event.sh" and c[1][:1] in (("bail",), ("step-added",))]
        assert not [c for c in fake.calls if c[0] == "git" and c[1][:1] in (("reset",), ("clean",), ("checkout",))]
        assert not [c for c in fake.calls if c[0] == "comment.sh" and c[1][1:2] in (("bail",), ("park",))]
