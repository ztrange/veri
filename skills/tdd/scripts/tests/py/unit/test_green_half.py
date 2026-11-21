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


BRANCH_BASE = "abc1234"  # the run's recorded branch base (#4375)


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
        files = {"branch_base": (wt / ".tdd" / "issue-12-branch-base", BRANCH_BASE + "\n"), 
                 "preflight": (wt / ".tdd" / "issue-12-preflight", "worktree=%s\nfast_cmd=make unit\n" % wt),
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
                                            ("spec", ".tdd/issue-12-spec.md")])
def test_4027_a_missing_input_is_exit_2_before_any_inner_call_named_on_stderr(green, missing, named):
    code, out, err, fake = green(missing=(missing,))

    assert (code, fake.calls) == (2, [])
    assert named in err


@pytest.mark.parametrize("given", [{"missing": ("red-half",)}, {"red_step": "zero ⟦criterion 1⟧"}])
def test_a_missing_red_half_record_or_one_naming_another_step_is_exit_1_on_the_seam_line_before_any_call_4342(
        green, given):
    """SC4, replacing #4027's exit 2: a stale or missing record is a designed hand-off, never an exit 2 (S1)."""
    code, out, err, fake = green(**given)

    assert (code, fake.calls) == (1, [])
    assert out.splitlines()[-1] == ("seam=green-half code=1 reason=record next=seam-settle.sh 12 red-half test_path=… "
                                    "target_test=…")


@pytest.mark.parametrize("step", ["port: replaces 'a' in tests/py/test_x.py ⟦replaces-case⟧ ⟦criterion 1⟧",
                                  "fix the CI job ⟦ci-repair⟧ ⟦criterion 1⟧"])
def test_4027_a_replaces_case_or_ci_repair_step_is_exit_2_before_any_inner_call(green, step):
    code, out, err, fake = green(step=step)

    assert (code, fake.calls) == (2, [])


def _after(fake, name, first=None):
    at = fake.calls.index(fake.call(name, first))
    return fake.calls[at + 1:]


def _short(args):
    return tuple(os.path.basename(a) if a.endswith(".sh") else a for a in args)


def test_4027_it_builds_the_green_prompt_from_the_red_values_and_launches_develop_green(green):
    code, out, err, fake = green(answers={("wait-leaf.sh", "verdict-green"): (3, "")})

    assert [c[0] for c in fake.calls[:4]] == ["build-develop-prompt.sh", "stop-requested.sh", "detach-leaf.sh",
                                              "wait-leaf.sh"]
    assert fake.calls[0][1] == ("green", ".tdd/issue-12-spec.md", STEP, "make unit", "tests/test_a.py",
                                "tests/test_a.py::test_one", "make unit")
    assert fake.calls[0][4]["out"] == ".tdd/develop-green.prompt"
    launch = fake.calls[2]
    assert _short(launch[1]) == ("supervise.sh", "develop-green", "run-leaf.sh", ".tdd/develop-green.prompt",
                                 "--permission-mode", "bypassPermissions")
    assert (launch[3]["VERI_TEST_CMD"], launch[3]["VERI_ISSUE"], launch[3]["VERI_STEP"]) == ("make unit", "12", STEP)
    assert (launch[4]["out"], launch[4]["err"]) == (".tdd/develop-green.out", ".tdd/develop-green.err")
    assert [c[0] for c in fake.calls[4:8]] == ["step-cost.sh", "step-budget.sh", "extract-result.sh",
                                               "suite-reported.sh"]


@pytest.mark.parametrize("leaf", [1, 2])
def test_4027_a_develop_green_wait_exit_1_or_2_stops_it(green, leaf):
    code, out, err, fake = green(answers={("wait-leaf.sh", "develop-green"): (leaf, "")})

    assert (code, out.splitlines()[-1]) == (leaf, "stopped at 1 wait-leaf.sh develop-green exit %d" % leaf)


def test_4027_a_cost_over_the_step_budget_stops_it_at_the_cost_check(green):
    code, out, err, fake = green(fake=Fake(cost="13\n"))

    assert (code, out.splitlines()[-1]) == (1, "stopped at cost-check spent 13 over the step budget 12")


def test_4027_suite_reported_exit_2_stops_it_with_no_verifier(green):
    code, out, err, fake = green(answers={("suite-reported.sh", None): (2, "")})

    assert (code, fake.names()[-1], fake.launched()) == (2, "suite-reported.sh", ["develop-green"])
    assert fake.call("suite-reported.sh")[1:] [0] == ("develop-green",)
    assert fake.call("suite-reported.sh")[4]["err"] == ".tdd/suite-reported.err"


@pytest.mark.parametrize("line", ["WRONG_TEST: the test asserts x", "SUPERSEDED: tests/test_b.py::test_b",
                                  "SPLIT: smaller one", "TIDY_FIRST: extract f"])
def test_4027_a_route_line_in_the_report_stops_it_with_exit_1_naming_it_before_any_route_or_suite_check(green, line):
    code, out, err, fake = green(fake=Fake(report=REPORT + line + "\n"))

    assert (code, out.splitlines()[-1]) == (1, "stopped at 1 " + line)
    assert fake.names()[-1] == "extract-result.sh"
    assert "wrong-test-route.sh" not in fake.names()


@pytest.mark.parametrize("verb", ["check", "check-earlier"])
@pytest.mark.parametrize("frozen", [1, 2])
def test_4027_a_frozen_test_check_exit_1_or_2_stops_it_with_no_verifier(green, verb, frozen):
    code, out, err, fake = green(answers={("tests-frozen.sh", verb): (frozen, "")})

    assert (code, fake.names()[-1], fake.launched()) == (frozen, "tests-frozen.sh", ["develop-green"])


def test_4027_it_checks_the_frozen_tests_then_the_earlier_steps_then_launches_verdict_green(green):
    code, out, err, fake = green()

    tail = _after(fake, "suite-reported.sh")
    assert [(c[0], c[1]) for c in tail[:2]] == [("tests-frozen.sh", ("check", "--step", STEP)),
                                                ("tests-frozen.sh", ("check-earlier", ".tdd/issue-12.md", "--step",
                                                                     STEP))]
    assert [c[0] for c in tail[2:7]] == ["stop-requested.sh", "detach-leaf.sh", "wait-leaf.sh", "step-cost.sh",
                                         "step-budget.sh"]
    launch = tail[3]
    assert _short(launch[1]) == ("supervise.sh", "verdict-green", "run-verdict.sh", "--step", STEP, "--fast-cmd",
                                 "make unit", "--branch-base", BRANCH_BASE, "green", ".tdd/issue-12-spec.md",
                                 "tests/test_a.py",
                                 "tests/test_a.py::test_one")
    assert (launch[4]["out"], launch[4]["err"]) == (".tdd/verify-green.reason", ".tdd/verify-green.err")


@pytest.mark.parametrize("verdict", [1, 2])
def test_4027_a_verdict_of_1_or_2_stops_it_before_any_comment_or_tick(green, verdict):
    code, out, err, fake = green(answers={("wait-leaf.sh", "verdict-green"): (verdict, "")})

    assert (code, out.splitlines()[-1]) == (verdict, "stopped at 2 wait-leaf.sh verdict-green exit %d" % verdict)
    assert not {"comment.sh", "tick-ledger.sh"} & set(fake.names())


def test_4027_with_green_switched_off_it_marks_the_skip_and_takes_the_pass_branch(green):
    (green.wt / ".tdd" / "issue-12-skip-verify").write_text("green\n")
    code, out, err, fake = green()

    assert (code, fake.launched()) == (0, ["develop-green"])
    assert fake.call("event.sh")[1] == ("verify-green-skipped", "reason=switched-off")
    assert (green.wt / ".tdd" / "verdict-green.exit").read_text().strip() == "skipped"
    assert [c[0] for c in _after(fake, "event.sh")][:2] == ["comment.sh", "comment.sh"]


def test_4027_on_a_pass_it_comments_checks_graded_units_and_frozen_tests_ticks_commits_pushes_and_asks_for_a_stop(
        green):
    code, out, err, fake = green()

    tail = [(c[0], c[1]) for c in _after(fake, "wait-leaf.sh", "verdict-green") if c[0] not in (
        "step-cost.sh", "step-budget.sh")]
    assert tail == [
        ("comment.sh", ("12", "green")), ("comment.sh", ("12", "verify-green")),
        ("git", ("log", "-1", "--format=%H", "--", ".tdd/issue-12.md")), ("graded-changed.sh", (BASE_SHA,)),
        ("tests-frozen.sh", ("check", "--step", STEP)),
        ("tick-ledger.sh", ("--refactor-pending", ".tdd/issue-12.md", STEP)), ("git", ("add", "-A")),
        ("git", ("commit", "-m", "feat: one thing works (#12)")), ("git", ("rev-parse", "HEAD")),
        ("push-branch.sh", ()), ("git", ("branch", "--show-current")),
        ("gh", ("api", "repos/{owner}/{repo}/pulls?head={owner}:tdd/12-a-thing", "-q", ".[0].html_url // empty")),
        ("pr-body.sh", ("77", ".tdd/green-half-pr-body.md")), ("stop-requested.sh", ())]
    assert (green.wt / ".tdd" / "green-half-pr-body.md").read_text() == (
        "Closes #12 — work in progress: 2 of 3 steps done. The ledger .tdd/issue-12.md is the source of truth.\n")
    expected = ["step=" + STEP, "green_sha=" + GREEN_SHA, "test_path=tests/test_a.py"]
    assert code == 0
    assert (green.wt / ".tdd" / "issue-12-green-half").read_text().splitlines() == expected
    assert out.splitlines()[-len(expected):] == expected
    assert "- [x] %s ⟂ refactor pending" % STEP in (green.wt / ".tdd" / "issue-12.md").read_text()


def test_4027_a_bug_runs_subject_is_fix(green):
    code, out, err, fake = green(spec="# spec\n\n## Bug\n\nit breaks\n")

    assert fake.call("git", "commit")[1] == ("commit", "-m", "fix: one thing works (#12)")


@pytest.mark.parametrize("graded", [1, 2])
def test_4027_a_graded_change_stops_it_with_nothing_ticked(green, graded):
    code, out, err, fake = green(answers={("graded-changed.sh", None): (graded, "")})

    assert (code, fake.names()[-1], "tick-ledger.sh" in fake.names()) == (graded, "graded-changed.sh", False)
    assert out.splitlines()[-1].startswith("stopped at 3 graded-changed.sh")


class _Changed(Fake):
    """tests-frozen.sh check answers 0 the first time and <code> the second."""
    second = 1

    def __call__(self, name, *args, **kw):
        if os.path.basename(name) == "tests-frozen.sh" and args[:1] == ("check",):
            seen = [c for c in self.calls if c[0] == "tests-frozen.sh" and c[1][:1] == ("check",)]
            if seen:
                self.calls.append(("tests-frozen.sh", args, kw.get("cwd"), kw.get("env"), kw))
                return self.second, "tests/test_a.py\n", ""
        return super().__call__(name, *args, **kw)


@pytest.mark.parametrize("second", [1, 2, 3])
def test_4027_a_frozen_test_changed_before_the_tick_stops_it_with_nothing_ticked(green, second):
    fake = _Changed()
    fake.second = second
    code, out, err, fake = green(fake=fake)

    assert (code, fake.names()[-1], "tick-ledger.sh" in fake.names()) == (
        1 if second == 3 else second, "tests-frozen.sh", False)


@pytest.mark.parametrize("pushed", [1, 2])
def test_4027_a_push_exit_1_or_2_stops_it_after_the_commit(green, pushed):
    code, out, err, fake = green(answers={("push-branch.sh", None): (pushed, "")})

    assert (code, fake.names()[-1]) == (pushed, "push-branch.sh")
    assert out.splitlines()[-1] == "stopped at 3 push-branch.sh exit %d" % pushed


def test_4027_no_pr_for_the_branch_stops_it_with_exit_2_before_the_pr_body(green):
    code, out, err, fake = green(answers={("gh", None): (0, "")})

    assert (code, fake.names()[-1], out.splitlines()[-1]) == (2, "gh", "stopped at 3 no PR for tdd/12-a-thing")


@pytest.mark.parametrize("code, mode, exit", [(0, "at-ledger\n", 1), (0, "now\n", 1), (2, "", 2)])
def test_4027_a_stop_asked_after_the_push_stops_it_unsettled(green, code, mode, exit):
    class Asked(Fake):
        def __call__(self, name, *args, **kw):
            if os.path.basename(name) == "stop-requested.sh" and "push-branch.sh" in self.names():
                self.calls.append(("stop-requested.sh", args, kw.get("cwd"), kw.get("env"), kw))
                return code, mode, ""
            return super().__call__(name, *args, **kw)

    got, out, err, fake = green(fake=Asked())

    assert (got, fake.names()[-1]) == (exit, "stop-requested.sh")
    assert out.splitlines()[-1].startswith("stopped at 3 stop-requested.sh exit %d" % code)
    assert not (green.wt / ".tdd" / "issue-12-green-half").exists()


def test_4027_it_launches_no_leaf_but_through_supervise(green):
    code, out, err, fake = green()

    assert not {"run-leaf.sh", "run-verdict.sh", "claude", "supervise.sh"} & set(fake.names())
    assert fake.launched() == ["develop-green", "verdict-green"]


def test_4027_it_writes_no_bail_and_resets_nothing_on_a_stop(green):
    code, out, err, fake = green(answers={("wait-leaf.sh", "verdict-green"): (1, "")})

    assert not {"classify-bail.sh", "preflight-refused.sh", "event.sh", "wrong-test-route.sh"} & set(fake.names())
    assert not [c for c in fake.calls if c[0] == "git"]


def _pid(green, text):
    (green.wt / ".tdd" / "conductor.pid").write_text(text)


@pytest.mark.parametrize("leaf", ["develop-green", "verdict-green"])
def test_4027_a_wait_whose_slice_ran_out_exits_3_on_a_waiting_on_line(green, leaf):
    code, out, err, fake = green(answers={("wait-leaf.sh", leaf): (3, "")})

    assert (code, out.splitlines()[-1]) == (3, "waiting on " + leaf)
    assert "tick-ledger.sh" not in fake.names()


@pytest.mark.parametrize("leaf, launched", [("develop-green", ["verdict-green"]), ("verdict-green", [])])
def test_4027_called_again_after_an_exit_3_it_only_waits_again_then_goes_on_once(green, leaf, launched):
    _pid(green, "111\nTue Nov 17 07:00:00 2026\n")
    first = green(answers={("wait-leaf.sh", leaf): (3, "")})[0]
    code, out, err, fake = green()

    assert (first, code) == (3, 0)
    assert fake.calls[0][:2] == ("wait-leaf.sh", (leaf,))
    assert (fake.launched(), "build-develop-prompt.sh" in fake.names()) == (launched, False)
    assert [c[1][1] for c in fake.calls if c[0] == "comment.sh"] == ["green", "verify-green"]
    assert [c[1][0] for c in fake.calls if c[0] == "git" and c[1][0] == "commit"] == ["commit"]
    assert fake.names().count("push-branch.sh") == 1
    assert not (green.wt / ".tdd" / "issue-12-green-half-wait").exists()


def test_4027_the_wait_record_names_the_conductor_by_the_pid_and_start_time_its_pid_file_held(green):
    _pid(green, "111\nTue Nov 17 07:00:00 2026\n")
    green(answers={("wait-leaf.sh", "verdict-green"): (3, "")})

    record = json.loads((green.wt / ".tdd" / "issue-12-green-half-wait").read_text())
    assert (record["conductor"], record["at"]) == ({"pid": "111", "started": "Tue Nov 17 07:00:00 2026"},
                                                   "verdict-green")


@pytest.mark.parametrize("second", ["222\nTue Nov 17 07:00:00 2026\n", "111\nTue Nov 17 08:00:00 2026\n", None],
                         ids=["another pid", "another start time", "no pid file"])
def test_4027_called_under_another_conductor_it_discards_the_record_and_starts_from_its_first_call(green, second):
    _pid(green, "111\nTue Nov 17 07:00:00 2026\n")
    green(answers={("wait-leaf.sh", "verdict-green"): (3, "")})
    if second is None:
        (green.wt / ".tdd" / "conductor.pid").unlink()
    else:
        _pid(green, second)
    code, out, err, fake = green()

    assert (code, fake.calls[0][0]) == (0, "build-develop-prompt.sh")


READ = ("extract-result.sh", "step-cost.sh", "step-budget.sh", "gh", "git")  # stdout read as a figure, report or sha


def test_4027_every_inner_call_prints_its_name_and_exit_then_its_stdout_and_its_stderr(green):
    class Marked(Fake):
        def __call__(self, name, *args, **kw):
            code, out, err = super().__call__(name, *args, **kw)
            if os.path.basename(name) in READ:
                return code, out, err
            return code, "OUT<%d>\n" % len(self.calls) + out, "ERR<%d>\n" % len(self.calls)

    code, out, err, fake = green(fake=Marked())

    lines = out.splitlines()
    assert code == 0
    for i, c in enumerate(fake.calls, 1):
        if c[0] in READ:
            continue
        assert "OUT<%d>" % i in lines and "ERR<%d>" % i in err
        named = lines[lines.index("OUT<%d>" % i) - 1]
        assert named.startswith(c[0]) and named.endswith(" exit %d" % (3 if c[0] == "stop-requested.sh" else 0))


# Inner calls the Green section does not name, each by name with its reason.
NAMED_ELSEWHERE = {
    "step-budget.sh": "RH4: the budget *The step's cost check* weighs step-cost.sh's figure against",
    "extract-result.sh": "FC2: *Launching a leaf* reads a leaf's report only through it",
}


def test_4027_every_inner_call_in_the_ordered_list_is_a_script_the_green_section_names():
    from pathlib import Path
    green_half = importlib.import_module("veri.green_half")
    skill = (Path(green_half.__file__).resolve().parents[2] / "SKILL.md").read_text()
    start = skill.index("#### Green — minimum implementation")
    section = skill[start:skill.index("\n#### ", start)]

    assert [name for name in green_half.CALLS if "$S/" + name not in section and name not in NAMED_ELSEWHERE] == []


def test_4027_a_clean_run_makes_the_calls_of_the_ordered_list_in_its_order(green):
    green_half = importlib.import_module("veri.green_half")
    code, out, err, fake = green()

    made = [c[0] for c in fake.calls if c[0] not in ("git", "gh")]
    made += [os.path.basename(a) for c in fake.calls if c[0] == "detach-leaf.sh" for a in c[1] if a.endswith(".sh")]
    assert code == 0
    assert set(made) | {"event.sh"} == set(green_half.CALLS)
    firsts = [made.index(name) for name in green_half.CALLS if name in made and name not in (
        "supervise.sh", "run-leaf.sh", "run-verdict.sh")]
    assert firsts == sorted(firsts)


def test_after_seam_settle_red_half_green_half_launches_develop_green_with_the_settled_values_4342(green, run_cli):
    """SC7: a Red done by hand hands back through seam-settle.sh, and green-half runs as after a clean red-half.sh."""
    wt = green.wt
    (wt / ".tdd" / "issue-12-preflight").write_text("worktree=%s\nfast_cmd=make unit\n" % wt)
    (wt / ".tdd" / "issue-12.md").write_text(LEDGER % STEP)
    settled = run_cli(importlib.import_module("veri.seam_settle"),
                      ["12", "red-half", "test_path=checks/hand_check.py", "target_test=hand_case"],
                      cwd=str(wt.parent.parent.parent))
    code, out, err, fake = green(answers={("wait-leaf.sh", "verdict-green"): (3, "")}, missing=("red-half",))

    assert settled[0] == 0
    assert (wt / ".tdd" / "issue-12-red-half").read_text() == (
        "step=%s\ntest_path=checks/hand_check.py\ntarget_test=hand_case\nred_test_id=checks/hand_check.py::hand_case\n"
        "against_unmodified=FAILS\n" % STEP)
    assert code == 3
    assert fake.call("build-develop-prompt.sh")[1] == ("green", ".tdd/issue-12-spec.md", STEP, "make unit",
                                                       "checks/hand_check.py", "hand_case", "make unit")
    assert fake.launched() == ["develop-green", "verdict-green"]


def test_it_compares_its_records_step_with_the_open_one_through_ledger_same_step_4342(green, monkeypatch):
    """SC3: the stage reads a step through ledger.same_step and no rule of its own."""
    asked = []
    monkeypatch.setattr(importlib.import_module("veri.ledger"), "same_step",
                        lambda one, other: asked.append((one, other)) or True)
    code, out, err, fake = green(answers={("wait-leaf.sh", "develop-green"): (3, "")}, red_step="another step")

    assert (code, fake.launched()) == (3, ["develop-green"])
    assert sorted(asked[0]) == sorted(("another step", STEP))


def test_a_record_step_differing_only_by_marks_is_rewritten_with_the_ledgers_and_the_stage_uses_the_ledgers_4342(green):
    """SC1: the open step comes from the ledger; a stale step in the record is rewritten with it."""
    stale = "one thing works ⟦added⟧ ⟦criterion 3⟧"
    code, out, err, fake = green(answers={("wait-leaf.sh", "develop-green"): (3, "")}, red_step=stale)

    assert (code, fake.call("build-develop-prompt.sh")[1][2]) == (3, STEP)
    assert (green.wt / ".tdd" / "issue-12-red-half").read_text() == RED_HALF % STEP


def test_each_record_rewrite_writes_one_record_refreshed_event_naming_stage_key_old_and_new_4342(green):
    """SC2, under the VERI_EVENT_STRICT=1 the hermetic fixture sets."""
    stale = "one thing works ⟦added⟧ ⟦criterion 3⟧"
    green(answers={("wait-leaf.sh", "develop-green"): (3, "")}, red_step=stale)

    events = [json.loads(line) for line in (green.wt / ".tdd" / "events.jsonl").read_text().splitlines()]
    refreshed = [e for e in events if e["event"] == "record-refreshed"]
    assert [(e["stage"], e["key"], e["old"], e["new"], e["issue"]) for e in refreshed] == [
        ("green-half", "step", stale, STEP, "12")]


@pytest.mark.parametrize("verdict, kept", [(1, True), (2, False)])
def test_a_verdict_reject_keeps_the_stage_wait_record_as_its_rejected_record_and_any_other_code_drops_it_4433(
        green, verdict, kept):
    """PRD 038.9 criterion 5: a REJECT hands the stage's wait values to revise.sh through `<stage>-rejected`."""
    _pid(green, "111\nTue Nov 17 07:00:00 2026\n")
    code, out, err, fake = green(answers={("wait-leaf.sh", "verdict-green"): (verdict, "")})

    rejected = green.wt / ".tdd" / "issue-12-green-half-rejected-wait"
    assert (code, (green.wt / ".tdd" / "issue-12-green-half-wait").exists(), rejected.exists()) == (verdict, False, kept)
    if kept:
        record = json.loads(rejected.read_text())
        assert (record["conductor"], record["at"], record["values"], record["step"]) == (
            {"pid": "111", "started": "Tue Nov 17 07:00:00 2026"}, "verdict-green",
            {"test_path": "tests/test_a.py", "target_test": "tests/test_a.py::test_one"}, STEP)


@pytest.mark.parametrize("at", ["verdict-green", "skipped"])
def test_re_entered_after_a_revised_pass_it_finishes_once_without_a_second_verify_comment_4433(green, at):
    """PRD 038.9 RVS5: revise.sh posted verify-revised before re-saving the wait (`revised`)."""
    values = {"test_path": "tests/test_a.py", "target_test": "tests/test_a.py::test_one", "revised": True}
    if at == "skipped":
        values["posted"] = True
    (green.wt / ".tdd" / "issue-12-green-half-wait").write_text(json.dumps({"conductor": None, "at": at,
                                                                             "values": values}))
    code, out, err, fake = green()

    assert (code, fake.launched()) == (0, [])
    assert [c[1][1] for c in fake.calls if c[0] == "comment.sh"] == ["green"]
    assert [c[1][0] for c in fake.calls if c[0] == "git" and c[1][0] == "commit"] == ["commit"]


def test_4499_after_a_reroute_rewrote_an_earlier_steps_case_check_earlier_excepts_it_and_verify_green_launches(green):
    rewritten = "tests/test_b.py::test_earlier"
    event = {"event": "reroute", "actor": "conductor", "step": STEP, "kind": "red", "case": rewritten}
    (green.wt / ".tdd" / "events.jsonl").write_text(json.dumps(event) + "\n")

    code, out, err, fake = green()

    tail = _after(fake, "suite-reported.sh")
    assert tail[1][:2] == ("tests-frozen.sh", ("check-earlier", ".tdd/issue-12.md", "--step", STEP, "--except",
                                               rewritten))
    assert "verdict-green" in fake.launched()


def test_4499_check_earlier_excepts_each_case_this_steps_reroutes_named_once_past_an_unreadable_line_and_not_another_steps(green):
    mine, other = "tests/test_b.py::test_mine", "tests/test_c.py::test_other"
    lines = [{"event": "reroute", "actor": "conductor", "step": STEP, "kind": "red", "case": mine},
             {"event": "reroute", "actor": "conductor", "step": "another step ⟦criterion 2⟧", "kind": "red",
              "case": other},
             {"event": "reroute", "actor": "conductor", "step": STEP, "kind": "red", "case": mine}]
    journal = "\n".join([json.dumps(lines[0]), "{not json", json.dumps(lines[1]), json.dumps(lines[2])]) + "\n"
    (green.wt / ".tdd" / "events.jsonl").write_text(journal)

    code, out, err, fake = green()

    tail = _after(fake, "suite-reported.sh")
    assert tail[1][:2] == ("tests-frozen.sh", ("check-earlier", ".tdd/issue-12.md", "--step", STEP, "--except", mine))
    assert "verdict-green" in fake.launched()


def test_4499_a_reroute_naming_two_cases_excepts_each_on_its_own_once_in_order(green):
    first, second = "tests/test_b.py::test_one", "tests/test_b.py::test_two"
    lines = [{"event": "reroute", "actor": "conductor", "step": STEP, "kind": "red", "case": first + " " + second},
             {"event": "reroute", "actor": "conductor", "step": STEP, "kind": "red", "case": second}]
    (green.wt / ".tdd" / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in lines))

    code, out, err, fake = green()

    tail = _after(fake, "suite-reported.sh")
    assert tail[1][:2] == ("tests-frozen.sh", ("check-earlier", ".tdd/issue-12.md", "--step", STEP,
                                               "--except", first, "--except", second))
    assert "verdict-green" in fake.launched()


def test_4479_a_green_half_wait_record_naming_another_step_is_ignored_and_the_open_step_launches_develop_green(green):
    values = {"test_path": "tests/test_old.py", "target_test": "tests/test_old.py::test_a"}
    (green.wt / ".tdd" / "issue-12-green-half-wait").write_text(json.dumps(
        {"conductor": None, "at": "verdict-green", "values": values, "step": "step A ⟦criterion 1⟧"}))
    (green.wt / ".tdd" / "verdict-green.exit").write_text("0\n")
    code, out, err, fake = green()

    assert fake.launched() == ["develop-green", "verdict-green"]


def test_4479_a_green_half_wait_record_naming_the_open_step_still_resumes_at_its_verdict_and_launches_nothing(green):
    values = {"test_path": "tests/test_a.py", "target_test": "tests/test_a.py::test_one"}
    (green.wt / ".tdd" / "issue-12-green-half-wait").write_text(json.dumps(
        {"conductor": None, "at": "verdict-green", "values": values, "step": STEP}))
    (green.wt / ".tdd" / "verdict-green.exit").write_text("0\n")
    code, out, err, fake = green()

    assert (code, fake.launched()) == (0, [])
    assert [c[1][0] for c in fake.calls if c[0] == "git" and c[1][0] == "commit"] == ["commit"]


def test_4479_the_wait_record_a_revised_green_pass_re_saves_is_not_loaded_once_a_later_step_is_open_and_it_launches_develop_green(
        green, monkeypatch, run_cli, tmp_path):
    fused = importlib.import_module("veri.fused")
    revise = importlib.import_module("veri.revise")
    tdd = green.wt / ".tdd"
    step_a, step_b = STEP, "two things work ⟦criterion 2⟧"
    for name, text in {"issue-12-branch-base": BRANCH_BASE + "\n", "issue-12-spec.md": "# spec\n",
                       "issue-12-preflight": "worktree=%s\nfast_cmd=make unit\n" % green.wt,
                       "issue-12.md": LEDGER % step_a, "issue-12-red-half": RED_HALF % step_a,
                       "verify-green.reason": "VERDICT: REJECT\nhardcoded\n", "revise-green-1.out": "report\n",
                       "verdict-green.exit": "0\n"}.items():
        (tdd / name).write_text(text)
    (tdd / "issue-12-green-half-rejected-wait").write_text(json.dumps(
        {"conductor": None, "at": "verdict-green", "step": step_a,
         "values": {"test_path": "tests/test_a.py", "target_test": "tests/test_a.py::test_one"}}))
    monkeypatch.setattr(fused, "run_script", Fake(wt=green.wt))
    assert run_cli(revise, ["12", "green"], cwd=str(tmp_path))[0] == 0
    (tdd / "issue-12.md").write_text(LEDGER.replace("- [ ] %s\n- [ ] two ⟦criterion 2⟧", "- [x] %s\n- [ ] " + step_b)
                                     % (step_a, ))
    (tdd / "issue-12-red-half").write_text(RED_HALF % step_b)
    code, out, err, fake = green(step=step_b)

    assert fake.launched()[:1] == ["develop-green"]
