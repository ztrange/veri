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
    """PRD 038.10 RRT4: a pin report is verify-pin's, `pin-target.sh` and `pin-reject-route.sh`, by hand."""
    reroute(answers={**ROUTE_RED, ("wait-leaf.sh", "develop-red-contradicted"): (3, "")})
    code, out, err, fake = reroute(files={"develop-red-contradicted.out": REROUTED.replace("FAILS", against)})

    assert (code, out.splitlines()[-1]) == (1, "stopped at leaf AGAINST_UNMODIFIED: " + against)
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
