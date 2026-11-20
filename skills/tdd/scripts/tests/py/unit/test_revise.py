"""In-process cases for veri/revise.py, the module revise.sh is a shim over (PRD 038.9, #4433)."""
import importlib
import json
import os

import pytest

STEP = "one thing works ⟦criterion 1⟧"
LEDGER = "# Plan for #12\n\n- [x] zero ⟦criterion 1⟧\n- [ ] %s\n- [ ] two ⟦criterion 2⟧\n"
RED_HALF = ("step=%s\ntest_path=tests/test_a.py\ntarget_test=tests/test_a.py::test_one\n"
            "red_test_id=tests/test_a.py::test_one\nagainst_unmodified=FAILS\n")
REASON = "VERDICT: REJECT\nthe green hardcodes the answer\n"
BRANCH_BASE = "abc1234"


class Fake:
    """A run_script stand-in: records (basename, args, cwd, env, kw) and answers from <answers>, keyed by
    (basename, first argument or None) -> (code, stdout)."""

    def __init__(self, answers=None, report="OUTCOME: REWRITTEN\nAGAINST_UNMODIFIED: N/A\n", cost="1.00\n"):
        self.answers, self.calls, self.report, self.cost = dict(answers or {}), [], report, cost

    def __call__(self, name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        self.calls.append((base, args, cwd, env, kw))
        for (script, first), (code, out) in self.answers.items():
            if base == script and (first is None or args[:1] == (first,)):
                return code, out, ""
        if base == "extract-result.sh":
            return 0, self.report, ""
        if base == "stop-requested.sh":
            return 3, "", ""
        if base == "step-cost.sh":
            return 0, self.cost, ""
        if base == "step-budget.sh":
            return 0, "12\n120\n", ""
        if base == "same-reject.sh":
            return 1, "", ""
        return 0, "", ""

    def names(self):
        return [c[0] for c in self.calls]

    def call(self, base, first=None):
        return next(c for c in self.calls if c[0] == base and (first is None or c[1][:1] == (first,)))

    def launched(self):
        return [c[1][1] for c in self.calls if c[0] == "detach-leaf.sh"]


@pytest.fixture
def revise(monkeypatch, run_cli, tmp_path):
    """revise(answers=None, fake=None, missing=(), argv=("12", "green")) runs revise for issue 12 from the main tree,
    the run's worktree at .tdd/wt/12; returns (code, stdout, stderr, fake)."""
    fused = importlib.import_module("veri.fused")
    module = importlib.import_module("veri.revise")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)

    def go(answers=None, fake=None, missing=(), argv=("12", "green")):
        files = {"branch_base": (wt / ".tdd" / "issue-12-branch-base", BRANCH_BASE + "\n"),
                 "preflight": (wt / ".tdd" / "issue-12-preflight", "worktree=%s\nfast_cmd=make unit\n" % wt),
                 "ledger": (wt / ".tdd" / "issue-12.md", LEDGER % STEP),
                 "spec": (wt / ".tdd" / "issue-12-spec.md", "# spec\n"),
                 "red-half": (wt / ".tdd" / "issue-12-red-half", RED_HALF % STEP),
                 "reason": (wt / ".tdd" / "verify-green.reason", REASON),
                 "revised": (wt / ".tdd" / "revise-green-1.out", "the revise-green-1 report\n"),
                 "revised-2": (wt / ".tdd" / "revise-green-2.out", "the revise-green-2 report\n")}
        for key, (path, text) in files.items():
            if key not in missing and not path.exists():
                path.write_text(text)
        fake = fake or Fake(answers)
        monkeypatch.setattr(fused, "run_script", fake)
        code, out, err = run_cli(module, list(argv), cwd=str(tmp_path))
        return code, out, err, fake

    go.wt = wt
    return go


def _short(args):
    return tuple(os.path.basename(a) if a.endswith(".sh") else a for a in args)


def test_green_attempt_1_builds_the_prompt_posts_the_revise_comment_marks_it_and_launches_revise_green_1_exiting_3(
        revise):
    """PRD 038.9 criteria 1, 3, 12: REVISE.md sub-steps 2 and 3 for attempt 1 of green."""
    code, out, err, fake = revise(answers={("wait-leaf.sh", "revise-green-1"): (3, "")})

    assert (code, out.splitlines()[-1]) == (3, "waiting on revise-green-1")
    assert (revise.wt / ".tdd" / "verify-green-1.reason").read_text() == REASON
    assert [(c[0], c[1]) for c in fake.calls[:2]] == [
        ("build-develop-prompt.sh", ("revise", "green", ".tdd/issue-12-spec.md", STEP, "make unit",
                                     ".tdd/verify-green.reason", "make unit")),
        ("comment.sh", ("12", "revise", "green", "1"))]
    assert fake.calls[0][4]["out"] == ".tdd/revise-green-1.prompt"
    mark = fake.call("event.sh")
    assert mark[1] == ("revise", "budget=2")
    assert (mark[3]["VERI_PHASE"], mark[3]["VERI_ATTEMPT"], mark[3]["VERI_ACTOR"], mark[3]["VERI_STEP"]) == (
        "green", "1", "conductor", STEP)
    launch = fake.call("detach-leaf.sh")
    assert _short(launch[1]) == ("supervise.sh", "revise-green-1", "run-leaf.sh", ".tdd/revise-green-1.prompt",
                                 "--permission-mode", "bypassPermissions")
    assert (launch[3]["VERI_TEST_CMD"], launch[3]["VERI_ISSUE"], launch[3]["VERI_STEP"]) == ("make unit", "12", STEP)
    assert (launch[4]["out"], launch[4]["err"]) == (".tdd/revise-green-1.out", ".tdd/revise-green-1.err")
    assert fake.names()[-1] == "wait-leaf.sh"
    record = json.loads((revise.wt / ".tdd" / "issue-12-revise-wait").read_text())
    assert (record["at"], record["values"]["phase"], record["values"]["k"]) == ("revise-green-1", "green", 1)


@pytest.mark.parametrize("argv, missing", [(("12",), ()), (("12", "blue"), ()), (("x", "green"), ()),
                                           (("12", "green"), ("preflight",))])
def test_a_bad_phase_or_argument_or_a_missing_preflight_is_exit_2_before_any_inner_call(revise, argv, missing):
    """PRD 038.9 criterion 12."""
    code, out, err, fake = revise(argv=argv, missing=missing)

    assert (code, fake.calls) == (2, [])
    assert ("usage: revise.sh <n> <phase>" in err) == (missing == ())


def test_called_again_it_only_waits_then_checks_cost_and_frozen_tests_and_launches_verdict_green_exiting_3(revise):
    """PRD 038.9 criteria 1, 3, 13: REVISE.md sub-steps 3-5 up to the re-verify, with green-half's run-verdict.sh
    arguments and the run's recorded branch base."""
    first = revise(answers={("wait-leaf.sh", "revise-green-1"): (3, "")})[0]
    code, out, err, fake = revise(answers={("wait-leaf.sh", "verdict-green"): (3, "")})

    assert (first, code, out.splitlines()[-1]) == (3, 3, "waiting on verdict-green")
    assert [(c[0], c[1]) for c in fake.calls if c[0] != "extract-result.sh"][:4] == [
        ("wait-leaf.sh", ("revise-green-1",)), ("step-cost.sh", (STEP,)), ("step-budget.sh", ()),
        ("tests-frozen.sh", ("check", "--step", STEP))]
    assert fake.launched() == ["verdict-green"]
    launch = fake.call("detach-leaf.sh")
    assert _short(launch[1]) == ("supervise.sh", "verdict-green", "run-verdict.sh", "--step", STEP, "--fast-cmd",
                                 "make unit", "--branch-base", BRANCH_BASE, "green", ".tdd/issue-12-spec.md",
                                 "tests/test_a.py", "tests/test_a.py::test_one")
    assert (launch[3]["VERI_TEST_CMD"], launch[4]["out"], launch[4]["err"]) == (
        "make unit", ".tdd/verify-green.reason", ".tdd/verify-green.err")
    assert fake.calls[-1][:2] == ("wait-leaf.sh", ("verdict-green",))
    record = json.loads((revise.wt / ".tdd" / "issue-12-revise-wait").read_text())
    assert (record["at"], record["values"]["k"]) == ("verdict-green", 1)


def test_4482_green_called_again_runs_check_earlier_with_no_except_after_check_and_before_launching_verdict_green(revise):
    revise(answers={("wait-leaf.sh", "revise-green-1"): (3, "")})
    code, out, err, fake = revise(answers={("wait-leaf.sh", "verdict-green"): (3, "")})

    steps = [(c[0], c[1][:1]) for c in fake.calls if c[0] in ("tests-frozen.sh", "detach-leaf.sh")]
    assert code == 3
    assert [s[0] if s[0] == "detach-leaf.sh" else s[1][0] for s in steps] == [
        "check", "check-earlier", "detach-leaf.sh"]
    assert fake.call("tests-frozen.sh", "check-earlier")[1] == (
        "check-earlier", ".tdd/issue-12.md", "--step", STEP)


def test_4482_green_on_a_replaces_case_step_passes_check_earlier_one_except_per_replaced_case(revise):
    step = "port it: replaces 'case one' and 'case two' in tests/py/test_x.py ⟦replaces-case⟧ ⟦criterion 2⟧"
    (revise.wt / ".tdd" / "issue-12.md").write_text(LEDGER % step)
    (revise.wt / ".tdd" / "issue-12-red-half").write_text(RED_HALF % step)
    revise(answers={("wait-leaf.sh", "revise-green-1"): (3, "")})
    code, out, err, fake = revise(answers={("wait-leaf.sh", "verdict-green"): (3, "")})

    assert code == 3
    assert fake.call("tests-frozen.sh", "check-earlier")[1] == (
        "check-earlier", ".tdd/issue-12.md", "--step", step, "--except", "case one", "--except", "case two")


def test_4482_green_on_a_replaces_case_step_whose_cases_cannot_be_parsed_passes_check_earlier_no_except(revise):
    step = "port it, naming no case to replace ⟦replaces-case⟧ ⟦criterion 2⟧"
    (revise.wt / ".tdd" / "issue-12.md").write_text(LEDGER % step)
    (revise.wt / ".tdd" / "issue-12-red-half").write_text(RED_HALF % step)
    revise(answers={("wait-leaf.sh", "revise-green-1"): (3, "")})
    code, out, err, fake = revise(answers={("wait-leaf.sh", "verdict-green"): (3, "")})

    assert code == 3
    assert fake.call("tests-frozen.sh", "check-earlier")[1] == (
        "check-earlier", ".tdd/issue-12.md", "--step", step)


def test_4482_green_called_again_runs_check_earlier_in_the_worktree_where_the_relative_ledger_path_resolves(revise):
    revise(answers={("wait-leaf.sh", "revise-green-1"): (3, "")})
    code, out, err, fake = revise(answers={("wait-leaf.sh", "verdict-green"): (3, "")})

    assert code == 3
    assert fake.call("tests-frozen.sh", "check-earlier")[2] == str(revise.wt)
    assert fake.call("tests-frozen.sh", "check")[2] == str(revise.wt)


def test_on_a_revised_pass_it_posts_verify_revised_resaves_green_halfs_wait_at_verdict_green_and_exits_0(revise):
    """PRD 038.9 criterion 5: the stage, called again, finishes as after its own PASS."""
    rejected = revise.wt / ".tdd" / "issue-12-green-half-rejected-wait"
    rejected.write_text(json.dumps({"conductor": None, "at": "verdict-green",
                                    "values": {"test_path": "tests/test_a.py",
                                               "target_test": "tests/test_a.py::test_one"}, "step": STEP}))
    code, out, err, fake = revise()

    assert code == 0
    assert (fake.calls[-1][0], fake.calls[-1][1]) == ("comment.sh", ("12", "verify-revised", "green"))
    record = json.loads((revise.wt / ".tdd" / "issue-12-green-half-wait").read_text())
    assert (record["at"], record["values"]) == (
        "verdict-green", {"test_path": "tests/test_a.py", "target_test": "tests/test_a.py::test_one",
                          "revised": True})
    assert not rejected.exists()
    assert not (revise.wt / ".tdd" / "issue-12-revise-wait").exists()


@pytest.mark.parametrize("same", [1, 2, 0])
def test_a_reverify_reject_spends_attempt_k_and_goes_on_to_k_plus_1_unless_same_reject_says_it_repeats(revise, same):
    """PRD 038.9 criteria 4 and 6: REVISE.md sub-step 1 for attempt 2; same-reject.sh exit 0 stops with exit 1."""
    code, out, err, fake = revise(answers={("wait-leaf.sh", "verdict-green"): (1, ""),
                                           ("wait-leaf.sh", "revise-green-2"): (3, ""),
                                           ("same-reject.sh", None): (same, "")})

    assert fake.call("same-reject.sh")[1] == (".tdd/verify-green-1.reason", ".tdd/verify-green.reason")
    comments = [c[1] for c in fake.calls if c[0] == "comment.sh"]
    if same:
        assert (code, out.splitlines()[-1]) == (3, "waiting on revise-green-2")
        assert comments == [("12", "revise", "green", "1"), ("12", "revise", "green", "2")]
        assert [c[3]["VERI_ATTEMPT"] for c in fake.calls if c[0] == "event.sh"] == ["1", "2"]
        assert fake.launched() == ["revise-green-1", "verdict-green", "revise-green-2"]
    else:
        assert (code, out.splitlines()[-1]) == (
            1, "stopped at 1 same-reject.sh .tdd/verify-green-1.reason .tdd/verify-green.reason exit 0")
        assert (comments, fake.launched()) == ([("12", "revise", "green", "1")], ["revise-green-1", "verdict-green"])


def test_once_revise_budget_attempts_are_spent_it_stops_with_exit_1_naming_the_budget_launching_nothing_more(
        revise, monkeypatch):
    """PRD 038.9 criteria 6 and 12: REVISE_BUDGET read through tunables; never a develop-exhausted leaf."""
    monkeypatch.setenv("REVISE_BUDGET", "1")
    code, out, err, fake = revise(answers={("wait-leaf.sh", "verdict-green"): (1, "")})

    assert (code, out.splitlines()[-1]) == (1, "stopped at budget REVISE_BUDGET=1 attempts spent")
    assert [c[1] for c in fake.calls if c[0] == "comment.sh"] == [("12", "revise", "green", "1")]
    assert fake.launched() == ["revise-green-1", "verdict-green"]
    assert [c[1] for c in fake.calls if c[0] == "build-develop-prompt.sh"][1:] == []


def test_the_attempt_is_read_from_the_open_steps_revise_events_for_the_phase_so_a_resumed_call_goes_on_at_the_next(
        revise):
    """PRD 038.9 criterion 2: one earlier `revise` mark of this step's green makes this call attempt 2; marks of
    another phase, another step or another actor do not count."""
    def mark(step, phase, actor="conductor"):
        return json.dumps({"event": "revise", "actor": actor, "step": step, "phase": phase, "attempt": "1",
                           "budget": "2"}) + "\n"
    (revise.wt / ".tdd" / "events.jsonl").write_text(
        mark(STEP, "green") + mark(STEP, "red") + mark("zero ⟦criterion 1⟧", "green") + mark(STEP, "green", "leaf"))
    code, out, err, fake = revise(answers={("wait-leaf.sh", "revise-green-2"): (3, "")})

    assert (code, out.splitlines()[-1]) == (3, "waiting on revise-green-2")
    assert fake.call("comment.sh")[1] == ("12", "revise", "green", "2")
    assert fake.call("same-reject.sh")[1] == (".tdd/verify-green-1.reason", ".tdd/verify-green.reason")


@pytest.mark.parametrize("frozen", [1, 2])
def test_a_tests_frozen_check_exit_1_spends_the_attempt_without_a_verifier_and_its_exit_2_is_exit_2(revise, frozen):
    """PRD 038.9 criteria 4 and 8: REVISE.md sub-step 4's green check."""
    code, out, err, fake = revise(answers={("tests-frozen.sh", "check"): (frozen, "tests/test_a.py\n"),
                                           ("wait-leaf.sh", "revise-green-2"): (3, "")})

    assert "verdict-green" not in fake.launched()
    if frozen == 1:
        assert (code, fake.launched()) == (3, ["revise-green-1", "revise-green-2"])
        assert "tests/test_a.py" in (revise.wt / ".tdd" / "verify-green.reason").read_text()
        assert (revise.wt / ".tdd" / "verify-green-2.reason").read_text() == (
            revise.wt / ".tdd" / "verify-green.reason").read_text()
    else:
        assert (code, out.splitlines()[-1]) == (2, "stopped at 4 tests-frozen.sh check --step %s exit 2" % STEP)


def test_with_the_phase_switched_off_it_marks_the_skip_writes_skipped_and_goes_on_as_on_a_pass(revise):
    """PRD 038.9 criterion 4 (ADR-0033): no verifier; the stage's record is re-saved past its verdict (at `skipped`,
    its verify comment `posted`), since wait-leaf.sh reads a `skipped` exit file as 2 and the stage's own switched-off
    branch waits on nothing."""
    (revise.wt / ".tdd" / "issue-12-skip-verify").write_text("green\n")
    code, out, err, fake = revise()

    assert (code, fake.launched()) == (0, ["revise-green-1"])
    assert fake.call("event.sh", "verify-green-skipped")[1] == ("verify-green-skipped", "reason=switched-off")
    assert (revise.wt / ".tdd" / "verdict-green.exit").read_text().strip() == "skipped"
    assert (fake.calls[-1][0], fake.calls[-1][1]) == ("comment.sh", ("12", "verify-revised", "green"))
    record = json.loads((revise.wt / ".tdd" / "issue-12-green-half-wait").read_text())
    assert (record["at"], record["values"]) == (
        "skipped", {"test_path": "tests/test_a.py", "target_test": "tests/test_a.py::test_one", "posted": True,
                    "revised": True})


RED_REPORT = "TEST_PATH: tests/test_b.py\nTARGET_TEST: tests/test_b.py::test_two\nAGAINST_UNMODIFIED: FAILS\n" \
             "OUTCOME: REWRITTEN\n"
RED_VALUES = {"refresh": 0, "test_path": "tests/test_a.py", "target_test": "tests/test_a.py::test_one"}


def _red(revise):
    """The files a rejected red leaves: red-half's rejected record, the reports and the reason."""
    (revise.wt / ".tdd" / "issue-12-red-half-rejected-wait").write_text(
        json.dumps({"conductor": None, "at": "verdict-red", "values": RED_VALUES, "step": STEP}))
    for name in ("develop-red.out", "revise-red-1.out"):
        (revise.wt / ".tdd" / name).write_text("the %s report\n" % name)
    (revise.wt / ".tdd" / "verify-red.reason").write_text(REASON)


def test_red_restores_production_gates_the_prediction_and_on_pass_records_and_resaves_red_halfs_wait(revise):
    """PRD 038.9 criteria 1, 4, 5: REVISE.md sub-steps 3-5 for red, red-half's record not needed."""
    _red(revise)
    code, out, err, fake = revise(fake=Fake({("red-divergence.sh", None): (3, "")}, report=RED_REPORT),
                                  argv=("12", "red"), missing=("red-half",))

    names = fake.names()
    assert code == 0, out
    assert fake.call("restore-production.sh")[1] == ("tests/test_b.py",)
    assert names.index("restore-production.sh") < names.index("detach-leaf.sh")
    gate = fake.call("red-divergence.sh")
    assert (gate[1], gate[4]["stdin"], gate[4]["out"]) == (
        (".tdd/red-prediction.md", ".tdd/red-run-output.txt"), "the revise-red-1.out report\n",
        ".tdd/verify-red.reason")
    assert fake.launched() == ["revise-red-1", "verdict-red"]
    verdict = [c for c in fake.calls if c[0] == "detach-leaf.sh"][1]
    assert _short(verdict[1])[-4:] == ("red", ".tdd/issue-12-spec.md", "tests/test_b.py", "tests/test_b.py::test_two")
    tail = [(c[0], c[1]) for c in fake.calls[names.index("wait-leaf.sh", names.index("red-divergence.sh")) + 1:]]
    assert tail == [("tests-frozen.sh", ("record", "--step", STEP, "--red-case", "tests/test_b.py::test_two",
                                         "tests/test_b.py")),
                    ("red-setup.sh", ("record", "12")), ("comment.sh", ("12", "verify-revised", "red"))]
    assert fake.call("red-setup.sh")[4]["stdin"] == "the revise-red-1.out report\n"
    record = json.loads((revise.wt / ".tdd" / "issue-12-red-half-wait").read_text())
    assert (record["at"], record["values"]) == ("verdict-red", {
        **RED_VALUES, "test_path": "tests/test_b.py", "target_test": "tests/test_b.py::test_two", "revised": True})
    assert not (revise.wt / ".tdd" / "issue-12-red-half-rejected-wait").exists()


@pytest.mark.parametrize("gate", [0, 1, 2])
def test_a_red_prediction_gate_exit_0_1_or_2_spends_the_attempt_without_a_verifier(revise, gate):
    """PRD 038.9 criterion 4: REVISE.md sub-step 4; only exit 3 (matched) re-verifies."""
    _red(revise)
    code, out, err, fake = revise(fake=Fake({("red-divergence.sh", None): (gate, ""),
                                             ("wait-leaf.sh", "revise-red-2"): (3, "")}, report=RED_REPORT),
                                  argv=("12", "red"), missing=("red-half",))

    assert (code, fake.launched()) == (3, ["revise-red-1", "revise-red-2"])
    reason = (revise.wt / ".tdd" / "verify-red.reason").read_text()
    if gate == 1:
        assert reason == "REASON: prediction not written before the run\n"
    if gate == 2:
        assert reason == "REASON: the revised red carries no readable PREDICTION: line\n"


@pytest.mark.parametrize("phase, line", [("green", "OUTCOME: IMPOSSIBLE"), ("red", "OUTCOME: IMPOSSIBLE"),
                                         ("green", "WRONG_TEST: the test asserts x"),
                                         ("green", "SUPERSEDED: tests/test_c.py::test_c"),
                                         ("red", "AGAINST_UNMODIFIED: PASSES")])
def test_it_stops_with_exit_1_naming_the_report_line_that_routes_the_revise_elsewhere(revise, phase, line):
    """PRD 038.9 criterion 7 (RVS7): those answers are the conductor's routes, never another attempt or verifier."""
    _red(revise)
    report = (RED_REPORT if phase == "red" else "OUTCOME: REWRITTEN\nAGAINST_UNMODIFIED: N/A\n") + line + "\n"
    code, out, err, fake = revise(fake=Fake({("red-divergence.sh", None): (3, "")}, report=report),
                                  argv=("12", phase))

    assert (code, out.splitlines()[-1]) == (1, "stopped at 3 " + line)
    assert fake.launched() == ["revise-%s-1" % phase]


GREEN_SHA = "c" * 40
REF_VALUES = {"green_sha": GREEN_SHA, "budget": 3, "touched": "src/a.py", "test_path": "tests/test_a.py",
              "ran": True, "count": 1, "stopped": "nothing-left", "candidates": [], "flags": []}


def _refactor(revise):
    """The files a rejected refactor leaves: the step refactor-pending, refactor-half's rejected record, the report
    and the reason."""
    (revise.wt / ".tdd" / "issue-12.md").write_text("# Plan for #12\n\n- [x] %s ⟂ refactor pending\n"
                                                    "- [ ] two ⟦criterion 2⟧\n" % STEP)
    (revise.wt / ".tdd" / "issue-12-refactor-half-rejected-wait").write_text(
        json.dumps({"conductor": None, "at": "verdict-refactor", "values": REF_VALUES, "step": STEP}))
    (revise.wt / ".tdd" / "revise-refactor-1.out").write_text("the revise-refactor-1 report\n")
    (revise.wt / ".tdd" / "verify-refactor.reason").write_text(REASON)


def test_refactor_runs_no_step_cost_reverifies_with_refactor_halfs_green_sha_and_on_pass_resaves_its_wait(revise):
    """PRD 038.9 criteria 1 and 5: refactor-half's values come back from its rejected record (D1)."""
    _refactor(revise)
    code, out, err, fake = revise(argv=("12", "refactor"))

    assert code == 0, out
    assert not {"step-cost.sh", "tests-frozen.sh"} & set(fake.names())
    assert fake.call("build-develop-prompt.sh")[1][:4] == ("revise", "refactor", ".tdd/issue-12-spec.md", STEP)
    verdict = [c for c in fake.calls if c[0] == "detach-leaf.sh"][1]
    assert _short(verdict[1])[-4:] == ("refactor", ".tdd/issue-12-spec.md", "tests/test_a.py", GREEN_SHA)
    assert (fake.calls[-1][0], fake.calls[-1][1]) == ("comment.sh", ("12", "verify-revised", "refactor"))
    record = json.loads((revise.wt / ".tdd" / "issue-12-refactor-half-wait").read_text())
    assert (record["at"], record["values"]) == ("verdict-refactor", dict(REF_VALUES, revised=True))
    assert not (revise.wt / ".tdd" / "issue-12-refactor-half-rejected-wait").exists()


def test_refactor_switched_off_resaves_refactor_halfs_wait_past_its_verify_with_the_comment_posted(revise):
    """PRD 038.9 criterion 4: refactor-half re-entered at `skipped` goes straight to its finish, posting no second
    verify-refactor comment (`posted`) and rerunning no check."""
    _refactor(revise)
    (revise.wt / ".tdd" / "issue-12-skip-verify").write_text("refactor\n")
    code, out, err, fake = revise(argv=("12", "refactor"))

    assert (code, fake.launched()) == (0, ["revise-refactor-1"])
    record = json.loads((revise.wt / ".tdd" / "issue-12-refactor-half-wait").read_text())
    assert (record["at"], record["values"]) == ("skipped", dict(REF_VALUES, posted=True, revised=True))


@pytest.mark.parametrize("answer, last", [
    (("build-develop-prompt.sh", None), "build-develop-prompt.sh"),
    (("detach-leaf.sh", None), "detach-leaf.sh"),
    (("wait-leaf.sh", "revise-green-1"), "wait-leaf.sh"),
    (("wait-leaf.sh", "verdict-green"), "wait-leaf.sh")],
    ids=["prompt", "launch", "supervisor", "verifier"])
def test_a_prompt_supervisor_or_verifier_exit_2_is_exit_2_with_nothing_after_it(revise, answer, last):
    """PRD 038.9 criterion 8: no answer could be obtained; a prompt's 2 posts no comment, writes no mark."""
    code, out, err, fake = revise(answers={answer: (2, "")})

    assert (code, fake.names()[-1]) == (2, last)
    if answer[0] == "build-develop-prompt.sh":
        assert not {"comment.sh", "event.sh", "detach-leaf.sh"} & set(fake.names())


@pytest.mark.parametrize("gate, marked", [(0, True), (1, False), (2, True)])
def test_a_diverged_or_unreadable_red_prediction_writes_the_mark_and_preserves_the_attempt_best_effort(
        revise, gate, marked):
    """PRD 038.9 RVS4: REVISE.md sub-step 4's exit 0 or 2 (a PREDICTION: DIVERGED report gates 0) is marked
    `prediction-diverged` and its tree preserved; preserve-attempt.sh's failure goes on."""
    _red(revise)
    code, out, err, fake = revise(fake=Fake({("red-divergence.sh", None): (gate, ""),
                                             ("preserve-attempt.sh", None): (1, ""),
                                             ("wait-leaf.sh", "revise-red-2"): (3, "")}, report=RED_REPORT),
                                  argv=("12", "red"), missing=("red-half",))

    marks = [c for c in fake.calls if c[0] == "event.sh" and c[1][:1] == ("prediction-diverged",)]
    preserved = [c[1] for c in fake.calls if c[0] == "preserve-attempt.sh"]
    assert (code, fake.launched()) == (3, ["revise-red-1", "revise-red-2"])
    assert (len(marks), preserved) == ((1, [("12", STEP, "revise-red", "1", "prediction-diverged")]) if marked
                                       else (0, []))
    if marked:
        assert (marks[0][1], marks[0][3]["VERI_ACTOR"], marks[0][3]["VERI_STEP"]) == (
            ("prediction-diverged",), "conductor", STEP)


@pytest.mark.parametrize("phase", ["green", "refactor"])
def test_green_and_refactor_without_a_red_half_record_for_the_step_stop_on_the_record_seam_line_with_exit_1(
        revise, phase):
    """PRD 038.9 criterion 11 (PRD 038.1 SC4): the record is a designed hand-off, never an exit 2."""
    _refactor(revise) if phase == "refactor" else None
    code, out, err, fake = revise(argv=("12", phase), missing=("red-half",))

    assert (code, fake.calls) == (1, [])
    assert out.splitlines()[-1] == ("seam=revise code=1 reason=record next=seam-settle.sh 12 red-half test_path=… "
                                    "target_test=…")


@pytest.mark.parametrize("phase", ["green", "red"])
def test_it_prints_one_line_per_call_and_never_a_calls_output_or_the_reason_file(revise, phase):
    """PRD 038.9 criterion 14: the leaf's, the suite's (tests-frozen.sh's file list) and the reason file stay out."""
    class Marked(Fake):
        def __call__(self, name, *args, **kw):
            code, out, err = super().__call__(name, *args, **kw)
            if os.path.basename(name) in ("extract-result.sh", "step-cost.sh", "step-budget.sh"):
                return code, out, err
            return code, "OUT<%d>\n" % len(self.calls) + out, err

    _red(revise)
    fake = Marked({("red-divergence.sh", None): (3, "")}, report=RED_REPORT if phase == "red" else
                  "OUTCOME: REWRITTEN\nAGAINST_UNMODIFIED: N/A\n")
    code, out, err, fake = revise(fake=fake, argv=("12", phase))

    lines = out.splitlines()
    assert code == 0
    assert not [line for line in lines if "OUT<" in line or "REJECT" in line or "hardcodes" in line]
    assert len(lines) == len(fake.calls)
    assert all(line.rsplit(" exit ", 1)[-1].isdigit() for line in lines)


# Inner calls REVISE.md does not name, each by name with its reason.
NAMED_ELSEWHERE = {
    "stop-requested.sh": "FC8: the stop check *Launching a leaf* states before every leaf, which REVISE.md defers to",
    "step-budget.sh": "RH4: the budget *The step's cost check* weighs step-cost.sh's figure against",
    "extract-result.sh": "FC2: *Launching a leaf* reads a leaf's report only through it",
}


def test_every_inner_call_in_the_ordered_list_is_a_script_revise_md_names():
    """FC19 for revise.sh (PRD 038.9 RVS15): the prose stays the fallback, so it names every script the call makes."""
    from pathlib import Path
    revise_module = importlib.import_module("veri.revise")
    prose = (Path(revise_module.__file__).resolve().parents[2] / "REVISE.md").read_text()

    assert [name for name in revise_module.CALLS if "$S/" + name not in prose and name not in NAMED_ELSEWHERE] == []


def test_a_missing_refactor_half_rejected_record_is_exit_2_before_any_call_4433(revise):
    """Review of #4437: refactor's values live only in refactor-half's rejected record, so without it no answer can be
    had (2), never a designed stop (1)."""
    _refactor(revise)
    (revise.wt / ".tdd" / "issue-12-refactor-half-rejected-wait").unlink()
    code, out, err, fake = revise(argv=("12", "refactor"))

    assert (code, fake.launched()) == (2, [])
    assert out.splitlines()[-1] == "stopped at 1 no .tdd/issue-12-refactor-half-rejected-wait"


def test_a_tests_frozen_record_exit_2_on_a_revised_red_pass_is_exit_2_4433(revise):
    """Review of #4437 (RVS8): the record could not answer, so the PASS is not recorded and no comment posts."""
    _red(revise)
    code, out, err, fake = revise(fake=Fake({("red-divergence.sh", None): (3, ""), ("tests-frozen.sh", "record"): (2, "")},
                                            report=RED_REPORT), argv=("12", "red"), missing=("red-half",))

    assert (code, fake.launched()) == (2, ["revise-red-1", "verdict-red"])
    record_at = next(i for i, c in enumerate(fake.calls) if c[0] == "tests-frozen.sh" and c[1][:1] == ("record",))
    assert "comment.sh" not in fake.names()[record_at:]
    assert not (revise.wt / ".tdd" / "issue-12-red-half-wait").exists()


def test_a_tests_frozen_record_exit_1_on_a_revised_red_pass_spends_the_attempt_with_its_stdout_the_reason_4433(revise):
    """Review of #4437 (REVISE.md sub-step 5): the step's own Red case is gone, a verify-red REJECT that spends
    REVISE_BUDGET, so attempt 2 launches on that reason."""
    _red(revise)
    code, out, err, fake = revise(fake=Fake({("red-divergence.sh", None): (3, ""),
                                             ("tests-frozen.sh", "record"): (1, "tests/test_b.py::test_two gone\n"),
                                             ("wait-leaf.sh", "revise-red-2"): (3, "")}, report=RED_REPORT),
                                  argv=("12", "red"), missing=("red-half",))

    assert (code, fake.launched()) == (3, ["revise-red-1", "verdict-red", "revise-red-2"])
    assert (revise.wt / ".tdd" / "verify-red-2.reason").read_text() == "tests/test_b.py::test_two gone\n"


DSTEP = "the prompt says so ⟦diff-checked⟧ ⟦criterion 1⟧"
STEP_BASE = "c" * 40
RENAMED = ("step renamed and changed test cases, so the step must be split: "
           "tests/test_a.py::test_old -> test_new\n")


def _diff_files(revise, reason=REASON, rejected=True):
    """A ⟦diff-checked⟧ step diff-step.sh rejected: its ledger, its reason and its rejected record."""
    tdd = revise.wt / ".tdd"
    (tdd / "issue-12.md").write_text(LEDGER % DSTEP)
    (tdd / "verify-diff.reason").write_text(reason)
    (tdd / "revise-diff-1.out").write_text("OUTCOME: REWRITTEN\nSUITE: ok\n")
    if rejected:
        (tdd / "issue-12-diff-step-rejected-wait").write_text(json.dumps(
            {"conductor": None, "at": "verdict-diff", "step": DSTEP,
             "values": {"step_base": STEP_BASE, "leaf": "develop-diff"}}))


def test_4435_diff_attempt_1_launches_revise_diff_1_from_the_diff_reason_with_no_red_half_record(revise):
    """DST7: the diff phase joins revise.sh (S10); a diff step has no Red, so no red-half record is read."""
    _diff_files(revise)
    code, out, err, fake = revise(argv=("12", "diff"), missing=("red-half",),
                                  answers={("wait-leaf.sh", "revise-diff-1"): (3, "")})

    assert (code, out.splitlines()[-1]) == (3, "waiting on revise-diff-1"), err
    assert fake.call("build-develop-prompt.sh")[1] == ("revise", "diff", ".tdd/issue-12-spec.md", DSTEP, "make unit",
                                                       ".tdd/verify-diff.reason", "make unit")
    assert fake.launched() == ["revise-diff-1"]
    assert (revise.wt / ".tdd" / "verify-diff-1.reason").read_text() == REASON


def test_4435_diff_after_its_leaf_it_runs_no_cost_check_and_re_verifies_against_the_original_step_base(revise):
    """DST7: suite-reported.sh and diff-leaf-deviation.sh for revise-diff-<k>, then verdict-diff on the step base the
    rejection was about; no step-cost line, no prediction check."""
    _diff_files(revise)
    revise(argv=("12", "diff"), missing=("red-half",), answers={("wait-leaf.sh", "revise-diff-1"): (3, "")})
    code, out, err, fake = revise(argv=("12", "diff"), missing=("red-half",),
                                  answers={("wait-leaf.sh", "verdict-diff"): (3, "")})

    assert (code, out.splitlines()[-1]) == (3, "waiting on verdict-diff"), err
    names = fake.names()
    assert not {"step-cost.sh", "red-divergence.sh", "tests-frozen.sh"} & set(names)
    assert [(c[0], c[1]) for c in fake.calls if c[0] in ("suite-reported.sh", "diff-leaf-deviation.sh")] == [
        ("suite-reported.sh", ("revise-diff-1",)),
        ("diff-leaf-deviation.sh", ("revise-diff-1", STEP_BASE, ".tdd/issue-12.md"))]
    launch = fake.call("detach-leaf.sh")
    assert _short(launch[1]) == ("supervise.sh", "verdict-diff", "run-verdict.sh", "--step", DSTEP, "--fast-cmd",
                                 "make unit", "--branch-base", BRANCH_BASE, "diff", ".tdd/issue-12-spec.md",
                                 STEP_BASE)


def test_4435_diff_a_revised_pass_re_saves_diff_steps_wait_naming_the_revise_leaf(revise):
    """DST7, S15: diff-step.sh called again goes on from its verdict to the flip check, pin-recheck.sh and the tick,
    reading the FLIP: line of the revise leaf that made the last commit."""
    _diff_files(revise)
    revise(argv=("12", "diff"), missing=("red-half",), answers={("wait-leaf.sh", "revise-diff-1"): (3, "")})
    revise(argv=("12", "diff"), missing=("red-half",), answers={("wait-leaf.sh", "verdict-diff"): (3, "")})
    code, out, err, fake = revise(argv=("12", "diff"), missing=("red-half",))

    assert code == 0, err
    record = json.loads((revise.wt / ".tdd" / "issue-12-diff-step-wait").read_text())
    assert (record["at"], record["values"]["step_base"], record["values"]["leaf"]) == (
        "verdict-diff", STEP_BASE, "revise-diff-1")
    assert not (revise.wt / ".tdd" / "issue-12-diff-step-rejected-wait").exists()
    assert fake.call("comment.sh", "12")[1] == ("12", "verify-revised", "diff")


def test_4435_diff_a_reject_naming_a_case_renamed_and_changed_stops_exit_1_with_no_leaf(revise):
    """DST7, #2594: the plan split is the conductor's, so no revise leaf runs and no attempt is spent."""
    _diff_files(revise, reason=RENAMED)
    code, out, err, fake = revise(argv=("12", "diff"), missing=("red-half",))

    assert code == 1, err
    assert (fake.launched(), [c for c in fake.calls if c[0] == "event.sh"]) == ([], [])
    assert "renamed and changed" in out.splitlines()[-1]


def test_4435_diff_with_no_rejected_record_is_exit_2(revise):
    _diff_files(revise, rejected=False)
    code, out, err, fake = revise(argv=("12", "diff"), missing=("red-half",))

    assert (code, fake.launched()) == (2, [])
    assert out.splitlines()[-1] == "stopped at 1 no .tdd/issue-12-diff-step-rejected-wait"


def test_4435_diff_a_revise_report_of_outcome_impossible_stops_exit_1_before_any_check_or_re_verify(revise):
    """DST7: the diff phase's route, as refactor's: the leaf says the step cannot be met as stated."""
    _diff_files(revise)
    revise(argv=("12", "diff"), missing=("red-half",), answers={("wait-leaf.sh", "revise-diff-1"): (3, "")})
    code, out, err, fake = revise(argv=("12", "diff"), missing=("red-half",),
                                  fake=Fake(report="OUTCOME: IMPOSSIBLE\n"))

    assert code == 1, err
    assert out.splitlines()[-1] == "stopped at 3 OUTCOME: IMPOSSIBLE"
    assert (fake.launched(), "suite-reported.sh" in fake.names()) == ([], False)


WHY = "OUTCOME: IMPOSSIBLE — the step asks for two behaviours"


def _phase(revise, phase):
    """The files a REJECT of <phase> leaves; the fixture's keyword arguments for its call."""
    if phase == "red":
        _red(revise)
    elif phase == "refactor":
        _refactor(revise)
    elif phase == "diff":
        _diff_files(revise)
        return {"missing": ("red-half",)}
    return {}


@pytest.mark.parametrize("phase", ["red", "green", "refactor", "diff"])
@pytest.mark.parametrize("line", ["OUTCOME: IMPOSSIBLE", WHY])
def test_4435_both_forms_of_outcome_impossible_the_revise_prompts_ask_for_stop_every_phase_exit_1(revise, phase, line):
    """`OUTCOME: REWRITTEN | IMPOSSIBLE — <why>` (develop-revise.md, develop-revise-diff.md) is routed, as is the bare
    `OUTCOME: IMPOSSIBLE` develop-revise.md asks for with a MISSING_TEST: line: neither is another attempt."""
    kw = _phase(revise, phase)
    report = (RED_REPORT if phase == "red" else "OUTCOME: REWRITTEN\n") + line + "\n"
    code, out, err, fake = revise(fake=Fake({("red-divergence.sh", None): (3, "")}, report=report),
                                  argv=("12", phase), **kw)

    assert (code, out.splitlines()[-1]) == (1, "stopped at 3 " + line), err
    assert fake.launched() == ["revise-%s-1" % phase]


@pytest.mark.parametrize("line", ["OUTCOME: IMPOSSIBLE—no spaces round the dash", "OUTCOME: IMPOSSIBLEX",
                                  "OUTCOME: REWRITTEN — IMPOSSIBLE was not the answer"])
def test_4435_an_outcome_line_of_neither_form_routes_nothing(revise, line):
    """The match is the prompts' two forms exactly, no looser."""
    code, out, err, fake = revise(fake=Fake(report="OUTCOME: REWRITTEN\n" + line + "\n"))

    assert not out.splitlines()[-1].startswith("stopped at 3"), out
    assert "verdict-green" in fake.launched()


def test_4435_only_the_outcome_route_takes_the_dash_form(revise):
    """`AGAINST_UNMODIFIED: PASSES — …` is no form a prompt asks for, so it routes nothing."""
    _red(revise)
    report = RED_REPORT + "AGAINST_UNMODIFIED: PASSES — and more\n"
    code, out, err, fake = revise(fake=Fake({("red-divergence.sh", None): (3, "")}, report=report), argv=("12", "red"))

    assert not out.splitlines()[-1].startswith("stopped at 3"), out
    assert "verdict-red" in fake.launched()


def test_4435_diff_a_one_commit_revise_leaf_deviation_exit_3_goes_on_to_the_re_verify(revise):
    """diff-leaf-deviation.sh exit 3 (the one-commit flow) is the normal case, never a stop."""
    _diff_files(revise)
    revise(argv=("12", "diff"), missing=("red-half",), answers={("wait-leaf.sh", "revise-diff-1"): (3, "")})
    code, out, err, fake = revise(argv=("12", "diff"), missing=("red-half",), answers={
        ("diff-leaf-deviation.sh", None): (3, ""), ("wait-leaf.sh", "verdict-diff"): (3, "")})

    assert (code, out.splitlines()[-1], fake.launched()) == (3, "waiting on verdict-diff", ["verdict-diff"]), err


def test_4435_an_outcome_impossible_line_with_no_dash_routes_nothing(revise):
    code, out, err, fake = revise(fake=Fake(report="OUTCOME: REWRITTEN\nOUTCOME: IMPOSSIBLE foo\n"))

    assert not out.splitlines()[-1].startswith("stopped at 3"), out
    assert "verdict-green" in fake.launched()
