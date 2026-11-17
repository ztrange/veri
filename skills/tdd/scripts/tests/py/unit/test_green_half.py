"""In-process cases for veri/green_half.py, the module green-half.sh is a shim over (PRD 027.5, #4027)."""
import importlib
import json
import os

import pytest

STEP = "one thing works ⟦criterion 1⟧"
LEDGER = "# Plan for #12\n\n- [x] zero ⟦criterion 1⟧\n- [ ] %s\n- [ ] two ⟦criterion 2⟧\n"
RED_HALF = ("step=%s\ntest_path=tests/test_a.py\ntarget_test=tests/test_a.py::test_one\n"
            "red_test_id=tests/test_a.py::test_one\nagainst_unmodified=FAILS\n")
REPORT = "IMPL_PATH: src/a.py\nSUITE: GREEN 3 passed\n"
GREEN_SHA = "d" * 40
BASE_SHA = "b" * 40
PR_URL = "https://github.com/o/r/pull/77"


class Fake:
    """A run_script stand-in: records (basename, args, cwd, env, kw) and answers from <answers>, keyed by
    (basename, first argument or None) -> (code, stdout). tick-ledger.sh ticks the ledger file as the real one does."""

    def __init__(self, answers=None, report=REPORT, cost="1.00\n", wt=None):
        self.answers, self.calls, self.report, self.cost, self.wt = dict(answers or {}), [], report, cost, wt

    def __call__(self, name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        self.calls.append((base, args, cwd, env, kw))
        for (script, first), (code, out) in self.answers.items():
            if base == script and (first is None or args[:1] == (first,)):
                return code, out, ""
        if base == "extract-result.sh":
            return 0, self.report, ""
        if base == "tick-ledger.sh":
            path = os.path.join(cwd, args[1])
            with open(path) as f:
                text = f.read()
            with open(path, "w") as f:
                f.write(text.replace("- [ ] " + args[2], "- [x] " + args[2] + " ⟂ refactor pending", 1))
            return 0, "", ""
        if base == "git" and args[:1] == ("log",):
            return 0, BASE_SHA + "\n", ""
        if base == "git" and args == ("rev-parse", "HEAD"):
            return 0, GREEN_SHA + "\n", ""
        if base == "git" and args == ("branch", "--show-current"):
            return 0, "tdd/12-a-thing\n", ""
        if base == "gh":
            return 0, PR_URL + "\n", ""
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
def green(monkeypatch, run_cli, tmp_path):
    """green(answers=None, fake=None, missing=(), step=STEP, red_step=None, spec="# spec\n", argv=None) runs
    green-half for issue 12 from the main tree, the run's worktree at .tdd/wt/12; returns (code, stdout, stderr,
    fake)."""
    fused = importlib.import_module("veri.fused")
    green_half = importlib.import_module("veri.green_half")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)

    def go(answers=None, fake=None, missing=(), step=STEP, red_step=None, spec="# spec\n", argv=None):
        files = {"preflight": (wt / ".tdd" / "issue-12-preflight", "worktree=%s\nfast_cmd=make unit\n" % wt),
                 "ledger": (wt / ".tdd" / "issue-12.md", LEDGER % step),
                 "spec": (wt / ".tdd" / "issue-12-spec.md", spec),
                 "red-half": (wt / ".tdd" / "issue-12-red-half", RED_HALF % (red_step or step)),
                 "out": (wt / ".tdd" / "develop-green.out", "{}\n")}
        for key, (path, text) in files.items():
            if key not in missing and not path.exists():
                path.write_text(text)
        fake = fake or Fake(answers)
        monkeypatch.setattr(fused, "run_script", fake)
        code, out, err = run_cli(green_half, list(argv if argv is not None else ("12",)), cwd=str(tmp_path))
        return code, out, err, fake

    go.wt = wt
    return go


def test_4027_no_argument_prints_the_usage_and_exits_2_with_no_inner_call(green):
    code, out, err, fake = green(argv=())

    assert (code, "green-half.sh <n>" in err, fake.calls) == (2, True, [])
    here = os.path.dirname(importlib.import_module("veri.green_half").__file__)
    assert os.path.exists(os.path.join(here, "..", "green-half.sh"))


@pytest.mark.parametrize("missing, named", [("preflight", ".tdd/issue-12-preflight"), ("ledger", ".tdd/issue-12.md"),
                                            ("spec", ".tdd/issue-12-spec.md"), ("red-half", ".tdd/issue-12-red-half")])
def test_4027_a_missing_input_is_exit_2_before_any_inner_call_named_on_stderr(green, missing, named):
    code, out, err, fake = green(missing=(missing,))

    assert (code, fake.calls) == (2, [])
    assert named in err


def test_4027_a_red_half_file_naming_another_step_is_exit_2_before_any_inner_call(green):
    code, out, err, fake = green(red_step="zero ⟦criterion 1⟧")

    assert (code, fake.calls) == (2, [])
    assert "red-half" in err


@pytest.mark.parametrize("step", ["port: replaces 'a' in tests/py/test_x.py ⟦replaces-case⟧ ⟦criterion 1⟧",
                                  "fix the CI job ⟦ci-repair⟧ ⟦criterion 1⟧"])
def test_4027_a_replaces_case_or_ci_repair_step_is_exit_2_before_any_inner_call(green, step):
    code, out, err, fake = green(step=step)

    assert (code, fake.calls) == (2, [])
