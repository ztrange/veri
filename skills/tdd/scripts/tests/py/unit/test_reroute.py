"""In-process cases for veri/reroute.py, the module reroute.sh is a shim over (PRD 038.10, #4434)."""
import importlib
import json
import os

import pytest

STEP = "one thing works ⟦criterion 1⟧"
LEDGER = "# Plan for #12\n\n- [x] zero ⟦criterion 1⟧\n- [ ] %s\n- [ ] two ⟦criterion 2⟧\n"
RED_HALF = ("step=%s\ntest_path=tests/test_a.py\ntarget_test=tests/test_a.py::test_one\n"
            "red_test_id=tests/test_a.py::test_one\nagainst_unmodified=FAILS\n")
OWN = "tests/test_a.py::test_one"
GREEN = ".tdd/develop-green.out"
BRANCH_BASE = "abc1234"
REROUTED = "TEST_PATH: tests/test_b.py\nTARGET_TEST: tests/test_b.py::test_two\nAGAINST_UNMODIFIED: FAILS\n"


class Fake:
    """A run_script stand-in: records (basename, args, cwd, env, kw) and answers from <answers>, keyed by
    (basename, first argument or None) -> (code, stdout); extract-result.sh echoes the report it is fed."""

    def __init__(self, answers=None, waits=None):
        self.answers, self.calls, self.waits = dict(answers or {}), [], dict(waits or {})

    def __call__(self, name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        self.calls.append((base, args, cwd, env, kw))
        if base == "wait-leaf.sh" and self.waits.get(args[0]):
            return self.waits[args[0]].pop(0), "", ""
        for (script, first), (code, out) in self.answers.items():
            if base == script and (first is None or args[:1] == (first,)):
                return code, out, ""
        if base == "extract-result.sh":
            return 0, kw.get("stdin") or "", ""
        if base == "stop-requested.sh":
            return 3, "", ""
        if base == "step-cost.sh":
            return 0, "1.00\n", ""
        if base == "step-budget.sh":
            return 0, "12\n120\n", ""
        return 0, "", ""

    def names(self):
        return [c[0] for c in self.calls]

    def call(self, base, first=None):
        return next(c for c in self.calls if c[0] == base and (first is None or c[1][:1] == (first,)))

    def all(self, base):
        return [c for c in self.calls if c[0] == base]

    def launched(self):
        return [c[1][1] for c in self.calls if c[0] == "detach-leaf.sh"]


@pytest.fixture
def reroute(monkeypatch, run_cli, tmp_path):
    """reroute(answers=None, fake=None, missing=(), argv=("12", GREEN), files=None) runs reroute for issue 12 from the
    main tree, the run's worktree at .tdd/wt/12; returns (code, stdout, stderr, fake)."""
    fused = importlib.import_module("veri.fused")
    module = importlib.import_module("veri.reroute")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)

    def go(answers=None, fake=None, missing=(), argv=("12", GREEN), files=None):
        given = {"branch_base": (wt / ".tdd" / "issue-12-branch-base", BRANCH_BASE + "\n"),
                 "preflight": (wt / ".tdd" / "issue-12-preflight", "worktree=%s\nfast_cmd=make unit\n" % wt),
                 "ledger": (wt / ".tdd" / "issue-12.md", LEDGER % STEP),
                 "spec": (wt / ".tdd" / "issue-12-spec.md", "# spec\n"),
                 "red-half": (wt / ".tdd" / "issue-12-red-half", RED_HALF % STEP),
                 "green": (wt / ".tdd" / "develop-green.out", "WRONG_TEST: the case asserts the old rule\n")}
        for name, text in (files or {}).items():
            (wt / ".tdd" / name).write_text(text)
        for key, (path, text) in given.items():
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


def test_it_runs_wrong_test_route_on_the_report_with_the_steps_own_red_case_and_veri_step_the_open_step_4434(reroute):
    """PRD 038.10 RRT1, RRT9: the target test id from red-half's record, read through fused_step.record."""
    code, out, err, fake = reroute(answers={("wrong-test-route.sh", None): (2, "")})

    route = fake.call("wrong-test-route.sh")
    assert route[1] == ("--spec", ".tdd/issue-12-spec.md", GREEN, OWN)
    assert (route[3]["VERI_STEP"], route[3]["VERI_ISSUE"], route[2]) == (STEP, "12", str(reroute.wt))


@pytest.mark.parametrize("argv, missing", [(("12",), ()), (("x", GREEN), ()), (("12", GREEN, "more"), ()),
                                           (("12", GREEN), ("preflight",))])
def test_a_bad_argument_or_a_missing_preflight_is_exit_2_before_any_inner_call_4434(reroute, argv, missing):
    code, out, err, fake = reroute(argv=argv, missing=missing)

    assert (code, fake.calls) == (2, [])
    assert ("usage: reroute.sh <n> <report>" in err) == (missing == ())


def test_with_no_red_half_record_naming_the_step_it_prints_the_record_seam_and_exits_1_calling_nothing_4434(reroute):
    """PRD 038.10 RRT9: `seam_contract.READS` gains `reroute: ("red-half",)`."""
    code, out, err, fake = reroute(missing=("red-half",))

    assert (code, fake.calls) == (1, [])
    assert out.splitlines()[-1] == ("seam=reroute code=1 reason=record next=seam-settle.sh 12 red-half "
                                    "test_path=… target_test=…")


ROUTE_RED = {("wrong-test-route.sh", None): (0, "red tests/test_b.py::test_two\n")}


def test_on_red_it_writes_the_reroute_event_then_launches_red_contradicted_through_supervise_exiting_3_4434(reroute):
    """PRD 038.10 RRT2, RRT6: the event before the launch, the leaf through detach-leaf.sh supervise.sh, a wait record."""
    code, out, err, fake = reroute(answers={**ROUTE_RED, ("wait-leaf.sh", "develop-red-contradicted"): (3, "")})

    assert (code, out.splitlines()[-1]) == (3, "waiting on develop-red-contradicted")
    names = fake.names()
    assert names.index("event.sh") < names.index("detach-leaf.sh")
    mark = fake.call("event.sh")
    assert mark[1] == ("reroute", "kind=red", "case=tests/test_b.py::test_two")
    assert (mark[3]["VERI_ACTOR"], mark[3]["VERI_STEP"], mark[3]["VERI_ISSUE"]) == ("conductor", STEP, "12")
    prompt = fake.call("build-develop-prompt.sh")
    assert prompt[1] == ("red-contradicted", ".tdd/issue-12-spec.md", STEP, "make unit", "tests/test_b.py::test_two")
    assert prompt[4]["out"] == ".tdd/develop-red-contradicted.prompt"
    launch = fake.call("detach-leaf.sh")
    assert _short(launch[1]) == ("supervise.sh", "develop-red-contradicted", "run-leaf.sh",
                                 ".tdd/develop-red-contradicted.prompt", "--permission-mode", "bypassPermissions")
    assert (launch[3]["VERI_TEST_CMD"], launch[3]["VERI_STEP"]) == ("make unit", STEP)
    assert (launch[4]["out"], launch[4]["err"]) == (".tdd/develop-red-contradicted.out",
                                                    ".tdd/develop-red-contradicted.err")
    record = json.loads((reroute.wt / ".tdd" / "issue-12-reroute-wait").read_text())
    assert (record["at"], record["values"]["kind"], record["values"]["report"]) == (
        "develop-red-contradicted", "red", GREEN)


def test_called_again_it_waits_launches_verdict_red_with_red_halfs_arguments_over_the_edited_case_exiting_3_4434(
        reroute):
    """PRD 038.10 RRT2, RRT10: the reroute's verify-red takes the red phase's run-verdict.sh arguments."""
    first = reroute(answers={**ROUTE_RED, ("wait-leaf.sh", "develop-red-contradicted"): (3, "")})[0]
    code, out, err, fake = reroute(answers={("wait-leaf.sh", "verdict-red"): (3, "")},
                                   files={"develop-red-contradicted.out": REROUTED})

    assert (first, code, out.splitlines()[-1]) == (3, 3, "waiting on verdict-red")
    assert fake.all("wrong-test-route.sh") == []
    assert [c[1] for c in fake.calls[:3]] == [("develop-red-contradicted",), (STEP,), ()]
    assert fake.launched() == ["verdict-red"]
    launch = fake.call("detach-leaf.sh")
    assert _short(launch[1]) == ("supervise.sh", "verdict-red", "run-verdict.sh", "--step", STEP, "--fast-cmd",
                                 "make unit", "--branch-base", BRANCH_BASE, "red", ".tdd/issue-12-spec.md",
                                 "tests/test_b.py", "tests/test_b.py::test_two")
    assert (launch[4]["out"], launch[4]["err"]) == (".tdd/verify-red.reason", ".tdd/verify-red.err")
    record = json.loads((reroute.wt / ".tdd" / "issue-12-reroute-wait").read_text())
    assert record["at"] == "verdict-red"


def test_called_again_it_runs_check_earlier_excepting_the_routed_case_before_launching_verdict_red_4482(reroute):
    reroute(answers={**ROUTE_RED, ("wait-leaf.sh", "develop-red-contradicted"): (3, "")})
    code, out, err, fake = reroute(answers={("wait-leaf.sh", "verdict-red"): (3, "")},
                                   files={"develop-red-contradicted.out": REROUTED})

    earlier = [c for c in fake.all("tests-frozen.sh") if c[1][:1] == ("check-earlier",)]
    assert [c[1] for c in earlier] == [("check-earlier", ".tdd/issue-12.md", "--step", STEP,
                                        "--except", "tests/test_b.py::test_two")]
    assert fake.calls.index(earlier[0]) < fake.calls.index(fake.call("detach-leaf.sh"))


def test_a_check_earlier_exit_1_is_exit_1_launching_no_verdict_red_4482(reroute):
    reroute(answers={**ROUTE_RED, ("wait-leaf.sh", "develop-red-contradicted"): (3, "")})
    code, out, err, fake = reroute(answers={("tests-frozen.sh", "check-earlier"): (1, "earlier test changed\n"),
                                            ("wait-leaf.sh", "verdict-red"): (3, "")},
                                   files={"develop-red-contradicted.out": REROUTED})

    assert (code, fake.launched()) == (1, [])


def test_a_check_earlier_exit_1_stops_the_stage_with_red_switched_off_too_4482(reroute):
    code, out, err, fake = reroute(answers={**ROUTE_RED, ("tests-frozen.sh", "check-earlier"): (1, "earlier test changed\n")},
                                   files={"develop-red-contradicted.out": REROUTED, "issue-12-skip-verify": "red\n"})

    earlier = [c for c in fake.all("tests-frozen.sh") if c[1][:1] == ("check-earlier",)]
    assert (code, len(earlier)) == (1, 1)
    assert not (reroute.wt / ".tdd" / "verdict-red.exit").exists()


def test_on_a_verify_red_pass_it_rerecords_the_frozen_tests_over_both_test_paths_and_exits_0_4434(reroute):
    """PRD 038.10 RRT2: `tests-frozen.sh record --step … --red-case '<red-test-id>' <test-path>…`, the step's own case."""
    reroute(answers={**ROUTE_RED, ("wait-leaf.sh", "develop-red-contradicted"): (3, "")})
    reroute(answers={("wait-leaf.sh", "verdict-red"): (3, "")}, files={"develop-red-contradicted.out": REROUTED})
    code, out, err, fake = reroute()

    assert code == 0, out + err
    record = fake.call("tests-frozen.sh")
    assert record[1] == ("record", "--step", STEP, "--red-case", OWN, "tests/test_a.py", "tests/test_b.py")
    assert record[4]["out"] == ".tdd/verify-red.reason"
    assert fake.names()[-1] == "tests-frozen.sh"
    assert not (reroute.wt / ".tdd" / "issue-12-reroute-wait").exists()


def test_a_successful_reroute_run_on_its_own_removes_the_answered_verify_green_rejects_exit_file_and_record_4833(
        reroute):
    rejected = {"conductor": None, "at": "verdict-green", "step": STEP,
                "values": {"test_path": "tests/test_a.py", "target_test": OWN}}
    code, out, err, fake = reroute(answers=ROUTE_RED, argv=("12", ".tdd/verify-green.reason"),
                                   files={"develop-red-contradicted.out": REROUTED,
                                          "verify-green.reason": "VERDICT: REJECT\nno\n",
                                          "verdict-green.exit": "1\n",
                                          "issue-12-green-half-rejected-wait": json.dumps(rejected)})

    assert code == 0, out + err
    left = [name for name in ("issue-12-green-half-rejected-wait", "verdict-green.exit")
            if (reroute.wt / ".tdd" / name).exists()]
    assert left == []


def test_run_step_from_green_half_after_a_reroute_run_on_its_own_calls_green_half_and_never_revise_green_4833(
        reroute, monkeypatch, run_cli, tmp_path):
    rejected = {"conductor": None, "at": "verdict-green", "step": STEP,
                "values": {"test_path": "tests/test_a.py", "target_test": OWN}}
    rerouted = reroute(answers=ROUTE_RED, argv=("12", ".tdd/verify-green.reason"),
                       files={"develop-red-contradicted.out": REROUTED,
                              "verify-green.reason": "VERDICT: REJECT\nno\n",
                              "verdict-green.exit": "1\n",
                              "issue-12-green-half-rejected-wait": json.dumps(rejected)})
    stages = Fake({("step-close.sh", None): (0, "next=cycle\n")})
    monkeypatch.setattr(importlib.import_module("veri.fused"), "run_script", stages)

    code, out, err = run_cli(importlib.import_module("veri.run_step"), ["12", "--from", "green-half"],
                             cwd=str(tmp_path))

    assert rerouted[0] == 0, rerouted[1] + rerouted[2]
    assert [c[1] for c in stages.all("revise.sh")] == []
    assert [c[1] for c in stages.all("green-half.sh")] == [("12",)]
    assert code == 0, out + err


@pytest.mark.parametrize("said, kind, phase, args", [
    ("repair tests/test_a.py::test_one tests/test_c.py::test_old", "repair", "red-repair",
     ("tests/test_a.py::test_one", GREEN, "tests/test_c.py::test_old")),
    ("supersede tests/test_c.py::test_x tests/test_d.py::test_y", "supersede", "red-supersede",
     (GREEN, "tests/test_c.py::test_x", "tests/test_d.py::test_y")),
    ("missing the empty list is rejected", "missing", "red-missing", (GREEN,))])
def test_repair_supersede_and_missing_launch_their_own_red_with_their_prompt_arguments_4434(
        reroute, said, kind, phase, args):
    """PRD 038.10 RRT2: `red-repair`, `red-supersede` and `red-missing`, each with its event before the launch."""
    code, out, err, fake = reroute(answers={("wrong-test-route.sh", None): (0, said + "\n"),
                                            ("wait-leaf.sh", None): (3, "")})

    assert (code, out.splitlines()[-1]) == (3, "waiting on develop-" + phase)
    assert fake.call("event.sh")[1] == ("reroute", "kind=" + kind, "case=" + said.split(" ", 1)[1])
    assert fake.call("build-develop-prompt.sh")[1] == (phase, ".tdd/issue-12-spec.md", STEP, "make unit") + args
    assert fake.launched() == ["develop-" + phase]


def test_supersede_verifies_each_named_case_in_turn_then_rerecords_over_every_test_path_4434(reroute):
    """PRD 038.10 RRT2: `supersede` names two or more cases, and each edited one goes through verify-red."""
    said = "supersede tests/test_c.py::test_x tests/test_d.py::test_y\n"
    reroute(answers={("wrong-test-route.sh", None): (0, said), ("wait-leaf.sh", "develop-red-supersede"): (3, "")})
    report = "TEST_PATH: tests/test_c.py\nTARGET_TEST: NONE — updated together\nAGAINST_UNMODIFIED: FAILS\n"
    first = reroute(answers={("wait-leaf.sh", "verdict-red"): (3, "")}, files={"develop-red-supersede.out": report})
    second = reroute(fake=Fake(waits={"verdict-red": [0, 3]}))
    code, out, err, fake = reroute()

    targets = [[a for a in c[1] if "::" in a] for f in (first, second) for c in f[3].calls if c[0] == "detach-leaf.sh"]
    assert (first[0], second[0], code) == (3, 3, 0), out + err
    assert targets == [["tests/test_c.py::test_x"], ["tests/test_d.py::test_y"]]
    assert fake.call("tests-frozen.sh")[1] == ("record", "--step", STEP, "--red-case", OWN, "tests/test_a.py",
                                               "tests/test_c.py", "tests/test_d.py")


def test_it_writes_no_revise_mark_and_reads_no_budget_so_broken_budgets_leave_the_reroute_unchanged_4434(
        reroute, monkeypatch):
    """PRD 038.10 RRT3: whether the reroute is free is wrong-test-route.sh's answer; the stage reads neither budget."""
    monkeypatch.setenv("REVISE_BUDGET", "not-a-number")
    monkeypatch.setenv("VERI_MISSING_REROUTE_BUDGET", "")
    code, out, err, fake = reroute(answers=ROUTE_RED, files={"develop-red-contradicted.out": REROUTED})

    assert code == 0, out + err
    assert [c[1][0] for c in fake.all("event.sh")] == ["reroute"]


@pytest.mark.parametrize("route, said", [
    (0, "prep tests/test_c.py::test_x tests/test_d.py::test_y"), (0, "later two"), (0, "fixture tests/test_a.py make"),
    (0, "supersede-diff tests/test_c.py::test_x"), (1, "missing-exhausted the empty list is rejected"),
    (1, "repair-exhausted test_one")])
def test_an_answer_it_does_not_run_stops_with_exit_1_naming_the_answer_launching_nothing_4434(reroute, route, said):
    """PRD 038.10 RRT4, S11, S12: plan growth, the diff verifier and bails stay the conductor's."""
    code, out, err, fake = reroute(answers={("wrong-test-route.sh", None): (route, said + "\n")})

    assert (code, out.splitlines()[-1]) == (1, "stopped at route " + said)
    assert (fake.launched(), fake.all("event.sh")) == ([], [])


@pytest.mark.parametrize("against", ["PASSES", "UNTESTABLE"])
def test_a_rerouted_red_that_does_not_fail_stops_with_exit_1_naming_the_line_launching_no_verify_red_4434(
        reroute, against):
    """PRD 038.10 RRT4: a pin report is verify-pin's, by hand."""
    reroute(answers={**ROUTE_RED, ("wait-leaf.sh", "develop-red-contradicted"): (3, "")})
    code, out, err, fake = reroute(files={"develop-red-contradicted.out": REROUTED.replace("FAILS", against)})

    assert (code, out.splitlines()[-1]) == (1, "stopped at leaf AGAINST_UNMODIFIED: " + against)
    assert (fake.launched(), fake.all("tests-frozen.sh")) == ([], [])


def test_4770_a_rerouted_red_reporting_against_unmodified_holds_stops_with_exit_1_naming_the_line_never_2(reroute):
    """PRD 044.2: a HOLDS report writes no test, so its TEST_PATH: and TARGET_TEST: lines are empty; it is stopped on
    as PASSES is, an answer (exit 1), never a missing line (exit 2)."""
    reroute(answers={**ROUTE_RED, ("wait-leaf.sh", "develop-red-contradicted"): (3, "")})
    holds = "TEST_PATH:\nTARGET_TEST:\nAGAINST_UNMODIFIED: HOLDS\nCOVERING_TESTS: tests/test_b.py::test_two\n"
    code, out, err, fake = reroute(files={"develop-red-contradicted.out": holds})

    assert (code, out.splitlines()[-1]) == (1, "stopped at leaf AGAINST_UNMODIFIED: HOLDS")
    assert (fake.launched(), fake.all("tests-frozen.sh")) == ([], [])


def test_a_rerouted_red_report_missing_a_line_is_exit_2_4434(reroute):
    reroute(answers={**ROUTE_RED, ("wait-leaf.sh", "develop-red-contradicted"): (3, "")})
    code, out, err, fake = reroute(files={"develop-red-contradicted.out": "TEST_PATH: tests/test_b.py\n"})

    assert (code, out.splitlines()[-1]) == (2, "stopped at leaf no TARGET_TEST: line")
    assert fake.launched() == []


@pytest.mark.parametrize("report", [GREEN, ".tdd/revise-green-1.out"])
def test_a_revise_answer_is_exit_1_printing_route_revise_never_3_and_leaves_revise_sh_a_reason_and_green_halfs_record(
        reroute, report):
    """PRD 038.10 RRT5: wrong-test-route.sh's 3 means "go revise", an answer, not "call again". The green report is
    the reason revise.sh's attempt copies, and green-half's rejected record sends a sliced revise back to revise.sh."""
    code, out, err, fake = reroute(answers={("wrong-test-route.sh", None): (3, "revise\n")}, argv=("12", report),
                                   files={"revise-green-1.out": "WRONG_TEST: still the old rule\n"})

    assert (code, out.splitlines()[-1]) == (1, "route=revise phase=green")
    assert (fake.launched(), fake.all("event.sh")) == ([], [])
    assert (reroute.wt / ".tdd" / "verify-green.reason").read_text() == (reroute.wt / report).read_text()
    record = json.loads((reroute.wt / ".tdd" / "issue-12-green-half-rejected-wait").read_text())
    assert (record["step"], record["at"], record["values"]) == (
        STEP, "verdict-green", {"test_path": "tests/test_a.py", "target_test": OWN})


def test_a_revise_answer_on_verify_greens_reason_keeps_the_reason_and_green_halfs_own_rejected_record_4434(reroute):
    kept = {"conductor": None, "at": "verdict-green", "values": {"test_path": "tests/test_a.py", "x": "1"},
            "step": STEP}
    code, out, err, fake = reroute(answers={("wrong-test-route.sh", None): (3, "revise\n")},
                                   argv=("12", ".tdd/verify-green.reason"),
                                   files={"verify-green.reason": "VERDICT: REJECT\nno\n",
                                          "issue-12-green-half-rejected-wait": json.dumps(kept)})

    assert (code, out.splitlines()[-1]) == (1, "route=revise phase=green")
    assert (reroute.wt / ".tdd" / "verify-green.reason").read_text() == "VERDICT: REJECT\nno\n"
    assert json.loads((reroute.wt / ".tdd" / "issue-12-green-half-rejected-wait").read_text()) == kept


def _red_revise_left(reroute):
    record = json.loads((reroute.wt / ".tdd" / "issue-12-red-half-rejected-wait").read_text())
    return (record["step"], record["at"], record["values"]) == (
        STEP, "verdict-red", {"test_path": "tests/test_a.py", "target_test": OWN,
                              "rerouted": ["tests/test_a.py", "tests/test_b.py"]})


def test_a_verify_red_reject_of_the_rerouted_case_is_exit_1_route_revise_red_with_red_halfs_rejected_record_4434(
        reroute):
    """PRD 038.10 RRT5: the verifier's reason stays in `.tdd/verify-red.reason` for revise.sh <n> red."""
    reroute(answers={**ROUTE_RED, ("wait-leaf.sh", "develop-red-contradicted"): (3, "")})
    code, out, err, fake = reroute(answers={("wait-leaf.sh", "verdict-red"): (1, "")},
                                   files={"develop-red-contradicted.out": REROUTED})

    assert (code, out.splitlines()[-1]) == (1, "route=revise phase=red")
    assert [c[1] for c in fake.all("tests-frozen.sh")] == [
        ("check-earlier", ".tdd/issue-12.md", "--step", STEP, "--except", "tests/test_b.py::test_two")]
    assert _red_revise_left(reroute)
    assert not (reroute.wt / ".tdd" / "issue-12-reroute-wait").exists()


def test_a_tests_frozen_record_exit_1_is_exit_1_route_revise_red_its_stdout_the_reason_4434(reroute):
    """PRD 038.10 RRT5: a reroute that deleted the step's own case is a verify-red REJECT."""
    code, out, err, fake = reroute(answers={**ROUTE_RED, ("tests-frozen.sh", "record"): (1, "")},
                                   files={"develop-red-contradicted.out": REROUTED})

    assert (code, out.splitlines()[-1]) == (1, "route=revise phase=red")
    assert fake.call("tests-frozen.sh", "record")[4]["out"] == ".tdd/verify-red.reason"
    assert _red_revise_left(reroute)


@pytest.mark.parametrize("answers, last", [
    ({("wrong-test-route.sh", None): (2, "")},
     "stopped at route wrong-test-route.sh --spec .tdd/issue-12-spec.md .tdd/develop-green.out %s exit 2" % OWN),
    ({**ROUTE_RED, ("wait-leaf.sh", "develop-red-contradicted"): (2, "")},
     "stopped at leaf wait-leaf.sh develop-red-contradicted exit 2"),
    ({**ROUTE_RED, ("detach-leaf.sh", None): (2, "")}, None),
    ({**ROUTE_RED, ("wait-leaf.sh", "verdict-red"): (2, "")}, "stopped at verify wait-leaf.sh verdict-red exit 2"),
    ({**ROUTE_RED, ("tests-frozen.sh", "record"): (2, "")},
     "stopped at record tests-frozen.sh record --step %s exit 2" % STEP)])
def test_a_route_supervisor_verifier_or_tests_frozen_exit_2_is_exit_2_4434(reroute, answers, last):
    """PRD 038.10 RRT6: no answer could be obtained, kept apart from the designed stops' 1."""
    code, out, err, fake = reroute(answers=answers, files={"develop-red-contradicted.out": REROUTED})

    assert code == 2, out + err
    assert last is None or out.splitlines()[-1] == last


def test_with_red_switched_off_no_reroute_launches_verify_red_it_marks_the_skip_and_goes_on_as_on_a_pass_4434(
        reroute):
    """PRD 038.10 RRT7, ADR-0033: `verify-red-skipped reason=switched-off`, `skipped` in `.tdd/verdict-red.exit`."""
    code, out, err, fake = reroute(answers=ROUTE_RED, files={"develop-red-contradicted.out": REROUTED,
                                                             "issue-12-skip-verify": "red\n"})

    assert code == 0, out + err
    assert fake.launched() == ["develop-red-contradicted"]
    assert [c[1] for c in fake.all("event.sh")][1:] == [("verify-red-skipped", "reason=switched-off")]
    assert (reroute.wt / ".tdd" / "verdict-red.exit").read_text() == "skipped\n"
    assert fake.names()[-1] == "tests-frozen.sh"


def test_with_green_switched_off_verify_greens_reason_is_never_routed_but_a_green_reports_routes_still_are_4434(
        reroute):
    """PRD 038.10 RRT7: SKILL.md's Green, "only a verify-green reason is never routed"."""
    off = {"issue-12-skip-verify": "green\n", "verify-green.reason": "VERDICT: REJECT\n"}
    code, out, err, fake = reroute(answers=ROUTE_RED, files=off, argv=("12", ".tdd/verify-green.reason"))
    routed = reroute(answers={("wrong-test-route.sh", None): (0, "later two\n")})

    assert (code, out.splitlines()[-1], fake.calls) == (
        1, "stopped at route .tdd/verify-green.reason with green switched off", [])
    assert (routed[0], len(routed[3].all("wrong-test-route.sh"))) == (1, 1)


def test_it_prints_one_line_per_call_with_its_exit_code_and_never_a_leafs_or_a_suites_output_4434(reroute):
    """PRD 038.10 RRT11, PRD 027 D7: inner stdout, the rerouted red's report and the green report stay out."""
    class Marked(Fake):
        def __call__(self, name, *args, **kw):
            code, out, err = super().__call__(name, *args, **kw)
            if os.path.basename(name) in ("extract-result.sh", "step-cost.sh", "step-budget.sh",
                                          "wrong-test-route.sh"):
                return code, out, err
            return code, "OUT<%d>\n" % len(self.calls) + out, err

    code, out, err, fake = reroute(fake=Marked(ROUTE_RED),
                                   files={"develop-red-contradicted.out": REROUTED + "MARKER-4434 leaf\n"})

    lines = out.splitlines()
    assert code == 0, out + err
    assert not [line for line in lines if "OUT<" in line or "MARKER-4434" in line or "old rule" in line]
    assert len(lines) == len(fake.calls)
    assert all(line.rsplit(" exit ", 1)[-1].isdigit() for line in lines)


def test_a_wait_record_naming_another_step_is_dropped_and_the_route_runs_again_4434(reroute):
    """Records are caches (S1): a reroute wait another step left is not this step's leaf."""
    reroute(answers={**ROUTE_RED, ("wait-leaf.sh", "develop-red-contradicted"): (3, "")})
    path = reroute.wt / ".tdd" / "issue-12-reroute-wait"
    record = json.loads(path.read_text())
    assert record["values"]["step"] == STEP
    record["values"]["step"] = "zero ⟦criterion 1⟧"
    path.write_text(json.dumps(record))
    code, out, err, fake = reroute(answers={("wrong-test-route.sh", None): (0, "later two\n")})

    assert (code, len(fake.all("wrong-test-route.sh")), fake.all("wait-leaf.sh")) == (1, 1, [])


def test_a_red_half_record_whose_step_differs_only_by_marks_is_refreshed_with_a_reroute_record_refreshed_event_4434(
        reroute):
    """PRD 038.10 RRT9: the `record-refreshed` `stage` enum gains `reroute`, under the strict events the fixture sets."""
    stale = "one thing works ⟦added⟧ ⟦criterion 3⟧"
    code, out, err, fake = reroute(answers={("wrong-test-route.sh", None): (0, "later two\n")},
                                   files={"issue-12-red-half": RED_HALF % stale})

    events = [json.loads(line) for line in (reroute.wt / ".tdd" / "events.jsonl").read_text().splitlines()]
    assert code == 1, out + err
    assert [(e["stage"], e["key"], e["old"], e["new"]) for e in events if e["event"] == "record-refreshed"] == [
        ("reroute", "step", stale, STEP)]


OWN_RED = "TEST_PATH: tests/test_a.py\nTARGET_TEST: tests/test_a.py::test_one\nAGAINST_UNMODIFIED: FAILS\n"


def test_a_revised_rerouted_red_keeps_the_steps_own_case_and_every_test_path_in_red_halfs_record_4434(
        reroute, run_cli, monkeypatch):
    """A verify-red REJECT of a rerouted case goes to revise.sh <n> red (RRT5): its PASS records the frozen tests with
    the step's own Red case over every test path, and leaves red-half's own case, not the rerouted one, in the wait
    record red-half settles from. Drives reroute.py, then revise.py, through one fake."""
    reroute(answers={**ROUTE_RED, ("wait-leaf.sh", "develop-red-contradicted"): (3, "")})
    code = reroute(answers={("wait-leaf.sh", "verdict-red"): (1, "")},
                   files={"develop-red-contradicted.out": REROUTED, "develop-red.out": OWN_RED,
                          "verify-red.reason": "VERDICT: REJECT\nthe rerouted case asserts nothing\n"})[0]
    (reroute.wt / ".tdd" / "revise-red-1.out").write_text(REROUTED)
    fake = Fake({("red-divergence.sh", None): (3, "")})
    monkeypatch.setattr(importlib.import_module("veri.fused"), "run_script", fake)
    revised = run_cli(importlib.import_module("veri.revise"), ["12", "red"], cwd=str(reroute.wt.parents[2]))

    assert (code, revised[0]) == (1, 0), revised[1] + revised[2]
    assert fake.call("tests-frozen.sh", "record")[1] == (
        "record", "--step", STEP, "--red-case", OWN, "tests/test_a.py", "tests/test_b.py")
    record = json.loads((reroute.wt / ".tdd" / "issue-12-red-half-wait").read_text())
    assert (record["at"], record["values"]["test_path"], record["values"]["target_test"]) == (
        "verdict-red", "tests/test_a.py", OWN)


@pytest.mark.parametrize("said, report, paths", [
    ("red tests/test_b.py::test_two\n", REROUTED, ("tests/test_a.py", "tests/test_b.py")),
    ("supersede tests/test_c.py::test_x tests/test_d.py::test_y\n",
     "TEST_PATH: tests/test_c.py\nTARGET_TEST: NONE — updated together\nAGAINST_UNMODIFIED: FAILS\n",
     ("tests/test_a.py", "tests/test_c.py", "tests/test_d.py"))])
def test_a_revise_of_a_rerouted_red_restores_production_keeping_every_rerouted_test_path_4434(
        reroute, run_cli, monkeypatch, said, report, paths):
    """`restore-production.sh` keeps only the paths it is handed: a revise of a rerouted case hands it every path the
    reroute edited, so neither the rerouted edit nor a case verify-red already passed is reverted. Drives reroute.py,
    then revise.py, through one fake."""
    leaf = "develop-red-supersede" if said.startswith("supersede") else "develop-red-contradicted"
    reroute(answers={("wrong-test-route.sh", None): (0, said), ("wait-leaf.sh", leaf): (3, "")})
    code = reroute(answers={("wait-leaf.sh", "verdict-red"): (1, "")},
                   files={leaf + ".out": report, "develop-red.out": OWN_RED,
                          "verify-red.reason": "VERDICT: REJECT\nthe rerouted case asserts nothing\n"})[0]
    fake = Fake({("wait-leaf.sh", "revise-red-1"): (3, "")})
    monkeypatch.setattr(importlib.import_module("veri.fused"), "run_script", fake)
    revised = run_cli(importlib.import_module("veri.revise"), ["12", "red"], cwd=str(reroute.wt.parents[2]))

    assert (code, revised[0]) == (1, 3), revised[1] + revised[2]
    assert fake.call("restore-production.sh")[1] == paths


def test_a_rerouted_red_reporting_an_unknown_against_unmodified_value_is_exit_2_4434(reroute):
    reroute(answers={**ROUTE_RED, ("wait-leaf.sh", "develop-red-contradicted"): (3, "")})
    code, out, err, fake = reroute(files={"develop-red-contradicted.out": REROUTED.replace("FAILS", "MAYBE")})

    assert (code, out.splitlines()[-1]) == (2, "stopped at leaf no AGAINST_UNMODIFIED: line")
    assert fake.launched() == []


def test_4496_on_red_green_s_uncommitted_production_edit_is_restored_before_the_leaf_launches_keeping_the_tests(reroute):
    """The production file reads as HEAD's when the leaf is launched; the step's test path and the rerouted case's
    file are the paths restore-production.sh keeps."""
    prod = reroute.wt / "src_prod.py"
    prod.write_text("green's edit\n")
    seen = {}

    class Restoring(Fake):
        def __call__(self, name, *args, **kw):
            base = os.path.basename(name)
            if base == "restore-production.sh":
                prod.write_text("HEAD\n")
            if base == "detach-leaf.sh":
                seen["at_launch"] = prod.read_text()
            return super().__call__(name, *args, **kw)

    fake = Restoring({**ROUTE_RED, ("wait-leaf.sh", "develop-red-contradicted"): (3, "")})
    reroute(fake=fake)

    assert seen["at_launch"] == "HEAD\n"
    assert sorted(fake.call("restore-production.sh")[1]) == ["tests/test_a.py", "tests/test_b.py"]


def test_4546_on_repair_green_s_uncommitted_production_edit_is_restored_before_the_leaf_launches_keeping_the_tests(
        reroute):
    """A `repair <case> <superseded>…` answer: the production file reads as HEAD's when develop-red-repair is
    launched; the step's test path and every routed case's file are the paths restore-production.sh keeps."""
    prod = reroute.wt / "src_prod.py"
    prod.write_text("green's edit\n")
    seen = {}

    class Restoring(Fake):
        def __call__(self, name, *args, **kw):
            base = os.path.basename(name)
            if base == "restore-production.sh":
                prod.write_text("HEAD\n")
            if base == "detach-leaf.sh":
                seen["at_launch"] = prod.read_text()
            return super().__call__(name, *args, **kw)

    fake = Restoring({("wrong-test-route.sh", None): (0, "repair tests/test_b.py::test_two tests/test_c.py::test_old\n"),
                      ("wait-leaf.sh", "develop-red-repair"): (3, "")})
    reroute(fake=fake)

    assert (fake.launched(), seen.get("at_launch")) == (["develop-red-repair"], "HEAD\n")
    assert sorted(fake.call("restore-production.sh")[1]) == ["tests/test_a.py", "tests/test_b.py", "tests/test_c.py"]


def test_4546_on_missing_green_s_uncommitted_production_edit_is_restored_before_the_leaf_launches_keeping_the_test(
        reroute):
    """A `missing <behaviour>` answer: the production file reads as HEAD's when develop-red-missing is launched; the
    step's test path is the one path restore-production.sh keeps, since the answer names a behaviour, not a case."""
    prod = reroute.wt / "src_prod.py"
    prod.write_text("green's edit\n")
    seen = {}

    class Restoring(Fake):
        def __call__(self, name, *args, **kw):
            base = os.path.basename(name)
            if base == "restore-production.sh":
                prod.write_text("HEAD\n")
            if base == "detach-leaf.sh":
                seen["at_launch"] = prod.read_text()
            return super().__call__(name, *args, **kw)

    fake = Restoring({("wrong-test-route.sh", None): (0, "missing the empty list is rejected\n"),
                      ("wait-leaf.sh", "develop-red-missing"): (3, "")})
    reroute(fake=fake)

    assert (fake.launched(), seen.get("at_launch")) == (["develop-red-missing"], "HEAD\n")
    assert list(fake.call("restore-production.sh")[1]) == ["tests/test_a.py"]


@pytest.mark.parametrize("said, leaf, restores", [
    ("red tests/test_b.py::test_two", "develop-red-contradicted", True),
    ("repair tests/test_a.py::test_one tests/test_c.py::test_old", "develop-red-repair", True),
    ("supersede tests/test_c.py::test_x tests/test_d.py::test_y", "develop-red-supersede", False),
    ("missing the empty list is rejected", "develop-red-missing", True)])
def test_4496_each_answer_kind_restores_production_or_not_before_its_leaf_launches(reroute, said, leaf, restores):
    """Contrast, per answer kind: whether restore-production.sh runs before its leaf launches. `supersede` launches
    with green's edit left alone (#4546 leaves it out of scope)."""
    fake = reroute(answers={("wrong-test-route.sh", None): (0, said + "\n"), ("wait-leaf.sh", None): (3, "")})[3]

    assert fake.launched() == [leaf]
    assert ("restore-production.sh" in fake.names()) is restores


def test_4496_a_restore_production_exit_2_stops_the_reroute_at_exit_2_before_any_leaf_launches(reroute):
    """No answer from restore-production.sh is no clean tree: the rerouted red is never launched over it."""
    code, out, err, fake = reroute(answers={**ROUTE_RED, ("restore-production.sh", None): (2, "")})

    assert (code, fake.launched()) == (2, []), out + err
    assert out.splitlines()[-1].startswith("stopped at launch restore-production.sh")


def test_4496_an_answer_it_does_not_run_calls_no_restore_production_leaving_the_edit_in_the_worktree(reroute):
    """Stopped at route, nothing launches and production is never restored: green's edit is still there at exit."""
    prod = reroute.wt / "src_prod.py"
    prod.write_text("green's edit\n")

    class Restoring(Fake):
        def __call__(self, name, *args, **kw):
            if os.path.basename(name) == "restore-production.sh":
                prod.write_text("HEAD\n")
            return super().__call__(name, *args, **kw)

    fake = Restoring({("wrong-test-route.sh", None): (0, "later two\n")})
    code, out, err, fake = reroute(fake=fake)

    assert (code, fake.launched(), "restore-production.sh" in fake.names()) == (1, [], False)
    assert prod.read_text() == "green's edit\n"
