"""In-process cases for veri/branch_gate.py, the module branch-gate.sh is a shim over (PRD 027.7, #4030)."""
import importlib
import json
import os

import pytest

LEDGER = "# Plan for #12\n\n- [x] one ⟦criterion 1⟧\n- [ ] the full suite is green ⟦full-suite⟧ ⟦criterion 2⟧\n"
FULL = "make test"


class Fake:
    """A run_script stand-in: records (basename, args, cwd, env, kw) and answers from <answers>, keyed by
    (basename, first argument or None) -> (code, stdout)."""

    def __init__(self, answers=None, mode="local"):
        self.answers, self.calls, self.mode = dict(answers or {}), [], mode

    def __call__(self, name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        self.calls.append((base, args, cwd, env, kw))
        for (script, first), (code, out) in self.answers.items():
            if base == script and (first is None or args[:1] == (first,)):
                return code, out, ""
        if base == "branch-suite.sh":
            return 0, self.mode + "\n", ""
        if base == "detect-test-command.sh":
            return 0, FULL + "\n", ""
        if base == "detach-command.sh" and args[:1] == ("wait",):
            return 0, "PASSED 812\n", ""
        return 0, "", ""

    def names(self):
        return [c[0] for c in self.calls]

    def call(self, base, first=None):
        return next(c for c in self.calls if c[0] == base and (first is None or c[1][:1] == (first,)))


@pytest.fixture
def gate(monkeypatch, run_cli, tmp_path):
    """gate(answers=None, fake=None, missing=(), ledger=LEDGER, argv=None) runs branch-gate for issue 12 from the main
    tree, the run's worktree at .tdd/wt/12; returns (code, stdout, stderr, fake)."""
    fused = importlib.import_module("veri.fused")
    branch_gate = importlib.import_module("veri.branch_gate")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)

    def go(answers=None, fake=None, missing=(), ledger=LEDGER, argv=None):
        files = {"preflight": (wt / ".tdd" / "issue-12-preflight", "worktree=%s\nfast_cmd=make unit\n" % wt),
                 "ledger": (wt / ".tdd" / "issue-12.md", ledger)}
        for key, (path, text) in files.items():
            if key not in missing:
                path.write_text(text)
        fake = fake or Fake(answers)
        monkeypatch.setattr(fused, "run_script", fake)
        code, out, err = run_cli(branch_gate, list(argv if argv is not None else ("12",)), cwd=str(tmp_path))
        return code, out, err, fake

    go.wt = wt
    return go


def test_4030_no_argument_prints_the_usage_and_exits_2_with_no_inner_call(gate):
    code, out, err, fake = gate(argv=())

    assert (code, "branch-gate.sh <n>" in err, fake.calls) == (2, True, [])
    here = os.path.dirname(importlib.import_module("veri.branch_gate").__file__)
    assert os.path.exists(os.path.join(here, "..", "branch-gate.sh"))


@pytest.mark.parametrize("missing, named", [("preflight", ".tdd/issue-12-preflight"), ("ledger", ".tdd/issue-12.md")])
def test_4030_a_missing_input_is_exit_2_before_any_inner_call_named_on_stderr(gate, missing, named):
    code, out, err, fake = gate(missing=(missing,))

    assert (code, fake.calls) == (2, [])
    assert named in err


@pytest.mark.parametrize("ledger", ["# Plan\n\n- [x] one\n- [ ] two ⟦criterion 2⟧\n",
                                    "# Plan\n\n- [x] one\n- [ ] re-pin it ⟦diff-checked⟧\n"],
                         ids=["an unchecked step", "an unchecked diff-checked step"])
def test_4030_a_step_next_unchecked_would_still_hand_out_is_exit_2_before_any_inner_call(gate, ledger):
    code, out, err, fake = gate(ledger=ledger)

    assert (code, fake.calls) == (2, [])
    assert "unchecked step" in err


def test_4030_only_full_suite_and_human_owed_lines_left_unchecked_let_it_run(gate):
    code, out, err, fake = gate(ledger=LEDGER + "- [ ] a human reads it ⟦human-owed⟧\n")

    assert code == 0 and fake.calls


def test_4030_under_ci_it_settles_branch_suite_ci_and_runs_nothing_more(gate):
    code, out, err, fake = gate(fake=Fake(mode="ci"))

    assert (code, out.splitlines()[-1]) == (0, "branch_suite=ci")
    assert [(c[0], c[1], c[2]) for c in fake.calls] == [("branch-suite.sh", (), str(gate.wt))]
    assert (gate.wt / ".tdd" / "issue-12-branch-gate").read_text() == "branch_suite=ci\n"


def test_4030_under_local_it_runs_the_full_command_inside_the_full_suite_stage_records_its_time_and_settles_local(
        gate, monkeypatch):
    clock = iter([1000.0, 1042.0])
    monkeypatch.setattr("time.time", lambda: next(clock))
    code, out, err, fake = gate()

    assert (code, out.splitlines()[-1]) == (0, "branch_suite=local")
    assert [(c[0], c[1]) for c in fake.calls] == [
        ("branch-suite.sh", ()), ("detect-test-command.sh", ("--tier", "all")),
        ("event.sh", ("stage-start", "stage=full-suite")), ("detach-command.sh", ("start", "branch-full-12", "make", "test")),
        ("detach-command.sh", ("wait", "branch-full-12")),
        ("event.sh", ("stage-end", "stage=full-suite", "status=0", "secs=42")),
        ("full-tier-time.sh", ("--record", "42", FULL))]
    for c in fake.calls:
        if c[0] == "event.sh":
            assert (c[3]["VERI_ISSUE"], c[3]["VERI_ACTOR"]) == ("12", "conductor")
    assert all(c[2] == str(gate.wt) for c in fake.calls)
    assert (gate.wt / ".tdd" / "issue-12-branch-gate").read_text() == "branch_suite=local\n"


def test_4030_it_ticks_no_full_suite_line_and_commits_nothing(gate):
    code, out, err, fake = gate()

    assert (gate.wt / ".tdd" / "issue-12.md").read_text() == LEDGER
    assert not {"tick-ledger.sh", "tick-issue-criterion.sh", "push-branch.sh", "git"} & set(fake.names())


@pytest.mark.parametrize("inner", [1, 2])
def test_4030_a_red_wait_ends_the_stage_with_its_code_and_stops_before_any_flake_rerun_repair_or_bail(gate, inner):
    code, out, err, fake = gate(answers={("detach-command.sh", "wait"): (inner, "FAILED 3\n")})

    assert (code, out.splitlines()[-1]) == (inner, "stopped at opening detach-command.sh wait branch-full-12 exit %d"
                                            % inner)
    assert fake.call("event.sh", "stage-end")[1][2] == "status=%d" % inner
    assert fake.calls[-1][0] == "event.sh"
    assert not {"full-tier-time.sh", "add-ledger-step.sh", "classify-bail.sh", "preflight-refused.sh",
                "suite-red-resume.sh", "detach-leaf.sh", "comment.sh"} & set(fake.names())
    assert not [c for c in fake.calls if c[0] == "event.sh" and c[1][:1] in (("bail",), ("suite-flake",))]
    assert not (gate.wt / ".tdd" / "issue-12-branch-gate").exists()
    assert "FAILED 3" in out


@pytest.mark.parametrize("script, first, inner", [("branch-suite.sh", None, 2), ("detect-test-command.sh", None, 2),
                                                  ("detach-command.sh", "start", 2), ("full-tier-time.sh", None, 2),
                                                  ("event.sh", "stage-start", 2)])
def test_4030_an_inner_call_that_fails_stops_it_with_its_code_and_runs_nothing_later(gate, script, first, inner):
    code, out, err, fake = gate(answers={(script, first): (inner, "")})

    assert code == inner
    assert (fake.calls[-1][0], out.splitlines()[-1].startswith("stopped at opening " + script)) == (script, True)
