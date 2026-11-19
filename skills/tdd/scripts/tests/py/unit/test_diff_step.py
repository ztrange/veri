"""In-process cases for veri/diff_step.py, the module diff-step.sh is a shim over (PRD 038.3, #4435)."""
import importlib
import json
import os

import pytest

STEP = "the prompt says so ⟦diff-checked⟧ ⟦criterion 1⟧"
QUALITY = "a weak test is strengthened ⟦test-quality⟧ ⟦diff-checked⟧ ⟦criterion 1⟧"
LINT = "lint passes ⟦lint-repair⟧ ⟦diff-checked⟧ ⟦criterion 1⟧"
LEDGER = "# Plan for #12\n\n- [x] zero ⟦criterion 1⟧\n- [ ] %s\n- [ ] two ⟦criterion 2⟧\n"
STEP_BASE = "c" * 40
BRANCH_BASE = "abc1234"
FLIP = "FLIP: tests/test_a.py 'assert x == 1→assert x == 2'\n"


class Fake:
    """A run_script stand-in: records (basename, args, cwd, env, kw) and answers from <answers>, keyed by
    (basename, first argument or None) -> (code, stdout); extract-result.sh answers <report>."""

    def __init__(self, answers=None, report="SUITE: make unit 1 passed\n"):
        self.answers, self.calls, self.report, self.paths = dict(answers or {}), [], report, []

    def __call__(self, name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        self.calls.append((base, args, cwd, env, kw))
        self.paths.append(name)
        for (script, first), (code, out) in self.answers.items():
            if base == script and (first is None or args[:1] == (first,)):
                return code, out, ""
        if base == "git" and args[:2] == ("log", "-1"):
            return 0, STEP_BASE + "\n", ""
        if base == "extract-result.sh":
            return 0, self.report, ""
        if base == "stop-requested.sh":
            return 3, "", ""
        if base == "diff-leaf-deviation.sh":
            return 3, "", ""
        if base == "detect-test-command.sh":
            return 0, "make test TESTS=\"$1\"\n", ""
        if base == "step-tick.sh":
            return 0, "tick-ledger.sh .tdd/issue-12.md exit 0\nnext=cycle\n", ""
        return 0, "", ""

    def names(self):
        return [c[0] for c in self.calls]

    def call(self, base, first=None):
        return next(c for c in self.calls if c[0] == base and (first is None or c[1][:1] == (first,)))

    def launched(self):
        return [c[1][1] for c in self.calls if c[0] == "detach-leaf.sh"]


@pytest.fixture
def diff(monkeypatch, run_cli, tmp_path):
    """diff(answers=None, fake=None, step=STEP, skip=None, argv=("12",)) runs diff-step for issue 12 from the main tree,
    the run's worktree at .tdd/wt/12; returns (code, stdout, stderr, fake)."""
    fused = importlib.import_module("veri.fused")
    module = importlib.import_module("veri.diff_step")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)

    def go(answers=None, fake=None, step=STEP, skip=None, argv=("12",), report=None):
        files = {(wt / ".tdd" / "issue-12-branch-base"): BRANCH_BASE + "\n",
                 (wt / ".tdd" / "issue-12-preflight"): "worktree=%s\nfast_cmd=make unit\n" % wt,
                 (wt / ".tdd" / "issue-12.md"): LEDGER % step,
                 (wt / ".tdd" / "issue-12-spec.md"): "# spec\n",
                 (wt / ".tdd" / "develop-diff.out"): "MARKER-4435 leaf output\n" + FLIP}
        for path, text in files.items():
            if not path.exists():
                path.write_text(text)
        if skip is not None:
            (wt / ".tdd" / "issue-12-skip-verify").write_text(skip + "\n")
        fake = fake or Fake(answers, **({"report": report} if report is not None else {}))
        monkeypatch.setattr(fused, "run_script", fake)
        code, out, err = run_cli(module, list(argv), cwd=str(tmp_path))
        return code, out, err, fake

    go.wt = wt
    return go


def _short(args):
    return tuple(os.path.basename(a) if a.endswith(".sh") else a for a in args)


def _clean(diff, step=STEP, **kw):
    """The three calls of a clean step: the leaf's launch, its wait and the verifier's launch, the verifier's wait and
    the close; each returns (code, stdout, stderr, fake)."""
    first = diff(step=step, answers={("wait-leaf.sh", "develop-diff"): (3, "")}, **kw)
    second = diff(step=step, answers={("wait-leaf.sh", "verdict-diff"): (3, "")}, **kw)
    third = diff(step=step, **kw)
    return first, second, third


@pytest.mark.parametrize("step", [STEP, LINT])
def test_4435_a_diff_checked_step_runs_its_clean_path_in_order_over_three_sliced_calls_ending_on_step_ticks_next(
        diff, step):
    """DST1, DST2, DST5: the step base from the ledger's last commit, the develop-diff leaf, suite-reported.sh,
    diff-leaf-deviation.sh, the verdict-diff verifier, pin-recheck.sh, then step-tick.sh; each wait sliced."""
    first, second, third = _clean(diff, step)

    assert (first[0], first[1].splitlines()[-1]) == (3, "waiting on develop-diff")
    calls = [(c[0], _short(c[1])) for c in first[3].calls]
    assert calls[0] == ("git", ("log", "-1", "--format=%H", "--", ".tdd/issue-12.md"))
    assert calls[1] == ("build-develop-prompt.sh", ("diff", ".tdd/issue-12-spec.md", step, "make unit", "make unit"))
    assert first[3].call("build-develop-prompt.sh")[4]["out"] == ".tdd/develop-diff.prompt"
    launch = first[3].call("detach-leaf.sh")
    assert _short(launch[1]) == ("supervise.sh", "develop-diff", "run-leaf.sh", ".tdd/develop-diff.prompt",
                                 "--permission-mode", "bypassPermissions")
    assert (launch[3]["VERI_ISSUE"], launch[3]["VERI_STEP"]) == ("12", step)
    assert (launch[4]["out"], launch[4]["err"]) == (".tdd/develop-diff.out", ".tdd/develop-diff.err")

    assert (second[0], second[1].splitlines()[-1]) == (3, "waiting on verdict-diff")
    calls = [(c[0], _short(c[1])) for c in second[3].calls]
    assert calls[:3] == [("wait-leaf.sh", ("develop-diff",)), ("suite-reported.sh", ("develop-diff",)),
                         ("diff-leaf-deviation.sh", ("develop-diff", STEP_BASE, ".tdd/issue-12.md"))]
    verdict = second[3].call("detach-leaf.sh")
    assert _short(verdict[1]) == ("supervise.sh", "verdict-diff", "run-verdict.sh", "--step", step, "--fast-cmd",
                                  "make unit", "--branch-base", BRANCH_BASE, "diff", ".tdd/issue-12-spec.md",
                                  STEP_BASE)
    assert (verdict[4]["out"], verdict[4]["err"]) == (".tdd/verify-diff.reason", ".tdd/verify-diff.err")

    assert third[0] == 0, third[2]
    calls = [(c[0], _short(c[1])) for c in third[3].calls]
    assert calls == [("wait-leaf.sh", ("verdict-diff",)),
                     ("pin-recheck.sh", ("--branch-base", BRANCH_BASE, STEP_BASE)),
                     ("step-tick.sh", ("12",))]
    scripts = os.path.dirname(os.path.dirname(os.path.realpath(importlib.import_module("veri.fused").__file__)))
    assert third[3].paths[-1] == os.path.join(scripts, "step-tick.sh")
    assert third[1].splitlines()[-1] == "next=cycle"
    for _, out, _, fake in (first, second, third):
        assert not [c for c in fake.calls if c[0] == "git" and c[1][:1] in (("reset",), ("commit",), ("rebase",))]
        assert "MARKER-4435" not in out
