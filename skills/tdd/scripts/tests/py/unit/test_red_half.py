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


DEVELOP_ONLY = {("wait-leaf.sh", "verdict-red"): (3, "")}


def _seq(fake):
    return [(c[0], c[1][:1]) for c in fake.calls]


def test_4026_it_refreshes_the_spec_builds_the_red_prompt_checks_for_a_stop_and_launches_develop_red(red):
    for name in ("develop-red.exit", "develop-red.pid", "red-prediction.md", "red-run-output.txt"):
        (red.wt / ".tdd" / name).write_text("old\n")
    code, out, err, fake = red(answers=DEVELOP_ONLY)

    assert [c[0] for c in fake.calls[:5]] == ["refresh-spec.sh", "build-develop-prompt.sh", "stop-requested.sh",
                                              "detach-leaf.sh", "wait-leaf.sh"]
    assert fake.calls[0][1] == ("12", ".tdd/issue-12-spec.md")
    assert fake.calls[1][1] == ("red", ".tdd/issue-12-spec.md", STEP, "make unit")
    assert fake.calls[1][4]["out"] == ".tdd/develop-red.prompt"
    assert fake.calls[4][1] == ("develop-red",)
    launch = fake.calls[3]
    assert tuple(os.path.basename(a) if a.endswith(".sh") else a for a in launch[1]) == (
        "supervise.sh", "develop-red", "run-leaf.sh", ".tdd/develop-red.prompt", "--permission-mode",
        "bypassPermissions")
    assert all(os.path.isabs(a) for a in launch[1] if a.endswith(".sh"))
    assert (launch[3]["VERI_TEST_CMD"], launch[3]["VERI_ISSUE"], launch[3]["VERI_STEP"]) == ("make unit", "12", STEP)
    assert (launch[4]["out"], launch[4]["err"]) == (".tdd/develop-red.out", ".tdd/develop-red.err")
    assert not [n for n in ("develop-red.exit", "develop-red.pid", "red-prediction.md", "red-run-output.txt")
                if (red.wt / ".tdd" / n).exists()]
    assert {c[2] for c in fake.calls} == {str(red.wt)}


@pytest.mark.parametrize("refresh", [0, 2, 3])
def test_4026_refresh_spec_exits_0_2_and_3_go_on(red, refresh):
    code, out, err, fake = red(answers={**DEVELOP_ONLY, ("refresh-spec.sh", None): (refresh, "")})

    assert "develop-red" in fake.launched()


def test_4026_refresh_spec_exit_1_stops_it_before_any_launch(red):
    code, out, err, fake = red(answers={("refresh-spec.sh", None): (1, "")})

    assert (code, fake.names()) == (1, ["refresh-spec.sh"])
    assert out.splitlines()[-1] == "stopped at 1 refresh-spec.sh 12 .tdd/issue-12-spec.md exit 1"


@pytest.mark.parametrize("code, mode, launches", [(3, "", True), (0, "at-ledger\n", True), (0, "at-leaf\n", False),
                                                  (0, "now\n", False), (2, "", False)])
def test_4026_the_stop_check_before_develop_red(red, code, mode, launches):
    got, out, err, fake = red(answers={**DEVELOP_ONLY, ("stop-requested.sh", None): (code, mode)})

    assert ("develop-red" in fake.launched()) == launches
    if not launches:
        assert (got, fake.names()[-1]) == (2 if code == 2 else 1, "stop-requested.sh")
        assert out.splitlines()[-1].startswith("stopped at 1 stop-requested.sh")


@pytest.mark.parametrize("leaf", [1, 2])
def test_4026_a_develop_red_wait_exit_1_or_2_stops_it(red, leaf):
    code, out, err, fake = red(answers={("wait-leaf.sh", "develop-red"): (leaf, "")})

    assert (code, fake.names()[-1], out.splitlines()[-1]) == (
        leaf, "wait-leaf.sh", "stopped at 1 wait-leaf.sh develop-red exit %d" % leaf)


def test_4026_after_the_wait_it_checks_the_steps_cost_then_prints_the_reports_three_lines(red):
    code, out, err, fake = red(answers=DEVELOP_ONLY)

    names = fake.names()
    at = names.index("wait-leaf.sh")
    assert names[at + 1:at + 4] == ["step-cost.sh", "step-budget.sh", "extract-result.sh"]
    assert fake.call("step-cost.sh")[1] == (STEP,)
    assert fake.call("extract-result.sh")[4]["stdin"] == "{}\n"
    lines = out.splitlines()
    shown = lines.index("extract-result.sh < .tdd/develop-red.out exit 0")
    assert lines[shown + 1:shown + 4] == ["test_path=tests/test_a.py", "target_test=tests/test_a.py::test_one",
                                          "against_unmodified=FAILS"]
    assert "WHY: because" not in out and "{}" not in out


def test_4026_a_cost_over_the_step_budget_stops_it_at_the_cost_check_with_both_figures(red):
    code, out, err, fake = red(fake=Fake(cost="12.50\n"))

    assert (code, fake.names()[-1]) == (1, "step-budget.sh")
    assert out.splitlines()[-1] == "stopped at cost-check spent 12.50 over the step budget 12"


def test_4026_a_step_that_already_crossed_its_budget_goes_on_past_an_over_budget_figure(red):
    (red.wt / ".tdd" / "events.jsonl").write_text(
        json.dumps({"event": "step-over-budget", "step": STEP, "spent": "13", "budget": "12"}) + "\n")
    code, out, err, fake = red(fake=Fake(DEVELOP_ONLY, cost="12.50\n"))

    assert "extract-result.sh" in fake.names()


@pytest.mark.parametrize("cost, goes_on", [(3, True), (2, False)])
def test_4026_step_cost_exit_3_goes_on_and_exit_2_stops_it(red, cost, goes_on):
    code, out, err, fake = red(answers={**DEVELOP_ONLY, ("step-cost.sh", None): (cost, "")})

    assert ("extract-result.sh" in fake.names()) == goes_on
    if not goes_on:
        assert (code, out.splitlines()[-1].startswith("stopped at cost-check step-cost.sh")) == (2, True)


@pytest.mark.parametrize("against", ["PASSES", "UNTESTABLE"])
def test_4026_passes_or_untestable_stops_it_with_exit_1(red, against):
    code, out, err, fake = red(fake=Fake(report=REPORT.replace("FAILS", against)))

    assert (code, fake.names()[-1]) == (1, "extract-result.sh")
    assert out.splitlines()[-1] == "stopped at 2 AGAINST_UNMODIFIED: " + against


@pytest.mark.parametrize("line", ["TEST_PATH:", "TARGET_TEST:", "AGAINST_UNMODIFIED:"])
def test_4026_a_missing_report_line_stops_it_with_exit_2(red, line):
    report = "".join(part + "\n" for part in REPORT.splitlines() if not part.startswith(line))
    code, out, err, fake = red(fake=Fake(report=report))

    assert (code, fake.names()[-1]) == (2, "extract-result.sh")
    assert out.splitlines()[-1] == "stopped at 1 no %s line" % line
