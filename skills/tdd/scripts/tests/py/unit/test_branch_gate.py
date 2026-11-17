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
