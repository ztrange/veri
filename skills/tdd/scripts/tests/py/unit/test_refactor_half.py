"""In-process cases for veri/refactor_half.py, the module refactor-half.sh is a shim over (PRD 027.6, #4028)."""
import importlib
import json
import os

import pytest

STEP = "one thing works ⟦criterion 1⟧"
LEDGER = "# Plan for #12\n\n- [x] %s ⟂ refactor pending\n- [ ] two ⟦criterion 2⟧\n"
RED_HALF = ("step=%s\ntest_path=tests/test_a.py\ntarget_test=tests/test_a.py::test_one\n"
            "red_test_id=tests/test_a.py::test_one\nagainst_unmodified=FAILS\n")
GREEN_SHA = "d" * 40
TOUCHED = "src/a.py,tests/test_a.py"
REPORT = ("RESULT: extract f\nCANDIDATES: structural | src/a.py | split g\nCANDIDATES: cosmetic | src/a.py | rename h\n"
          "CANDIDATES: structural | src/a.py | inline k\nFLAGS: beyond-spec | negative sizes\n"
          "FLAGS: uncovered-spec | empty input returns 0\n")
VERDICT = "FLAGS: overfit | the size is hard-coded\nFLAGS: uncovered-spec | a tab separates too\nVERDICT: PASS\n"


class Fake:
    """A run_script stand-in: records (basename, args, cwd, env, kw) and answers from <answers>, keyed by
    (basename, first argument or None) -> (code, stdout)."""

    def __init__(self, answers=None, report=REPORT, verdict=VERDICT, porcelain="", subjects="refactor: extract f (#12)\n",
                 count="1\n"):
        self.answers, self.calls = dict(answers or {}), []
        self.report, self.verdict, self.porcelain, self.subjects, self.count = report, verdict, porcelain, subjects, count

    def __call__(self, name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        self.calls.append((base, args, cwd, env, kw))
        for (script, first), (code, out) in self.answers.items():
            if base == script and (first is None or args[:1] == (first,)):
                return code, out, ""
        if base == "extract-result.sh":
            return 0, self.verdict if "VERDICT" in kw.get("stdin", "") else self.report, ""
        if base == "refactor-budget.sh":
            return 0, "refactor 0/5 — another transform may run\n", ""
        if base == "refactor-touched.sh":
            return 0, TOUCHED + "\n", ""
        if base == "git" and args[:2] == ("log", "-1"):
            return 0, GREEN_SHA + "\n", ""
        if base == "git" and args[:1] == ("log",):
            return 0, self.subjects, ""
        if base == "git" and args[:1] == ("rev-list",):
            return 0, self.count, ""
        if base == "git" and args == ("status", "--porcelain"):
            return 0, self.porcelain, ""
        if base in ("stop-requested.sh", "refactor-triage.sh"):
            return 3, "", ""
        return 0, "", ""

    def names(self):
        return [c[0] for c in self.calls]

    def call(self, base, first=None):
        return next(c for c in self.calls if c[0] == base and (first is None or c[1][:1] == (first,)))

    def launched(self):
        return [c[1][1] for c in self.calls if c[0] == "detach-leaf.sh"]


@pytest.fixture
def tidy(monkeypatch, run_cli, tmp_path):
    """tidy(answers=None, fake=None, missing=(), step=STEP, red_step=None, argv=None) runs refactor-half for issue
    12 from the main tree, the run's worktree at .tdd/wt/12; returns (code, stdout, stderr, fake)."""
    fused = importlib.import_module("veri.fused")
    refactor_half = importlib.import_module("veri.refactor_half")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)

    def go(answers=None, fake=None, missing=(), step=STEP, red_step=None, argv=None):
        files = {"preflight": (wt / ".tdd" / "issue-12-preflight", "worktree=%s\nfast_cmd=make unit\n" % wt),
                 "ledger": (wt / ".tdd" / "issue-12.md", LEDGER % step),
                 "spec": (wt / ".tdd" / "issue-12-spec.md", "# spec\n"),
                 "red-half": (wt / ".tdd" / "issue-12-red-half", RED_HALF % (red_step or step)),
                 "out": (wt / ".tdd" / "develop-refactor.out", "{\"report\": 1}\n"),
                 "log": (wt / ".tdd" / "verify-refactor.log", "{\"VERDICT\": 1}\n")}
        for key, (path, text) in files.items():
            if key not in missing and not path.exists():
                path.write_text(text)
        fake = fake or Fake(answers)
        monkeypatch.setattr(fused, "run_script", fake)
        code, out, err = run_cli(refactor_half, list(argv if argv is not None else ("12",)), cwd=str(tmp_path))
        return code, out, err, fake

    go.wt = wt
    return go


def test_4028_no_argument_prints_the_usage_and_exits_2_with_no_inner_call(tidy):
    code, out, err, fake = tidy(argv=())

    assert (code, "refactor-half.sh <n>" in err, fake.calls) == (2, True, [])
    here = os.path.dirname(importlib.import_module("veri.refactor_half").__file__)
    assert os.path.exists(os.path.join(here, "..", "refactor-half.sh"))


@pytest.mark.parametrize("missing, named", [("preflight", ".tdd/issue-12-preflight"), ("ledger", ".tdd/issue-12.md"),
                                            ("spec", ".tdd/issue-12-spec.md"), ("red-half", ".tdd/issue-12-red-half")])
def test_4028_a_missing_input_is_exit_2_before_any_inner_call_named_on_stderr(tidy, missing, named):
    code, out, err, fake = tidy(missing=(missing,))

    assert (code, fake.calls) == (2, [])
    assert named in err


def test_4028_a_red_half_file_naming_another_step_is_exit_2_before_any_inner_call(tidy):
    code, out, err, fake = tidy(red_step="zero ⟦criterion 1⟧")

    assert (code, fake.calls) == (2, [])


def test_4028_no_refactor_pending_step_is_exit_2_before_any_inner_call(tidy):
    (tidy.wt / ".tdd" / "issue-12.md").write_text("# Plan\n\n- [x] %s\n- [ ] two ⟦criterion 2⟧\n" % STEP)
    code, out, err, fake = tidy()

    assert (code, fake.calls) == (2, [])
