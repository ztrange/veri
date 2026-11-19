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

    def __init__(self, answers=None):
        self.answers, self.calls = dict(answers or {}), []

    def __call__(self, name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        self.calls.append((base, args, cwd, env, kw))
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
