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


def test_4435_with_diff_switched_off_it_launches_no_verifier_marks_the_skip_writes_skipped_and_goes_on(diff):
    """DST4: ADR-0033's skip, then pin-recheck.sh and the tick in the same call."""
    diff(skip="diff", answers={("wait-leaf.sh", "develop-diff"): (3, "")})
    code, out, err, fake = diff(skip="diff")

    assert code == 0, err
    assert fake.launched() == []
    mark = fake.call("event.sh")
    assert (mark[1], mark[3]["VERI_ACTOR"], mark[3]["VERI_STEP"]) == (
        ("verify-diff-skipped", "reason=switched-off"), "conductor", STEP)
    assert (diff.wt / ".tdd" / "verdict-diff.exit").read_text() == "skipped\n"
    names = fake.names()
    assert names.index("diff-leaf-deviation.sh") < names.index("event.sh") < names.index("pin-recheck.sh") < names.index(
        "step-tick.sh")


ONE = "make test TESTS=\"$1\"\n"
PROBE = ("mutation-probe.sh", ("tests/test_a.py", "assert x == 1", "assert x == 2", "--", "sh", "-c", ONE.strip(), "sh",
                               "tests/test_a.py"))


def _verified(diff, step=QUALITY, **kw):
    """A ⟦test-quality⟧ step's call after its verify-diff PASS; (code, stdout, stderr, fake)."""
    diff(step=step, answers={("wait-leaf.sh", "develop-diff"): (3, "")})
    diff(step=step, answers={("wait-leaf.sh", "verdict-diff"): (3, "")})
    return diff(step=step, **kw)


def test_4435_a_test_quality_step_probes_its_flip_line_after_the_pass_and_before_pin_recheck(diff):
    """DST3: the last FLIP: line of the leaf's report, probed with the `veri: one test file:` command."""
    code, out, err, fake = _verified(diff, report="SUITE: ok\n" + FLIP)

    assert code == 0, err
    names = fake.names()
    assert fake.call("detect-test-command.sh")[1] == ("--tier", "one test file")
    assert (fake.call("mutation-probe.sh")[0], _short(fake.call("mutation-probe.sh")[1])) == PROBE
    assert fake.call("mutation-probe.sh")[4]["out"] == ".tdd/flip-probe.out"
    assert "VERI_MUTATION_RECORD" not in (fake.call("mutation-probe.sh")[3] or {})
    assert names.index("wait-leaf.sh") < names.index("mutation-probe.sh") < names.index("pin-recheck.sh")


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
def test_4435_a_flip_that_stays_green_or_no_flip_line_is_a_verify_diff_reject_exit_1_before_pin_recheck(
        diff, report, answers, reason):
    """DST3: the reason written to .tdd/verify-diff.reason; no pin-recheck.sh, no tick."""
    code, out, err, fake = _verified(diff, report=report, answers=answers)

    assert code == 1, err
    assert (diff.wt / ".tdd" / "verify-diff.reason").read_text() == reason
    assert not {"pin-recheck.sh", "step-tick.sh"} & set(fake.names())


@pytest.mark.parametrize("answers", [{("mutation-probe.sh", None): (2, "")},
                                     {("detect-test-command.sh", None): (2, "")}])
def test_4435_a_probe_or_detect_test_command_exit_2_is_exit_2(diff, answers):
    """DST3: no answer, never a REJECT."""
    code, out, err, fake = _verified(diff, report=FLIP, answers=answers)

    assert code == 2
    assert not {"pin-recheck.sh", "step-tick.sh"} & set(fake.names())
    assert not (diff.wt / ".tdd" / "issue-12-diff-step-rejected-wait").exists()


def _rejected(diff):
    path = diff.wt / ".tdd" / "issue-12-diff-step-rejected-wait"
    return json.loads(path.read_text()) if path.exists() else None


@pytest.mark.parametrize("step, answers, report", [
    (STEP, {("wait-leaf.sh", "verdict-diff"): (1, "")}, None),
    (QUALITY, {("mutation-probe.sh", None): (1, "")}, FLIP),
    (STEP, {("pin-recheck.sh", None): (1, "kept green: tests/test_a.py\n")}, None),
])
def test_4435_a_verify_flip_or_pin_recheck_reject_leaves_the_steps_rejected_record_for_revise_and_exits_1(
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


def test_4435_a_pin_recheck_reject_writes_its_report_as_the_reason(diff):
    """DST7: the pins pin-recheck.sh printed are what the revise leaf is told."""
    diff(answers={("wait-leaf.sh", "develop-diff"): (3, "")})
    diff(answers={("wait-leaf.sh", "verdict-diff"): (3, "")})
    diff(answers={("pin-recheck.sh", None): (1, "kept green: tests/test_a.py\n")})

    assert (diff.wt / ".tdd" / "verify-diff.reason").read_text() == (
        "REJECT: pin-recheck.sh found a pin this step disarmed\nkept green: tests/test_a.py\n")


def test_4435_a_pin_recheck_exit_2_is_exit_2_with_no_rejected_record(diff):
    diff(answers={("wait-leaf.sh", "develop-diff"): (3, "")})
    diff(answers={("wait-leaf.sh", "verdict-diff"): (3, "")})
    code, out, err, fake = diff(answers={("pin-recheck.sh", None): (2, "")})

    assert (code, _rejected(diff)) == (2, None)


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
    assert not {"mutation-probe.sh", "pin-recheck.sh"} & set(fake.names())
    assert (diff.wt / ".tdd" / "verify-diff.reason").read_text().startswith("REJECT: the report of develop-diff")


def test_4435_a_develop_diff_leaf_with_no_suite_line_stops_exit_2_with_no_verifier(diff):
    """DST1, CY92: suite-reported.sh exit 2 launches no verifier; the adjudication is the conductor's."""
    diff(answers={("wait-leaf.sh", "develop-diff"): (3, "")})
    code, out, err, fake = diff(answers={("suite-reported.sh", None): (2, "")})

    assert (code, out.splitlines()[-1]) == (2, "stopped at develop suite-reported.sh develop-diff 2> "
                                                ".tdd/suite-reported.err exit 2")
    assert (fake.launched(), "diff-leaf-deviation.sh" in fake.names()) == ([], False)


REPIN = ("⟦diff-checked⟧ edit the case of the pin on tests/test_a.py so its recorded mutation turns it red "
         "⟦added⟧ ⟦criterion 1⟧")
GREEN = "d" * 40
GREEN_PARENT = "e" * 40


class RepinHistory(Fake):
    """The history of a re-pin step: the ledger's last commit before the re-pin plan commit (STEP_BASE) is GREEN, the
    green tick of the step whose pin it re-arms, and GREEN~1 is GREEN_PARENT; pin-recheck.sh finds the disarmed pin
    (exit 1) only over a range from GREEN_PARENT, and nothing to check (exit 3) from any later base."""

    def __call__(self, name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        if base == "git" and args[:2] == ("log", "-1") and STEP_BASE + "~1" in args:
            self.calls.append((base, args, cwd, env, kw))
            return 0, GREEN + "\n", ""
        if base == "git" and args[:1] == ("rev-parse",) and GREEN + "~1" in args:
            self.calls.append((base, args, cwd, env, kw))
            return 0, GREEN_PARENT + "\n", ""
        if base == "pin-recheck.sh":
            self.calls.append((base, args, cwd, env, kw))
            if args[-1:] == (GREEN_PARENT,):
                return 1, "pin stayed green under its mutation: tests/test_a.py\n", ""
            return 3, "", ""
        return super().__call__(name, *args, cwd=cwd, env=env, **kw)


def test_4511_a_repin_step_rechecks_from_the_rearmed_steps_green_parent_so_a_pin_left_green_is_a_reject(diff):
    """A re-pin step's pin-recheck.sh range starts at <green>~1 of the step whose pin it re-arms, so a re-pin that
    leaves the pin green under its mutation is a verify-diff REJECT, not a tick."""
    diff(step=REPIN, answers={("wait-leaf.sh", "develop-diff"): (3, "")})
    diff(step=REPIN, answers={("wait-leaf.sh", "verdict-diff"): (3, "")})
    code, out, err, fake = diff(step=REPIN, fake=RepinHistory())

    assert code == 1, err
    assert fake.call("pin-recheck.sh")[1] == ("--branch-base", BRANCH_BASE, GREEN_PARENT)
    record = _rejected(diff)
    assert (record["step"], record["at"]) == (REPIN, "verdict-diff")
    assert "step-tick.sh" not in fake.names()


def test_4511_the_step_pin_reject_route_adds_on_a_disarmed_pin_is_rechecked_by_diff_step_as_a_repin(
        diff, run_cli, tmp_path, fake_processes):
    """The re-pin line pin-reject-route.sh --recheck writes is the one diff-step recognises as a re-pin step: its
    pin-recheck.sh range starts at the re-armed step's <green>~1, so the two cannot drift apart."""
    route = importlib.import_module("veri.pin_reject_route")
    planned = tmp_path / "route" / ".tdd" / "issue-12.md"
    planned.parent.mkdir(parents=True)
    planned.write_text("# Plan for #12\n\n- [x] zero ⟦criterion 1⟧\n- [ ] two ⟦criterion 2⟧\n")
    fake_processes.answers({"git log --format=%H %s": (0, "beef plan: scope #12 into 2 steps (#12)\n", ""),
                            "git show beef:./issue-12.md": (0, planned.read_text(), "")})
    reason = tmp_path / "route" / "reason.txt"
    reason.write_text("pin stayed green under its mutation: tests/test_a.py\n")
    code, out, err = run_cli(route, ["--recheck", str(reason), str(planned), "zero"], env={"VERI_ISSUE": "12"},
                             cwd=str(planned.parent.parent))
    assert (code, out.strip()) == (0, "repin tests/test_a.py"), err
    step = planned.read_text().splitlines()[3].split("] ", 1)[1]

    diff(step=step, answers={("wait-leaf.sh", "develop-diff"): (3, "")})
    diff(step=step, answers={("wait-leaf.sh", "verdict-diff"): (3, "")})
    code, out, err, fake = diff(step=step, fake=RepinHistory())

    assert (code, fake.call("pin-recheck.sh")[1]) == (1, ("--branch-base", BRANCH_BASE, GREEN_PARENT)), err
