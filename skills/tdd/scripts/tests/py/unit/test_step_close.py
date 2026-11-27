"""In-process cases for veri/step_close.py, the module step-close.sh is a shim over (PRD 027.8, #4029)."""
import hashlib
import importlib
import json
import os

import pytest

STEP = "one thing works ⟦criterion 1⟧"
LEDGER = "# Plan for #12\n\n- [x] %s ⟂ refactor pending\n- [ ] two ⟦criterion 2⟧\n"
GREEN_SHA = "d" * 40
VERDICT_LOG = "FLAGS: none\nVERDICT: PASS\n"
REFACTOR_HALF = ("step=%s\ngreen_sha=" + GREEN_SHA + "\ncount=1\nbudget=5\nstopped=nothing-left\n"
                 "verdict_log=" + hashlib.sha256(VERDICT_LOG.encode()).hexdigest() + "\n"
                 "touched=src/a.py,tests/test_a.py\n")
BODY = "## Acceptance criteria\n\n- [ ] one thing works\n- [ ] two\n"
LEDGER_ROWS = "1\tdone\tstep\tone thing works\n2\topen\tstep\ttwo\n3\topen\tfull-suite\tfull\n"


class Fake:
    """A run_script stand-in: records (basename, args, cwd, env, kw) and answers from <answers>, keyed by
    (basename, first argument or None) -> (code, stdout)."""

    def __init__(self, answers=None, porcelain=""):
        self.answers, self.calls, self.porcelain = dict(answers or {}), [], porcelain

    def __call__(self, name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        self.calls.append((base, args, cwd, env, kw))
        for (script, first), (code, out) in self.answers.items():
            if base == script and (first is None or args[:1] == (first,)):
                return code, out, ""
        if base == "git" and args[:2] == ("log", "-1"):
            return 0, GREEN_SHA + "\n", ""
        if base == "git" and args[:2] == ("status", "--porcelain"):
            return 0, self.porcelain, ""
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
    the main tree, the run's worktree at .tdd/wt/12; returns
    (code, stdout, stderr, fake)."""
    fused = importlib.import_module("veri.fused")
    step_close = importlib.import_module("veri.step_close")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)
    (tmp_path / ".git").mkdir()

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


@pytest.mark.parametrize("missing, named", [("preflight", ".tdd/issue-12-preflight"), ("ledger", ".tdd/issue-12.md")])
def test_4029_a_missing_input_is_exit_2_before_any_inner_call_named_on_stderr(close, missing, named):
    code, out, err, fake = close(missing=(missing,))

    assert (code, fake.calls) == (2, [])
    assert named in err


@pytest.mark.parametrize("given", [{"missing": ("refactor-half",)}, {"half": REFACTOR_HALF % "zero ⟦criterion 1⟧"}])
def test_a_missing_refactor_half_record_or_one_naming_another_step_is_exit_1_on_the_seam_line_before_any_call_4342(
        close, given):
    """SC4, replacing #4029's exit 2: a stale or missing record is a designed hand-off (S1)."""
    code, out, err, fake = close(**given)

    assert (code, fake.calls) == (1, [])
    assert out.splitlines()[-1] == "seam=step-close code=1 reason=record next=seam-settle.sh 12 refactor-half"


def test_4029_no_refactor_pending_step_is_exit_2_before_any_inner_call(close):
    code, out, err, fake = close(ledger="# Plan\n\n- [x] %s\n- [ ] two ⟦criterion 2⟧\n" % STEP)

    assert (code, fake.calls) == (2, [])


def test_4029_an_uncovered_spec_line_stops_it_with_exit_1_before_any_inner_call(close):
    code, out, err, fake = close(half=REFACTOR_HALF % STEP + "uncovered_spec=empty input returns 0\n")

    assert (code, fake.calls) == (1, [])
    assert out.splitlines()[-1] == "stopped at 6 uncovered_spec=empty input returns 0"


def test_it_takes_the_step_green_sha_and_verdict_from_their_sources_and_rewrites_a_stale_record_4342(close):
    """SC1, replacing #4029's exit 2 on an earlier verdict: the ledger, git and .tdd/verify-refactor.log win."""
    later = "FLAGS: none\nVERDICT: PASS after a revise\n"
    (close.wt / ".tdd" / "verify-refactor.log").write_text(later)
    stale = REFACTOR_HALF.replace(GREEN_SHA, "e" * 40) % "one thing works ⟦added⟧ ⟦criterion 3⟧"
    code, out, err, fake = close(half=stale)

    record = (close.wt / ".tdd" / "issue-12-refactor-half").read_text()
    assert (code, fake.call("graded-changed.sh")[1]) == (0, (GREEN_SHA,))
    assert record == REFACTOR_HALF.replace(hashlib.sha256(VERDICT_LOG.encode()).hexdigest(),
                                           hashlib.sha256(later.encode()).hexdigest()) % STEP
    events = [json.loads(line) for line in (close.wt / ".tdd" / "events.jsonl").read_text().splitlines()]
    assert [e["key"] for e in events if e["event"] == "record-refreshed"] == ["step", "verdict_log", "green_sha"]


def test_4029_a_refactor_half_file_from_a_skipped_verify_names_no_verdict_log(close):
    code, out, err, fake = close(half=REFACTOR_HALF.replace(
        "verdict_log=" + hashlib.sha256(VERDICT_LOG.encode()).hexdigest(), "verdict_log=none") % STEP,
        missing=("verdict",))

    assert code == 0


def _named(fake):
    return [(c[0], c[1][:1]) for c in fake.calls]


def test_4029_it_checks_graded_units_and_rerecords_checks_the_tree_clears_commits_and_pushes_in_order(close):
    code, out, err, fake = close()

    assert _named(fake)[:10] == [
        ("git", ("log",)), ("graded-changed.sh", (GREEN_SHA,)), ("tests-frozen.sh", ("rerecord-refactored",)), ("git", ("status",)),
        ("clear-refactor-pending.sh", (".tdd/issue-12.md",)), ("git", ("add",)), ("git", ("commit",)),
        ("push-branch.sh", ()), ("event.sh", ("stage-end",)), ("stop-requested.sh", ())]
    assert fake.call("tests-frozen.sh")[1] == ("rerecord-refactored", ".tdd/issue-12.md", GREEN_SHA)
    assert fake.call("clear-refactor-pending.sh")[1] == (".tdd/issue-12.md", STEP)
    assert fake.call("git", "add")[1] == ("add", "-A")
    assert fake.call("git", "commit")[1] == ("commit", "-m", "chore: refactor verified for one thing works (#12)")
    assert all(c[2] == str(close.wt) for c in fake.calls)


class History(Fake):
    """A Fake whose `git log -1 --format=%H [-S <text>] -- <ledger>` answers from a ledger history, newest last, as
    git does: the newest commit that changed the ledger, or with -S the newest that changed <text>'s count in it."""

    def __init__(self, commits, **kw):
        super().__init__(**kw)
        self.commits = commits

    def __call__(self, name, *args, **kw):
        if os.path.basename(name) == "git" and args[:2] == ("log", "-1"):
            self.calls.append(("git", args, kw.get("cwd"), kw.get("env"), kw))
            text = args[args.index("-S") + 1] if "-S" in args else None
            for (sha, after), (_, before) in zip(reversed(self.commits), reversed([(None, "")] + self.commits[:-1]), strict=False):
                if (before.count(text) != after.count(text)) if text else before != after:
                    return 0, sha + "\n", ""
            return 0, "", ""
        return super().__call__(name, *args, **kw)


def test_4510_a_later_commit_adding_only_a_re_pin_step_leaves_the_step_green_commit_as_the_checked_sha(close):
    plan = "e" * 40
    repinned = LEDGER % STEP + "- [ ] ⟦diff-checked⟧ ⟦added⟧ ⟦criterion 1⟧ re-pin\n"
    fake = History([("a" * 40, "# Plan for #12\n\n- [ ] %s\n- [ ] two ⟦criterion 2⟧\n" % STEP),
                    (GREEN_SHA, LEDGER % STEP), (plan, repinned)])
    code, out, err, fake = close(fake=fake, ledger=repinned)

    assert fake.call("graded-changed.sh")[1] == (GREEN_SHA,)
    assert fake.call("tests-frozen.sh")[1] == ("rerecord-refactored", ".tdd/issue-12.md", GREEN_SHA)


def test_4510_a_later_green_tick_of_a_step_whose_text_ends_in_this_one_leaves_the_step_green_commit_as_the_checked_sha(
        close):
    """-S matches the whole step text after its checkbox, so "no one thing works" ticked later is not its green."""
    other = "no " + STEP
    green = LEDGER % STEP + "- [ ] %s\n" % other
    later = LEDGER % STEP + "- [x] %s ⟂ refactor pending\n" % other
    fake = History([("a" * 40, "# Plan for #12\n\n- [ ] %s\n- [ ] two ⟦criterion 2⟧\n- [ ] %s\n" % (STEP, other)),
                    (GREEN_SHA, green), ("e" * 40, later)])
    code, out, err, fake = close(fake=fake, ledger=later)

    assert fake.call("graded-changed.sh")[1] == (GREEN_SHA,), err


def test_4510_no_commit_that_changed_the_refactor_pending_line_stops_it_at_6_with_exit_2_before_any_check(close):
    fake = History([("a" * 40, "# Plan for #12\n\n- [ ] %s\n- [ ] two ⟦criterion 2⟧\n" % STEP)])
    code, out, err, fake = close(fake=fake)

    assert (code, out.splitlines()[-1]) == (2, "stopped at 6 no green commit for %s in .tdd/issue-12.md" % STEP), err
    assert "graded-changed.sh" not in fake.names()


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
    ("graded-changed.sh", None, 1), ("graded-changed.sh", None, 2), ("tests-frozen.sh", None, 1), ("tests-frozen.sh", None, 2),
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


def test_4481_an_already_ticked_criterion_still_marks_step_done_and_exits_0(close):
    code, out, err, fake = close(answers={("tick-issue-criterion.sh", None): (3, "")})

    assert code == 0, out
    assert ("event.sh", ("step-done",)) in [(c[0], c[1]) for c in fake.calls]


def test_4481_a_tick_issue_criterion_exit_1_stops_at_6_with_1_before_the_step_done_mark(close):
    code, out, err, fake = close(answers={("tick-issue-criterion.sh", None): (1, "")})

    assert (code, out.splitlines()[-1].split(" 12 ")[0]) == (1, "stopped at 6 tick-issue-criterion.sh")
    assert ("event.sh", ("step-done",)) not in [(c[0], c[1]) for c in fake.calls]


def test_4481_a_tick_issue_criterion_exit_2_stops_at_6_with_2_before_the_step_done_mark(close):
    code, out, err, fake = close(answers={("tick-issue-criterion.sh", None): (2, "")})

    assert (code, out.splitlines()[-1].split(" 12 ")[0]) == (2, "stopped at 6 tick-issue-criterion.sh")
    assert ("event.sh", ("step-done",)) not in [(c[0], c[1]) for c in fake.calls]


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


READ = ("git", "ledger-steps.sh", "gh")  # stdout read as a value


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

    expected = ["graded-changed.sh", "tests-frozen.sh", "clear-refactor-pending.sh", "push-branch.sh",
                "event.sh", "stop-requested.sh", "comment.sh", "criterion-finished.sh", "ledger-steps.sh",
                "tick-issue-criterion.sh", "next-unchecked.sh", "run-affordable.sh"]

    assert [name for name in expected if "$S/" + name not in section and name not in NAMED_ELSEWHERE] == []


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


def test_a_record_lacking_a_key_with_a_committed_source_gains_it_with_an_empty_old_value_4342(close):
    """SC1, SC2: the source's value is written into a record that lacks the key; the event's old value is empty."""
    lacking = "".join(line + "\n" for line in (REFACTOR_HALF % STEP).splitlines() if not line.startswith("verdict_log="))
    code, out, err, fake = close(half=lacking)

    verdict = hashlib.sha256(VERDICT_LOG.encode()).hexdigest()
    assert (code, (close.wt / ".tdd" / "issue-12-refactor-half").read_text()) == (0, lacking + "verdict_log=" + verdict + "\n")
    events = [json.loads(line) for line in (close.wt / ".tdd" / "events.jsonl").read_text().splitlines()]
    assert [(e["key"], e["old"]) for e in events if e["event"] == "record-refreshed"] == [("verdict_log", "")]


def test_4029_a_revised_pass_whose_log_flags_uncovered_spec_stops_it_though_the_record_lacks_the_line_4342(close):
    """#4029's case, restored under S1: the record is a cache, so the log's `uncovered-spec` FLAGS (their committed
    source) are written into it, and a revised PASS's uncovered behaviour is never skipped."""
    (close.wt / ".tdd" / "verify-refactor.log").write_text("FLAGS: uncovered-spec | a later verdict's flag\nVERDICT: PASS\n")
    code, out, err, fake = close()

    record = (close.wt / ".tdd" / "issue-12-refactor-half").read_text()
    assert (code, fake.calls) == (1, [])
    assert out.splitlines()[-1] == "stopped at 6 uncovered_spec=a later verdict's flag"
    assert record.endswith("uncovered_spec=a later verdict's flag\n")
    events = [json.loads(line) for line in (close.wt / ".tdd" / "events.jsonl").read_text().splitlines()]
    assert [(e["key"], e["old"], e["new"]) for e in events if e["event"] == "record-refreshed"][-1] == (
        "uncovered_spec", "", "a later verdict's flag")


def test_a_refactor_half_record_that_exists_but_cannot_be_read_is_exit_2_not_the_seam_4342(close):
    """SC4's split: only a missing record is the exit-1 seam; one that cannot be read (here a directory) is no answer."""
    (close.wt / ".tdd" / "issue-12-refactor-half").mkdir()
    code, out, err, fake = close()

    assert (code, fake.calls, "seam=" in out) == (2, [], False)


def test_a_refused_record_refreshed_event_stops_it_with_exit_2_and_leaves_the_record_4342(close, monkeypatch):
    """SC2: a rewrite whose event is refused stops the stage (exit 2) before the record is written."""
    monkeypatch.setattr(importlib.import_module("veri.step_close").fused_step.event, "mark", lambda *a, **k: 2)
    stale = REFACTOR_HALF % "one thing works ⟦added⟧ ⟦criterion 1⟧"
    code, out, err, fake = close(half=stale)

    assert (code, fake.calls) == (2, [])
    assert out.splitlines()[-1] == "stopped at step-close record-refreshed event refused"
    assert (close.wt / ".tdd" / "issue-12-refactor-half").read_text() == stale


def test_log_flags_the_record_was_settled_after_add_nothing_to_it_4342(close):
    """#4029's rule reads the log's flags only for a verdict the record was not settled after: a log an earlier step
    left behind, which refactor-half saw and wrote no `uncovered_spec=` for, does not stop the close."""
    left = "FLAGS: uncovered-spec | an earlier step's flag\nVERDICT: PASS\n"
    (close.wt / ".tdd" / "verify-refactor.log").write_text(left)
    settled = REFACTOR_HALF.replace(hashlib.sha256(VERDICT_LOG.encode()).hexdigest(),
                                    hashlib.sha256(left.encode()).hexdigest()) % STEP
    code, out, err, fake = close(half=settled)

    assert (code, (close.wt / ".tdd" / "issue-12-refactor-half").read_text()) == (0, settled)


def test_a_refused_record_refreshed_event_for_a_gained_uncovered_spec_line_stops_it_with_exit_2_4342(close, monkeypatch):
    """SC2 for #4029's flags: a gained `uncovered_spec=` line whose event is refused stops the stage (exit 2), the
    line not written."""
    event = importlib.import_module("veri.step_close").fused_step.event
    mark = event.mark
    monkeypatch.setattr(event, "mark", lambda wt, context, name, fields=(), **kw: 2 if "key=uncovered_spec" in fields
                        else mark(wt, context, name, fields, **kw))
    (close.wt / ".tdd" / "verify-refactor.log").write_text("FLAGS: uncovered-spec | a later verdict's flag\nVERDICT: PASS\n")
    code, out, err, fake = close()

    assert (code, fake.calls) == (2, [])
    assert out.splitlines()[-1] == "stopped at step-close record-refreshed event refused"
    assert "uncovered_spec=" not in (close.wt / ".tdd" / "issue-12-refactor-half").read_text()


def test_a_hand_revised_pass_settled_by_seam_settle_plans_its_uncovered_spec_flags_before_any_close_4342(
        close, run_cli, tmp_path):
    """#4029's hand path (RF74): verify-refactor REJECT, a revise, then a PASS whose log flags uncovered-spec, all by
    hand. step-close stops at the seam, `seam-settle.sh <n> refactor-half` writes the record from the log as it stands,
    and the re-run step-close stops on that flag (exit 1) as the automatic path's record makes it, never ticking the
    step done with the flag unplanned."""
    (close.wt / ".tdd" / "verify-refactor.log").write_text("FLAGS: uncovered-spec | a revised verdict's flag\nVERDICT: PASS\n")
    code, out, err, fake = close(missing=("refactor-half",))
    assert (code, out.splitlines()[-1]) == (1, "seam=step-close code=1 reason=record next=seam-settle.sh 12 refactor-half")

    settled = run_cli(importlib.import_module("veri.seam_settle"), ["12", "refactor-half"], cwd=str(tmp_path))
    assert settled[0] == 0
    code, out, err, fake = close()

    assert (code, fake.calls) == (1, [])
    assert out.splitlines()[-1] == "stopped at 6 uncovered_spec=a revised verdict's flag"



EARLIER_PASS = {"event": "verdict", "phase": "refactor", "step": "an earlier step", "verdict": "PASS"}


@pytest.mark.parametrize("journal, flagged", [
    ([EARLIER_PASS, {"event": "verify-refactor-skipped", "step": STEP, "reason": "nothing-landed"}], False),
    ([{"event": "verify-refactor-skipped", "step": STEP, "reason": "switched-off"}, EARLIER_PASS], False),
    ([{"event": "verify-refactor-skipped", "step": STEP, "reason": "nothing-landed"},
      {"event": "verdict", "phase": "refactor", "step": STEP, "verdict": "PASS"}], True),
    ([{"event": "verify-refactor-skipped", "step": STEP, "reason": "nothing-landed"},
      {"event": "verdict", "phase": "green", "step": STEP, "verdict": "PASS"}], False),
], ids=["nothing-landed", "switched-off", "verified-after-the-skip", "a-green-verdict-after-the-skip"])
def test_a_hand_refactor_whose_verify_was_skipped_settles_no_flag_of_an_earlier_steps_log_and_closes_4342(
        close, run_cli, tmp_path, journal, flagged):
    """A hand refactor that skipped its verify (the `verify-refactor-skipped` event for the open step, SKILL.md
    Refactor 5, with no refactor `verdict` for the step after it) leaves `.tdd/verify-refactor.log` an earlier step's:
    `seam-settle.sh <n> refactor-half` names its hash but records none of its `uncovered_spec=` flags, as
    refactor-half.sh's own skip does, so step-close closes the step rather than stopping on another step's flag. A
    refactor verdict for the step after the skip makes the log the step's, its flags recorded and stopping the close."""
    left = "FLAGS: uncovered-spec | the log's flag\nVERDICT: PASS\n"
    (close.wt / ".tdd" / "verify-refactor.log").write_text(left)
    (close.wt / ".tdd" / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in journal))
    code, out, err, fake = close(missing=("refactor-half",))
    assert (code, out.splitlines()[-1]) == (1, "seam=step-close code=1 reason=record next=seam-settle.sh 12 refactor-half")

    settled = run_cli(importlib.import_module("veri.seam_settle"), ["12", "refactor-half"], cwd=str(tmp_path))
    record = (close.wt / ".tdd" / "issue-12-refactor-half").read_text()
    assert (settled[0], "uncovered_spec=the log's flag\n" in record) == (0, flagged)
    assert "verdict_log=%s\n" % hashlib.sha256(left.encode()).hexdigest() in record

    code, out, err, fake = close()

    assert (code, out.splitlines()[-1] == "stopped at 6 uncovered_spec=the log's flag") == (int(flagged), flagged)


def _queued(tmp_path):
    """The (type, issue, criterion) of each entry in the main tree's GitHub queue, in file order."""
    with open(tmp_path / ".tdd" / "github-queue") as f:
        return [(e["type"], e["issue"], e["criterion"]) for e in map(json.loads, f.read().splitlines())]


def test_4803_with_the_outage_file_each_finished_criterion_is_queued_as_a_tick_without_reading_the_body(close, tmp_path):
    (tmp_path / ".tdd" / "github-outage").write_text("")

    code, out, err, fake = close(step="one thing works ⟦criterion 1⟧ ⟦criterion 3⟧")

    assert code == 0, out
    assert not {"gh", "tick-issue-criterion.sh"} & set(fake.names())
    assert _queued(tmp_path) == [("tick", "12", 1), ("tick", "12", 3)]
    assert fake.call("event.sh", "step-done")


def test_4803_a_body_read_that_gets_no_answer_during_an_incident_queues_the_tick_and_exits_0(
        close, tmp_path, monkeypatch):
    monkeypatch.setattr(importlib.import_module("veri.github_queue"), "incident", lambda: True)

    code, out, err, fake = close(answers={("gh", None): (2, "")})

    assert code == 0, out
    assert "tick-issue-criterion.sh" not in fake.names()
    assert _queued(tmp_path) == [("tick", "12", 1)]


def test_4803_a_body_read_that_gets_no_answer_with_no_incident_still_stops_at_6_with_2(close, tmp_path, monkeypatch):
    monkeypatch.setattr(importlib.import_module("veri.github_queue"), "incident", lambda: False)

    code, out, err, fake = close(answers={("gh", None): (2, "")})

    assert (code, fake.names()[-1]) == (2, "gh")
    assert not (tmp_path / ".tdd" / "github-queue").exists()
