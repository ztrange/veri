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
    diff-leaf-deviation.sh, the verdict-diff verifier, then step-tick.sh; each wait sliced."""
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
    assert calls == [("wait-leaf.sh", ("verdict-diff",)), ("step-tick.sh", ("12",))]
    scripts = os.path.dirname(os.path.dirname(os.path.realpath(importlib.import_module("veri.fused").__file__)))
    assert third[3].paths[-1] == os.path.join(scripts, "step-tick.sh")
    assert third[1].splitlines()[-1] == "next=cycle"
    for _, out, _, fake in (first, second, third):
        assert not [c for c in fake.calls if c[0] == "git" and c[1][:1] in (("reset",), ("commit",), ("rebase",))]
        assert "MARKER-4435" not in out


def test_4435_with_diff_switched_off_it_launches_no_verifier_marks_the_skip_writes_skipped_and_goes_on(diff):
    """DST4: ADR-0033's skip, then the tick in the same call."""
    diff(skip="diff", answers={("wait-leaf.sh", "develop-diff"): (3, "")})
    code, out, err, fake = diff(skip="diff")

    assert code == 0, err
    assert fake.launched() == []
    mark = fake.call("event.sh")
    assert (mark[1], mark[3]["VERI_ACTOR"], mark[3]["VERI_STEP"]) == (
        ("verify-diff-skipped", "reason=switched-off"), "conductor", STEP)
    assert (diff.wt / ".tdd" / "verdict-diff.exit").read_text() == "skipped\n"
    names = fake.names()
    assert names.index("diff-leaf-deviation.sh") < names.index("event.sh") < names.index("step-tick.sh")


ONE = "make test TESTS=\"$1\"\n"
PROBE = ("mutation-probe.sh", ("tests/test_a.py", "assert x == 1", "assert x == 2", "--", "sh", "-c", ONE.strip(), "sh",
                               "tests/test_a.py"))


def _verified(diff, step=QUALITY, **kw):
    """A ⟦test-quality⟧ step's call after its verify-diff PASS; (code, stdout, stderr, fake)."""
    diff(step=step, answers={("wait-leaf.sh", "develop-diff"): (3, "")})
    diff(step=step, answers={("wait-leaf.sh", "verdict-diff"): (3, "")})
    return diff(step=step, **kw)


def test_4435_a_test_quality_step_probes_its_flip_line_after_the_pass_and_before_the_tick(diff):
    """DST3: the last FLIP: line of the leaf's report, probed with the `veri: one test file:` command."""
    code, out, err, fake = _verified(diff, report="SUITE: ok\n" + FLIP)

    assert code == 0, err
    names = fake.names()
    assert fake.call("detect-test-command.sh")[1] == ("--tier", "one test file")
    assert (fake.call("mutation-probe.sh")[0], _short(fake.call("mutation-probe.sh")[1])) == PROBE
    assert fake.call("mutation-probe.sh")[4]["out"] == ".tdd/flip-probe.out"
    assert "VERI_MUTATION_RECORD" not in (fake.call("mutation-probe.sh")[3] or {})
    assert names.index("wait-leaf.sh") < names.index("mutation-probe.sh") < names.index("step-tick.sh")


def test_4435_with_no_one_test_file_command_the_probe_runs_the_all_tier_command(diff):
    """DST3: detect-test-command.sh exit 3 for the one-file tier falls back to the all tier."""
    class NoOneFile(Fake):
        def __call__(self, name, *args, **kw):
            if os.path.basename(name) == "detect-test-command.sh" and args == ("--tier", "one test file"):
                self.calls.append(("detect-test-command.sh", args, None, None, kw))
                return 3, "", ""
            if os.path.basename(name) == "detect-test-command.sh":
                self.calls.append(("detect-test-command.sh", args, None, None, kw))
                return 0, "make test\n", ""
            return super().__call__(name, *args, **kw)

    diff(step=QUALITY, answers={("wait-leaf.sh", "develop-diff"): (3, "")})
    diff(step=QUALITY, answers={("wait-leaf.sh", "verdict-diff"): (3, "")})
    code, out, err, fake = diff(step=QUALITY, fake=NoOneFile(report=FLIP))

    assert code == 0, err
    assert _short(fake.call("mutation-probe.sh")[1])[3:] == ("--", "sh", "-c", "make test")
    tiers = [c[1] for c in fake.calls if c[0] == "detect-test-command.sh"]
    assert tiers == [("--tier", "one test file"), ("--tier", "all")]


@pytest.mark.parametrize("report, answers, reason", [
    (FLIP, {("mutation-probe.sh", None): (1, "")},
     "REJECT: flipping assert x == 1→assert x == 2 in tests/test_a.py left tests/test_a.py green\n"),
    ("SUITE: ok\n", {}, "REJECT: the report of develop-diff carries no FLIP: line\n"),
])
def test_4435_a_flip_that_stays_green_or_no_flip_line_is_a_verify_diff_reject_exit_1_before_the_tick(
        diff, report, answers, reason):
    """DST3: the reason written to .tdd/verify-diff.reason; no tick."""
    code, out, err, fake = _verified(diff, report=report, answers=answers)

    assert code == 1, err
    assert (diff.wt / ".tdd" / "verify-diff.reason").read_text() == reason
    assert "step-tick.sh" not in fake.names()


@pytest.mark.parametrize("answers", [{("mutation-probe.sh", None): (2, "")},
                                     {("detect-test-command.sh", None): (2, "")}])
def test_4435_a_probe_or_detect_test_command_exit_2_is_exit_2(diff, answers):
    """DST3: no answer, never a REJECT."""
    code, out, err, fake = _verified(diff, report=FLIP, answers=answers)

    assert code == 2
    assert "step-tick.sh" not in fake.names()
    assert not (diff.wt / ".tdd" / "issue-12-diff-step-rejected-wait").exists()


def _rejected(diff):
    path = diff.wt / ".tdd" / "issue-12-diff-step-rejected-wait"
    return json.loads(path.read_text()) if path.exists() else None


@pytest.mark.parametrize("step, answers, report", [
    (STEP, {("wait-leaf.sh", "verdict-diff"): (1, "")}, None),
    (QUALITY, {("mutation-probe.sh", None): (1, "")}, FLIP),
])
def test_4435_a_verify_or_flip_reject_leaves_the_steps_rejected_record_for_revise_and_exits_1(
        diff, step, answers, report):
    """DST7: each REJECT hands the step to revise.sh <n> diff through the rejected record, which names the step and
    carries the original step base, so the re-verify judges the diff the rejection was about."""
    diff(step=step, answers={("wait-leaf.sh", "develop-diff"): (3, "")})
    diff(step=step, answers={("wait-leaf.sh", "verdict-diff"): (3, "")})
    code, out, err, fake = diff(step=step, answers=answers, **({"report": report} if report else {}))

    assert code == 1, err
    record = _rejected(diff)
    assert (record["step"], record["at"], record["values"]["step_base"]) == (step, "verdict-diff", STEP_BASE)
    assert "step-tick.sh" not in fake.names()


def test_4435_a_cycle_step_with_no_diff_checked_mark_is_exit_2_before_any_call(diff):
    """A cycle step must never get a develop-diff leaf."""
    code, out, err, fake = diff(step="one thing works ⟦criterion 1⟧")

    assert (code, fake.calls) == (2, [])
    assert "no open ⟦diff-checked⟧ step" in err


@pytest.mark.parametrize("answers, last", [
    ({("wait-leaf.sh", "develop-diff"): (2, "")}, "stopped at develop wait-leaf.sh develop-diff exit 2"),
    ({("diff-leaf-deviation.sh", None): (2, "")}, None),
])
def test_4435_a_killed_develop_diff_leaf_or_a_deviation_check_exit_2_is_exit_2_with_no_verifier(diff, answers, last):
    """DIFF-CHECKED.md: a supervisor exit 2 on the leaf is killed-stuck, and diff-leaf-deviation.sh exit 2 bails;
    neither reaches the verifier."""
    diff(answers={("wait-leaf.sh", "develop-diff"): (3, "")})
    code, out, err, fake = diff(answers=answers)

    assert (code, fake.launched()) == (2, [])
    assert "step-tick.sh" not in fake.names()
    if last:
        assert out.splitlines()[-1] == last
        assert "suite-reported.sh" not in fake.names()


@pytest.mark.parametrize("line", ["FLIP: tests/test_a.py assert x == 1→assert x == 2\n",
                                  "FLIP: tests/test_a.py 'assert x == 1→assert x == 2\n",
                                  "FLIP: tests/test_a.py 'assert x == 1'\n"])
def test_4435_a_malformed_flip_line_is_a_reject_and_nothing_is_probed(diff, line):
    code, out, err, fake = _verified(diff, report=line)

    assert code == 1, err
    assert not {"mutation-probe.sh", "step-tick.sh"} & set(fake.names())
    assert (diff.wt / ".tdd" / "verify-diff.reason").read_text().startswith("REJECT: the report of develop-diff")


def test_4435_a_develop_diff_leaf_with_no_suite_line_stops_exit_2_with_no_verifier(diff):
    """DST1, CY92: suite-reported.sh exit 2 launches no verifier; the adjudication is the conductor's."""
    diff(answers={("wait-leaf.sh", "develop-diff"): (3, "")})
    code, out, err, fake = diff(answers={("suite-reported.sh", None): (2, "")})

    assert (code, out.splitlines()[-1]) == (2, "stopped at develop suite-reported.sh develop-diff 2> "
                                                ".tdd/suite-reported.err exit 2")
    assert (fake.launched(), "diff-leaf-deviation.sh" in fake.names()) == ([], False)


def test_4709_a_step_only_quoting_test_quality_in_its_prose_runs_no_flip(diff):
    step = "document the `⟦test-quality⟧` mark in `a.md` ⟦diff-checked⟧ ⟦criterion 1⟧"
    code, out, err, fake = _verified(diff, step=step, report="SUITE: ok\n")

    assert code == 0, err
    assert "mutation-probe.sh" not in fake.names()


def test_4709_a_step_only_quoting_diff_checked_in_its_prose_is_exit_2_before_any_call(diff):
    code, out, err, fake = diff(step="document the `⟦diff-checked⟧` mark in `a.md` ⟦criterion 1⟧")

    assert (code, fake.calls) == (2, [])
    assert "no open ⟦diff-checked⟧ step" in err


POSSIBLE_BUG = "POSSIBLE-BUG: tests/test_a.py::test_split expects [300, 300, 300], code yields [300, 300, 299]\n"


def test_4760_a_test_quality_step_whose_leaf_reports_a_possible_bug_launches_no_verdict_diff(diff):
    """SG2, SG3: the strengthened case red, reverted and uncommitted, is a possible bug, not a step a verify-diff REJECT
    can stop."""
    diff(step=QUALITY, answers={("wait-leaf.sh", "develop-diff"): (3, "")})
    code, out, err, fake = diff(step=QUALITY, report="SUITE: ok\n" + POSSIBLE_BUG + FLIP)

    assert fake.launched() == []
    assert "run-verdict.sh" not in [os.path.basename(a) for c in fake.calls for a in c[1]]
    assert code == 0, err


def test_4760_a_test_quality_step_whose_leaf_reports_a_possible_bug_over_a_commit_stops_exit_2_and_ticks_nothing(diff):
    """SG2: a POSSIBLE-BUG: line is a claim that the leaf committed nothing; with commits since the step base the claim
    is false, so the step is neither ticked unjudged nor routed: no answer, exit 2."""
    diff(step=QUALITY, answers={("wait-leaf.sh", "develop-diff"): (3, "")})
    code, out, err, fake = diff(step=QUALITY, answers={("git", "diff"): (0, "tests/test_a.py\n")},
                                report="SUITE: ok\n" + POSSIBLE_BUG)

    assert code == 2, err
    diffs = [c[1] for c in fake.calls if c[0] == "git" and c[1][:1] == ("diff",)]
    assert diffs == [("diff", "--name-only", STEP_BASE + "..HEAD")]
    assert ("step-tick.sh" in fake.names(), "add-ledger-step.sh" in fake.names(), fake.launched()) == (
        False, False, [])
    assert "⟦quality-repair⟧" not in (diff.wt / ".tdd" / "issue-12.md").read_text()


def test_4760_an_ordinary_diff_checked_step_whose_leaf_reports_a_possible_bug_still_launches_verdict_diff(diff):
    """SG2's counter-case: the skip is keyed on the step's own ⟦test-quality⟧ mark, so an ordinary step's POSSIBLE-BUG
    line is judged by verify-diff like any other report, and adds no repair step."""
    report = "SUITE: ok\n" + POSSIBLE_BUG
    diff(answers={("wait-leaf.sh", "develop-diff"): (3, "")})
    second = diff(answers={("wait-leaf.sh", "verdict-diff"): (3, "")}, report=report)
    third = diff(report=report)

    assert (second[0], second[1].splitlines()[-1]) == (3, "waiting on verdict-diff")
    assert second[3].launched() == ["verdict-diff"]
    assert third[0] == 0, third[2]
    for _, _, _, fake in (second, third):
        assert "add-ledger-step.sh" not in fake.names()
        assert not [c for c in fake.calls if c[0] == "git" and c[1][:1] == ("commit",)]


def test_4760_a_test_quality_step_whose_leaf_reports_neither_a_possible_bug_nor_a_flip_still_launches_verdict_diff(
        diff):
    """SG2's counter-case: without a POSSIBLE-BUG line the test-quality step is judged by verify-diff as before, adds no
    repair step and leaves the run's test-quality record as it was."""
    record = diff.wt / ".tdd" / "issue-12-test-quality"
    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text("fixes=1\n")
    diff(step=QUALITY, answers={("wait-leaf.sh", "develop-diff"): (3, "")})
    code, out, err, fake = diff(step=QUALITY, answers={("wait-leaf.sh", "verdict-diff"): (3, "")}, report="SUITE: ok\n")

    assert (code, out.splitlines()[-1]) == (3, "waiting on verdict-diff")
    assert fake.launched() == ["verdict-diff"]
    assert "add-ledger-step.sh" not in fake.names()
    assert not [c for c in fake.calls if c[0] == "git" and c[1][:1] == ("commit",)]
    assert record.read_text() == "fixes=1\n"


def test_4760_a_quality_repair_step_whose_leaf_reports_a_possible_bug_still_launches_verdict_diff(diff):
    """SG2's counter-case: a ⟦quality-repair⟧ step carries no ⟦test-quality⟧ mark, so its POSSIBLE-BUG line is judged
    by verify-diff like any ordinary diff-checked step's, and the repair adds no further repair step."""
    repair = "fix the split ⟦diff-checked⟧ ⟦quality-repair⟧ ⟦criterion 1⟧"
    report = "SUITE: ok\n" + POSSIBLE_BUG
    diff(step=repair, answers={("wait-leaf.sh", "develop-diff"): (3, "")})
    second = diff(step=repair, answers={("wait-leaf.sh", "verdict-diff"): (3, "")}, report=report)
    third = diff(step=repair, report=report)

    assert (second[0], second[1].splitlines()[-1]) == (3, "waiting on verdict-diff")
    assert second[3].launched() == ["verdict-diff"]
    assert third[0] == 0, third[2]
    for _, _, _, fake in (second, third):
        assert "add-ledger-step.sh" not in fake.names()
        assert not [c for c in fake.calls if c[0] == "git" and c[1][:1] == ("commit",)]


def test_4760_a_test_quality_step_whose_leaf_reports_a_possible_bug_and_no_flip_runs_no_probe_and_ticks(diff):
    """SG2: the strengthened case was reverted, so there is no flip to probe; the step ticks, exit 0."""
    diff(step=QUALITY, answers={("wait-leaf.sh", "develop-diff"): (3, "")})
    code, out, err, fake = diff(step=QUALITY, report="SUITE: ok\n" + POSSIBLE_BUG)

    assert code == 0, err
    assert "mutation-probe.sh" not in fake.names()
    assert "step-tick.sh" in fake.names()


def test_4760_a_test_quality_steps_possible_bug_appends_one_quality_repair_step_last_and_commits_it_as_plan(
        diff, monkeypatch):
    """SG4: the finding becomes one ⟦diff-checked⟧ ⟦quality-repair⟧ step after the ledger's last step, outside the growth
    budget (no ⟦added⟧), carrying the POSSIBLE-BUG line, committed as a plan: commit."""
    monkeypatch.delenv("VERI_QUALITY_REPAIRS", raising=False)
    diff(step=QUALITY, answers={("wait-leaf.sh", "develop-diff"): (3, "")})
    code, out, err, fake = diff(step=QUALITY, report="SUITE: ok\n" + POSSIBLE_BUG)

    steps = [line for line in (diff.wt / ".tdd" / "issue-12.md").read_text().split("\n") if line.startswith("- [")]
    repairs = [line for line in steps if "⟦quality-repair⟧" in line]
    commits = [c[1] for c in fake.calls if c[0] == "git" and c[1][:1] == ("commit",)]
    assert code == 0, err
    assert repairs == [steps[-1]]
    assert ("⟦diff-checked⟧" in repairs[0], "⟦added⟧" in repairs[0], POSSIBLE_BUG.strip() in repairs[0]) == (
        True, False, True)
    assert [a[a.index("-m") + 1].startswith("plan:") for a in commits] == [True]


def test_4760_a_test_quality_step_whose_leaf_reports_a_killed_flip_and_no_possible_bug_appends_no_step(diff):
    """SG4's counter-case: a FLIP: line the probe kills and no POSSIBLE-BUG: line is the ordinary test-quality route, so
    the ledger gains no step and no plan: commit is made."""
    ledger = diff.wt / ".tdd" / "issue-12.md"
    code, out, err, fake = _verified(diff, report="SUITE: ok\n" + FLIP)

    steps = [line for line in ledger.read_text().split("\n") if line.startswith("- [")]
    commits = [c[1] for c in fake.calls if c[0] == "git" and c[1][:1] == ("commit",)]
    assert code == 0, err
    assert "mutation-probe.sh" in fake.names()
    assert (len(steps), [line for line in steps if "⟦quality-repair⟧" in line]) == (3, [])
    assert [a for a in commits if any(str(x).startswith("plan:") for x in a)] == []


def test_4760_a_refused_quality_repair_append_makes_no_plan_commit_does_not_tick_and_stops_exit_2(diff, monkeypatch):
    """SG4's failure path: add-ledger-step.sh refusing the append (the ledger's last step carries no ⟦criterion k⟧ tag
    to inherit) is no answer, so nothing is committed, the step stays open and the run stops exit 2."""
    monkeypatch.delenv("VERI_QUALITY_REPAIRS", raising=False)
    ledger = diff.wt / ".tdd" / "issue-12.md"
    ledger.write_text("# Plan for #12\n\n- [x] zero ⟦criterion 1⟧\n- [ ] %s\n- [ ] two, untagged\n" % QUALITY)
    diff(step=QUALITY, answers={("wait-leaf.sh", "develop-diff"): (3, "")})
    code, out, err, fake = diff(step=QUALITY, report="SUITE: ok\n" + POSSIBLE_BUG)

    commits = [c[1] for c in fake.calls if c[0] == "git" and c[1][:1] == ("commit",)]
    assert code == 2
    assert (commits, "step-tick.sh" in fake.names()) == ([], False)
    assert "⟦quality-repair⟧" not in ledger.read_text()


def test_4760_a_spent_quality_repair_budget_appends_no_step_makes_no_plan_commit_and_ticks_exit_0(diff, monkeypatch):
    """SG5: with VERI_QUALITY_REPAIRS=0 the finding causes no repair step, and a spent budget is not a bail: the step
    ticks, exit 0."""
    monkeypatch.setenv("VERI_QUALITY_REPAIRS", "0")
    ledger = diff.wt / ".tdd" / "issue-12.md"
    diff(step=QUALITY, answers={("wait-leaf.sh", "develop-diff"): (3, "")})
    before = [line for line in ledger.read_text().split("\n") if line.startswith("- [")]
    code, out, err, fake = diff(step=QUALITY, report="SUITE: ok\n" + POSSIBLE_BUG)

    steps = [line for line in ledger.read_text().split("\n") if line.startswith("- [")]
    commits = [c[1] for c in fake.calls if c[0] == "git" and c[1][:1] == ("commit",)]
    assert code == 0, err
    assert (len(steps), [line for line in steps if "⟦quality-repair⟧" in line]) == (len(before), [])
    assert commits == []
    assert "step-tick.sh" in fake.names()


def test_4760_a_ledger_already_holding_one_quality_repair_step_gets_no_second_at_the_default_budget_and_ticks(
        diff, monkeypatch):
    """SG5: VERI_QUALITY_REPAIRS counts the run's ⟦quality-repair⟧ steps; at the default 1, with one already in the
    ledger, a further finding appends no step and makes no plan: commit, and the step ticks, exit 0."""
    monkeypatch.delenv("VERI_QUALITY_REPAIRS", raising=False)
    ledger = diff.wt / ".tdd" / "issue-12.md"
    ledger.write_text((LEDGER % QUALITY) + "- [ ] fix the bug ⟦diff-checked⟧ ⟦quality-repair⟧ ⟦criterion 2⟧\n")
    diff(step=QUALITY, answers={("wait-leaf.sh", "develop-diff"): (3, "")})
    code, out, err, fake = diff(step=QUALITY, report="SUITE: ok\n" + POSSIBLE_BUG)

    repairs = [line for line in ledger.read_text().split("\n") if line.startswith("- [") and "⟦quality-repair⟧" in line]
    commits = [c[1] for c in fake.calls if c[0] == "git" and c[1][:1] == ("commit",)]
    assert code == 0, err
    assert len(repairs) == 1
    assert commits == []
    assert "step-tick.sh" in fake.names()


def test_4760_a_quality_repairs_cap_of_2_with_one_quality_repair_step_already_in_the_ledger_appends_a_second(
        diff, monkeypatch):
    """SG5: the cap is read from VERI_QUALITY_REPAIRS, not fixed at 1: at 2, with one ⟦quality-repair⟧ step already in
    the ledger, a further finding appends a second one, last, as a plan: commit."""
    monkeypatch.setenv("VERI_QUALITY_REPAIRS", "2")
    ledger = diff.wt / ".tdd" / "issue-12.md"
    ledger.write_text((LEDGER % QUALITY) + "- [ ] fix the bug ⟦diff-checked⟧ ⟦quality-repair⟧ ⟦criterion 2⟧\n")
    diff(step=QUALITY, answers={("wait-leaf.sh", "develop-diff"): (3, "")})
    code, out, err, fake = diff(step=QUALITY, report="SUITE: ok\n" + POSSIBLE_BUG)

    steps = [line for line in ledger.read_text().split("\n") if line.startswith("- [")]
    repairs = [line for line in steps if "⟦quality-repair⟧" in line]
    commits = [c[1] for c in fake.calls if c[0] == "git" and c[1][:1] == ("commit",)]
    assert code == 0, err
    assert (len(repairs), repairs[-1] == steps[-1], POSSIBLE_BUG.strip() in repairs[-1]) == (2, True, True)
    assert [a[a.index("-m") + 1].startswith("plan:") for a in commits] == [True]


def test_4760_a_spent_quality_repair_budget_appends_the_possible_bug_to_the_test_quality_record_as_not_fixed(
        diff, monkeypatch):
    """SG5: past VERI_QUALITY_REPAIRS the finding is not repaired, so it lands in .tdd/issue-<n>-test-quality, the record
    the PR body's ### Test quality section renders as `<kind> | <file>::<case> | <why>`, after the lines already there."""
    monkeypatch.setenv("VERI_QUALITY_REPAIRS", "0")
    record = diff.wt / ".tdd" / "issue-12-test-quality"
    earlier = "redundant | tests/test_a.py::test_other | the same as test_split\n"
    record.write_text(earlier)
    diff(step=QUALITY, answers={("wait-leaf.sh", "develop-diff"): (3, "")})
    code, out, err, fake = diff(step=QUALITY, report="SUITE: ok\n" + POSSIBLE_BUG)

    assert code == 0, err
    assert record.read_text() == earlier + (
        "possible-bug | tests/test_a.py::test_split | expects [300, 300, 300], code yields [300, 300, 299];"
        " not fixed: past VERI_QUALITY_REPAIRS\n")


def test_4760_a_possible_bug_within_the_default_budget_leaves_the_test_quality_record_byte_for_byte_unchanged(
        diff, monkeypatch):
    """SG5's counter-case: at the default VERI_QUALITY_REPAIRS with no ⟦quality-repair⟧ step in the ledger, the finding
    is repaired by its own step, so .tdd/issue-<n>-test-quality keeps exactly the bytes it held."""
    monkeypatch.delenv("VERI_QUALITY_REPAIRS", raising=False)
    record = diff.wt / ".tdd" / "issue-12-test-quality"
    earlier = b"redundant | tests/test_a.py::test_other | the same as test_split\n"
    record.write_bytes(earlier)
    diff(step=QUALITY, answers={("wait-leaf.sh", "develop-diff"): (3, "")})
    code, out, err, fake = diff(step=QUALITY, report="SUITE: ok\n" + POSSIBLE_BUG)

    assert code == 0, err
    assert "⟦quality-repair⟧" in (diff.wt / ".tdd" / "issue-12.md").read_text()
    assert record.read_bytes() == earlier
