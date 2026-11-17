"""In-process cases for veri/red_half.py, the module red-half.sh is a shim over (PRD 027.4, #4026)."""
import importlib
import json
import os

import pytest

STEP = "one thing works ⟦criterion 1⟧"
LEDGER = "# Plan for #12\n\n- [x] zero ⟦criterion 1⟧\n- [ ] %s\n- [ ] two ⟦criterion 2⟧\n"
REPORT = ("TEST_PATH: tests/test_a.py\nTARGET_TEST: tests/test_a.py::test_one\nAGAINST_UNMODIFIED: FAILS\n"
          "WHY: because\nFAIL_OUTPUT: boom\n")


class Fake:
    """A run_script stand-in: records (basename, args, cwd, env, kw) and answers from <answers>, keyed by
    (basename, first argument or None) -> (code, stdout)."""

    def __init__(self, answers=None, porcelain="?? tests/test_a.py\n M .tdd/x\n", report=REPORT, cost="1.00\n"):
        self.answers, self.calls, self.porcelain, self.report, self.cost = dict(answers or {}), [], porcelain, report, cost

    def __call__(self, name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        self.calls.append((base, args, cwd, env, kw))
        for (script, first), (code, out) in self.answers.items():
            if base == script and (first is None or args[:1] == (first,)):
                return code, out, ""
        if base == "extract-result.sh":
            return 0, self.report, ""
        if base == "git" and args == ("status", "--porcelain"):
            return 0, self.porcelain, ""
        if base in ("stop-requested.sh", "red-divergence.sh"):
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
def red(monkeypatch, run_cli, tmp_path):
    """red(answers=None, fake=None, missing=(), step=STEP, argv=None) runs red-half for issue 12 from the main tree,
    the run's worktree at .tdd/wt/12; returns (code, stdout, stderr, fake)."""
    fused = importlib.import_module("veri.fused")
    red_half = importlib.import_module("veri.red_half")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)

    def go(answers=None, fake=None, missing=(), step=STEP, argv=None):
        files = {"preflight": (wt / ".tdd" / "issue-12-preflight", "worktree=%s\nfast_cmd=make unit\n" % wt),
                 "ledger": (wt / ".tdd" / "issue-12.md", LEDGER % step),
                 "spec": (wt / ".tdd" / "issue-12-spec.md", "# spec\n"),
                 "out": (wt / ".tdd" / "develop-red.out", "{}\n")}
        for key, (path, text) in files.items():
            if key not in missing and not path.exists():
                path.write_text(text)
        fake = fake or Fake(answers)
        monkeypatch.setattr(fused, "run_script", fake)
        code, out, err = run_cli(red_half, list(argv if argv is not None else ("12",)), cwd=str(tmp_path))
        return code, out, err, fake

    go.wt = wt
    return go


def test_4026_no_argument_prints_the_usage_and_exits_2_with_no_inner_call(red):
    code, out, err, fake = red(argv=())

    assert (code, "red-half.sh <n>" in err, fake.calls) == (2, True, [])
    here = os.path.dirname(importlib.import_module("veri.red_half").__file__)
    assert os.path.exists(os.path.join(here, "..", "red-half.sh"))


@pytest.mark.parametrize("missing, named", [("preflight", ".tdd/issue-12-preflight"), ("ledger", ".tdd/issue-12.md"),
                                            ("spec", ".tdd/issue-12-spec.md")])
def test_4026_a_missing_input_is_exit_2_before_any_inner_call_named_on_stderr(red, missing, named):
    code, out, err, fake = red(missing=(missing,))

    assert (code, fake.calls) == (2, [])
    assert named in err


@pytest.mark.parametrize("step", ["re-pin it ⟦diff-checked⟧ ⟦criterion 1⟧", "phased ⟦phases: expand, migrate⟧",
                                  "⟦skill-edit⟧ `skills/tdd/SKILL.md` ⟦criterion 1⟧",
                                  "fix: repairs the fixture 'f' in tests/test_a.py, x ⟦fixture-repair⟧"])
def test_4026_a_step_of_a_kind_it_leaves_to_the_prose_is_exit_2_before_any_inner_call(red, step):
    code, out, err, fake = red(step=step)

    assert (code, fake.calls) == (2, [])
    assert "red-half.sh" in err


def test_4026_no_open_step_is_exit_2_before_any_inner_call(red):
    (red.wt / ".tdd").mkdir(parents=True, exist_ok=True)
    (red.wt / ".tdd" / "issue-12.md").write_text("# Plan\n\n- [x] done ⟦criterion 1⟧\n")
    code, out, err, fake = red()

    assert (code, fake.calls) == (2, [])
