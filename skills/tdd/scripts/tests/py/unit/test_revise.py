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
                 "reason": (wt / ".tdd" / "verify-green.reason", REASON)}
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
    assert [(c[0], c[1]) for c in fake.calls[:4]] == [
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
