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
        if base == "git" and args == ("status", "--porcelain", "--untracked-files=all"):
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


BRANCH_BASE = "abc1234"  # the run's recorded branch base (#4375)


@pytest.fixture
def red(monkeypatch, run_cli, tmp_path):
    """red(answers=None, fake=None, missing=(), step=STEP, argv=None) runs red-half for issue 12 from the main tree,
    the run's worktree at .tdd/wt/12; returns (code, stdout, stderr, fake)."""
    fused = importlib.import_module("veri.fused")
    red_half = importlib.import_module("veri.red_half")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)

    def go(answers=None, fake=None, missing=(), step=STEP, argv=None):
        files = {"branch_base": (wt / ".tdd" / "issue-12-branch-base", BRANCH_BASE + "\n"),
                 "preflight": (wt / ".tdd" / "issue-12-preflight", "worktree=%s\nfast_cmd=make unit\n" % wt),
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


REPLACES = "port it: replaces 'case one' and 'case two' in tests/py/test_x.py ⟦replaces-case⟧ ⟦criterion 1⟧"


def _after(fake, name, first=None):
    at = fake.calls.index(fake.call(name, first))
    return fake.calls[at + 1:]


def test_4026_the_prediction_gate_runs_on_the_report_into_the_verify_red_reason(red):
    code, out, err, fake = red()

    gate = fake.call("red-divergence.sh")
    assert gate[1] == (".tdd/red-prediction.md", ".tdd/red-run-output.txt")
    assert (gate[4]["stdin"], gate[4]["out"]) == ("{}\n", ".tdd/verify-red.reason")


@pytest.mark.parametrize("gate, stop", [(0, 1), (1, 1), (2, 2)])
def test_4026_a_prediction_gate_exit_0_1_or_2_stops_it_with_no_verifier(red, gate, stop):
    code, out, err, fake = red(answers={("red-divergence.sh", None): (gate, "")})

    assert (code, fake.names()[-1], "verdict-red" in fake.launched()) == (stop, "red-divergence.sh", False)
    assert out.splitlines()[-1].startswith("stopped at 2 red-divergence.sh")


def test_4026_an_ordinary_step_runs_no_unreplaced_check_and_no_except(red):
    code, out, err, fake = red()

    assert "unreplaced-cases.sh" not in fake.names()
    assert fake.call("tests-frozen.sh", "check-earlier")[1] == ("check-earlier", ".tdd/issue-12.md", "--step", STEP)


def test_4026_a_replaces_case_step_checks_its_replaced_cases_and_excepts_each_from_the_earlier_check(red):
    code, out, err, fake = red(step=REPLACES)

    assert fake.call("unreplaced-cases.sh")[1] == (REPLACES, ".tdd/develop-red.out")
    assert fake.call("tests-frozen.sh", "check-earlier")[1] == (
        "check-earlier", ".tdd/issue-12.md", "--step", REPLACES, "--except", "case one", "--except", "case two")
    assert code == 0


@pytest.mark.parametrize("check", [1, 2])
def test_4026_an_unreplaced_cases_exit_1_or_2_stops_it_with_no_verifier(red, check):
    code, out, err, fake = red(step=REPLACES, answers={("unreplaced-cases.sh", None): (check, "")})

    assert (code, fake.names()[-1], "verdict-red" in fake.launched()) == (check, "unreplaced-cases.sh", False)


@pytest.mark.parametrize("check", [1, 2])
def test_4026_an_earlier_steps_check_exit_1_or_2_stops_it_with_no_verifier(red, check):
    code, out, err, fake = red(answers={("tests-frozen.sh", "check-earlier"): (check, "")})

    assert (code, fake.names()[-1], "verdict-red" in fake.launched()) == (check, "tests-frozen.sh", False)
    assert out.splitlines()[-1].startswith("stopped at 2 tests-frozen.sh check-earlier")


def test_4026_it_launches_verdict_red_with_red_2s_arguments_only(red):
    code, out, err, fake = red()

    launch = [c for c in fake.calls if c[0] == "detach-leaf.sh"][1]
    assert tuple(os.path.basename(a) if a.endswith(".sh") else a for a in launch[1]) == (
        "supervise.sh", "verdict-red", "run-verdict.sh", "--step", STEP, "--fast-cmd", "make unit",
        "--branch-base", BRANCH_BASE, "red",
        ".tdd/issue-12-spec.md", "tests/test_a.py", "tests/test_a.py::test_one")
    assert (launch[3]["VERI_TEST_CMD"], launch[3]["VERI_STEP"]) == ("make unit", STEP)
    assert (launch[4]["out"], launch[4]["err"]) == (".tdd/verify-red.reason", ".tdd/verify-red.err")
    assert [c[0] for c in _after(fake, "tests-frozen.sh", "check-earlier")[:4]] == [
        "stop-requested.sh", "detach-leaf.sh", "wait-leaf.sh", "step-cost.sh"]


def test_4375_a_missing_branch_base_record_stops_it_with_exit_2_naming_the_record_and_launches_no_verdict(red):
    code, out, err, fake = red(missing=("branch_base",))

    assert (code, out.splitlines()[-1], fake.launched()) == (
        2, "stopped at 2 branch-base record of issue 12", ["develop-red"])


@pytest.mark.parametrize("verdict", [1, 2])
def test_4026_a_verdict_of_1_or_2_stops_it_before_any_record_or_comment(red, verdict):
    code, out, err, fake = red(answers={("wait-leaf.sh", "verdict-red"): (verdict, "")})

    assert (code, out.splitlines()[-1]) == (verdict, "stopped at 2 wait-leaf.sh verdict-red exit %d" % verdict)
    assert not {"comment.sh", "red-setup.sh"} & set(fake.names())
    assert ("tests-frozen.sh", ("record",)) not in [(c[0], c[1][:1]) for c in fake.calls]


def test_4026_a_pass_records_the_frozen_tests_with_the_red_case_into_the_verify_red_reason(red):
    code, out, err, fake = red()

    record = fake.call("tests-frozen.sh", "record")
    assert record[1] == ("record", "--step", STEP, "--red-case", "tests/test_a.py::test_one", "tests/test_a.py")
    assert record[4]["out"] == ".tdd/verify-red.reason"
    assert fake.call("red-setup.sh")[1] == ("record", "12")


def test_4026_a_bare_target_test_is_joined_to_its_path_for_the_red_case(red):
    code, out, err, fake = red(fake=Fake(report=REPORT.replace("TARGET_TEST: tests/test_a.py::", "TARGET_TEST: ")))

    assert fake.call("tests-frozen.sh", "record")[1][4] == "tests/test_a.py::test_one"


@pytest.mark.parametrize("recorded", [1, 2])
def test_4026_a_record_exit_1_or_2_stops_it_before_any_comment(red, recorded):
    code, out, err, fake = red(answers={("tests-frozen.sh", "record"): (recorded, "")})

    assert (code, fake.names()[-1]) == (recorded, "tests-frozen.sh")


@pytest.mark.parametrize("porcelain", [" M src/a.py\n", "?? lib/b.py\n?? tests/test_a.py\n"])
def test_4026_a_production_path_in_the_tree_stops_it_at_3_tree_check_before_any_comment(red, porcelain):
    code, out, err, fake = red(fake=Fake(porcelain=porcelain))

    assert (code, out.splitlines()[-1], "comment.sh" in fake.names()) == (1, "stopped at 3 tree-check", False)


def test_4026_on_a_clean_path_it_posts_red_with_a_note_then_verify_red_and_settles_last(red):
    code, out, err, fake = red(answers={("refresh-spec.sh", None): (2, "")})

    comments = [c for c in fake.calls if c[0] == "comment.sh"]
    assert [c[1][:2] for c in comments] == [("12", "red"), ("12", "verify-red")]
    assert comments[0][1][2:] == ("--note-file", ".tdd/red-half-note.md")
    note = (red.wt / ".tdd" / "red-half-note.md").read_text()
    assert "capture" in note and "prediction matched" in note.lower()
    expected = ["step=" + STEP, "test_path=tests/test_a.py", "target_test=tests/test_a.py::test_one",
                "red_test_id=tests/test_a.py::test_one", "against_unmodified=FAILS"]
    assert code == 0
    assert (red.wt / ".tdd" / "issue-12-red-half").read_text().splitlines() == expected
    assert out.splitlines()[-len(expected):] == expected
    assert fake.names()[-1] == "comment.sh"


def test_4026_a_refreshed_spec_is_named_in_the_note(red):
    red()

    assert "refreshed" in (red.wt / ".tdd" / "issue-12-red-half").parent.joinpath("red-half-note.md").read_text()


def test_4026_it_commits_and_ticks_nothing(red):
    code, out, err, fake = red()

    assert code == 0
    assert not [c for c in fake.calls if c[0] == "git" and c[1][:1] != ("status",)]
    assert not {"tick-ledger.sh", "push-branch.sh"} & set(fake.names())
    assert "- [ ] " + STEP in (red.wt / ".tdd" / "issue-12.md").read_text()


def test_4026_with_red_switched_off_it_marks_the_skip_and_launches_no_verdict_red(red):
    (red.wt / ".tdd" / "issue-12-skip-verify").write_text("red\n")
    code, out, err, fake = red()

    assert (code, fake.launched()) == (0, ["develop-red"])
    mark = fake.call("event.sh")
    assert mark[1] == ("verify-red-skipped", "reason=switched-off")
    assert (mark[3]["VERI_ACTOR"], mark[3]["VERI_STEP"], mark[3]["VERI_ISSUE"]) == ("conductor", STEP, "12")
    assert (red.wt / ".tdd" / "verdict-red.exit").read_text().strip() == "skipped"
    assert [c[0] for c in _after(fake, "event.sh")][:2] == ["tests-frozen.sh", "red-setup.sh"]


def test_4026_it_launches_no_leaf_but_through_supervise(red):
    code, out, err, fake = red()

    assert not {"run-leaf.sh", "run-verdict.sh", "claude", "supervise.sh"} & set(fake.names())
    assert fake.launched() == ["develop-red", "verdict-red"]


def test_4026_it_writes_no_bail_and_resets_nothing_on_a_stop(red):
    code, out, err, fake = red(answers={("wait-leaf.sh", "verdict-red"): (1, "")})

    assert not {"classify-bail.sh", "preflight-refused.sh", "event.sh"} & set(fake.names())
    assert not [c for c in fake.calls if c[0] == "git" and c[1][:1] in (("reset",), ("clean",))]


def _pid(red, text):
    (red.wt / ".tdd" / "conductor.pid").write_text(text)


@pytest.mark.parametrize("leaf", ["develop-red", "verdict-red"])
def test_4026_a_wait_whose_slice_ran_out_exits_3_on_a_waiting_on_line(red, leaf):
    code, out, err, fake = red(answers={("wait-leaf.sh", leaf): (3, "")})

    assert (code, out.splitlines()[-1]) == (3, "waiting on " + leaf)
    assert not (red.wt / ".tdd" / "issue-12-red-half").exists()


def test_4026_called_again_after_a_develop_red_wait_it_only_waits_again_then_goes_on(red):
    _pid(red, "111\nTue Nov 17 07:00:00 2026\n")
    first = red(answers={("wait-leaf.sh", "develop-red"): (3, ""), ("refresh-spec.sh", None): (2, "")})[0]
    code, out, err, fake = red()

    assert (first, code) == (3, 0)
    assert fake.calls[0][:2] == ("wait-leaf.sh", ("develop-red",))
    assert fake.launched() == ["verdict-red"]
    assert "refresh-spec.sh" not in fake.names()
    assert "capture" in (red.wt / ".tdd" / "red-half-note.md").read_text()


def test_4026_called_again_after_a_verdict_red_wait_it_only_waits_again_then_records_and_comments(red):
    _pid(red, "111\nTue Nov 17 07:00:00 2026\n")
    first = red(answers={("wait-leaf.sh", "verdict-red"): (3, "")})[0]
    code, out, err, fake = red()

    assert (first, code) == (3, 0)
    assert [c[0] for c in fake.calls[:3]] == ["wait-leaf.sh", "step-cost.sh", "step-budget.sh"]
    assert fake.calls[0][1] == ("verdict-red",)
    assert fake.launched() == []
    assert [c[1][1] for c in fake.calls if c[0] == "comment.sh"] == ["red", "verify-red"]
    assert not (red.wt / ".tdd" / "issue-12-red-half-wait").exists()
    assert (red.wt / ".tdd" / "issue-12-red-half").read_text().startswith("step=" + STEP + "\ntest_path=tests/")


def test_4026_the_wait_record_names_the_conductor_by_the_pid_and_start_time_its_pid_file_held(red):
    _pid(red, "111\nTue Nov 17 07:00:00 2026\n")
    red(answers={("wait-leaf.sh", "develop-red"): (3, "")})

    record = json.loads((red.wt / ".tdd" / "issue-12-red-half-wait").read_text())
    assert (record["conductor"], record["at"]) == ({"pid": "111", "started": "Tue Nov 17 07:00:00 2026"},
                                                   "develop-red")


@pytest.mark.parametrize("second", ["222\nTue Nov 17 07:00:00 2026\n", "111\nTue Nov 17 08:00:00 2026\n", None],
                         ids=["another pid", "another start time", "no pid file"])
def test_4026_called_under_another_conductor_it_discards_the_record_and_starts_from_its_first_call(red, second):
    _pid(red, "111\nTue Nov 17 07:00:00 2026\n")
    red(answers={("wait-leaf.sh", "verdict-red"): (3, "")})
    if second is None:
        (red.wt / ".tdd" / "conductor.pid").unlink()
    else:
        _pid(red, second)
    code, out, err, fake = red()

    assert (code, fake.calls[0][:2]) == (0, ("refresh-spec.sh", ("12", ".tdd/issue-12-spec.md")))


READ = ("extract-result.sh", "step-cost.sh", "step-budget.sh")  # their stdout is read as a figure or a report


def test_4026_every_inner_call_prints_its_name_and_exit_then_its_stdout_and_its_stderr(red):
    class Marked(Fake):
        def __call__(self, name, *args, **kw):
            code, out, err = super().__call__(name, *args, **kw)
            if os.path.basename(name) in READ:
                return code, out, err
            return code, "OUT<%d>\n" % len(self.calls) + out, "ERR<%d>\n" % len(self.calls)

    code, out, err, fake = red(fake=Marked())

    lines = out.splitlines()
    for i, c in enumerate(fake.calls, 1):
        if c[0] in READ:
            continue
        assert "OUT<%d>" % i in lines and "ERR<%d>" % i in err
        named = lines[lines.index("OUT<%d>" % i) - 1]
        assert named.startswith(c[0]) and named.endswith(" exit %d" % (3 if c[0] in (
            "stop-requested.sh", "red-divergence.sh") else 0))


# Inner calls the Red section does not name, each by name with its reason.
NAMED_ELSEWHERE = {
    "stop-requested.sh": "FC8: the stop check *Launching a leaf* states before every leaf, which Red defers to",
    "step-budget.sh": "RH4: the budget *The step's cost check* weighs step-cost.sh's figure against",
    "extract-result.sh": "FC2: *Launching a leaf* reads a leaf's report only through it",
}


def test_4026_every_inner_call_in_the_ordered_list_is_a_script_the_red_section_names():
    from pathlib import Path
    red_half = importlib.import_module("veri.red_half")
    skill = (Path(red_half.__file__).resolve().parents[2] / "SKILL.md").read_text()
    section = skill[skill.index("#### Red — one failing test"):skill.index("#### Green — minimum implementation")]

    assert [name for name in red_half.CALLS if "$S/" + name not in section and name not in NAMED_ELSEWHERE] == []


def test_4026_a_clean_run_makes_the_calls_of_the_ordered_list_in_its_order(red):
    red_half = importlib.import_module("veri.red_half")
    code, out, err, fake = red(step=REPLACES)

    made = [c[0] for c in fake.calls if c[0] != "git"]
    made += [os.path.basename(a) for c in fake.calls if c[0] == "detach-leaf.sh" for a in c[1] if a.endswith(".sh")]
    assert code == 0
    assert set(made) | {"event.sh"} == set(red_half.CALLS)
    firsts = [made.index(name) for name in red_half.CALLS if name in made and name not in (
        "supervise.sh", "run-leaf.sh", "run-verdict.sh")]
    assert firsts == sorted(firsts)


@pytest.mark.parametrize("at", ["verdict-red", "skipped"])
def test_re_entered_after_a_revised_pass_it_finishes_once_without_a_second_verify_comment_or_record_4433(red, at):
    """PRD 038.9 RVS5: revise.sh re-saved the wait (`revised`) after posting verify-revised and recording the frozen
    tests and red-setup on the revised report, so red-half's finish posts no verify-red and records neither again."""
    values = {"refresh": 0, "test_path": "tests/test_a.py", "target_test": "tests/test_a.py::test_one",
              "revised": True}
    if at == "skipped":
        values["posted"] = True
    (red.wt / ".tdd" / "issue-12-red-half-wait").write_text(json.dumps({"conductor": None, "at": at,
                                                                         "values": values}))
    code, out, err, fake = red()

    assert (code, fake.launched()) == (0, [])
    assert [c[1][1] for c in fake.calls if c[0] == "comment.sh"] == ["red"]
    assert not {"tests-frozen.sh", "red-setup.sh"} & set(fake.names())
    assert (red.wt / ".tdd" / "issue-12-red-half").read_text().splitlines()[0] == "step=" + STEP


def test_re_entered_with_no_refresh_value_it_still_finishes_4433(red):
    """Review of #4437: a revise whose rejected record was dropped (another conductor's, FC7) re-saves red-half's wait
    without the `refresh` its own develop wrote, and finish still posts the Red comment, with no refresh note."""
    (red.wt / ".tdd" / "issue-12-red-half-wait").write_text(json.dumps({
        "conductor": None, "at": "verdict-red",
        "values": {"test_path": "tests/test_a.py", "target_test": "tests/test_a.py::test_one", "revised": True}}))
    code, out, err, fake = red()

    assert (code, [c[1][1] for c in fake.calls if c[0] == "comment.sh"]) == (0, ["red"]), out
    assert (red.wt / ".tdd" / "red-half-note.md").read_text() == "Prediction matched: verify-red judged the test.\n"


def test_4443_a_go_red_step_is_exit_2_before_any_inner_call(red):
    code, out, err, fake = red(step="Go-red guard: probe `a.py` `x` → `y` on `t.py::c` ⟦go-red⟧ ⟦criterion 1⟧")

    assert (code, fake.calls) == (2, [])
    assert "a step its prose runs" in err


@pytest.mark.parametrize("kind, mark", [("⟦diff-checked⟧", "⟦diff-checked⟧"), ("⟦go-red⟧", "⟦go-red⟧"),
                                        ("⟦phases:", "⟦phases: expand, migrate⟧"), ("⟦skill-edit⟧", "⟦skill-edit⟧"),
                                        ("⟦fixture-repair⟧", "⟦fixture-repair⟧")])
def test_4709_a_kind_mark_quoted_in_the_prose_is_no_kind_and_one_in_the_trailing_run_is(kind, mark):
    refused = importlib.import_module("veri.red_half").refused

    assert refused("appends a step carrying no `%s` mark ⟦criterion 1⟧" % mark) == []
    assert refused("does the thing %s ⟦criterion 1⟧" % mark) == [kind]


MIXED_LEDGER = ("# Plan for #12\n\n"
                "- [x] re-pin the moved case ⟦diff-checked⟧ ⟦criterion 1⟧\n"
                "- [ ] appends a repair step carrying `⟦branch-repair⟧` and no `⟦diff-checked⟧` ⟦criterion 1⟧\n"
                "- [ ] a plain step ⟦criterion 2⟧\n"
                "- [ ] edit the fixture ⟦diff-checked⟧ ⟦criterion 2⟧\n"
                "- [ ] names `⟦skill-edit⟧`, `⟦fixture-repair⟧` and `⟦phases: expand, migrate⟧` in passing ⟦criterion 3⟧\n"
                "- [ ] ⟦diff-checked⟧ edit the case of the pin on skills/x/test_a.py so its recorded mutation turns it red ⟦added⟧ ⟦criterion 3⟧\n"
                "- [ ] another plain step ⟦criterion 3⟧\n")


def test_4709_refused_and_ledger_steps_agree_on_every_steps_kind_in_a_ledger_mixing_quoted_and_trailing_marks():
    red_half, ledger = importlib.import_module("veri.red_half"), importlib.import_module("veri.ledger")

    for step in ledger.ledger_steps(MIXED_LEDGER):
        kinds = red_half.refused(step.text)
        assert ("⟦diff-checked⟧" in kinds) == (step.kind == "diff-checked"), step.text
        assert [kind for kind in kinds if kind not in ledger.trailing_markers(step.text)] == [], step.text


@pytest.mark.parametrize("step", ["⟦fixture-repair⟧ rebuild the fixture ⟦criterion 1⟧",
                                  "⟦phases: expand, migrate⟧ move the interface ⟦criterion 1⟧",
                                  "⟦go-red⟧ guard ⟦criterion 1⟧", "⟦diff-checked⟧ re-edit a case ⟦criterion 1⟧"])
def test_4709_a_step_that_only_starts_with_a_refused_mark_gets_no_kind(step):
    refused = importlib.import_module("veri.red_half").refused

    assert refused(step) == []


def test_4709_the_leading_skill_edit_form_still_gives_its_kind():
    red_half = importlib.import_module("veri.red_half")

    assert red_half.refused("⟦skill-edit⟧ edit `skills/tdd/SKILL.md` ⟦criterion 1⟧") == ["⟦skill-edit⟧"]
