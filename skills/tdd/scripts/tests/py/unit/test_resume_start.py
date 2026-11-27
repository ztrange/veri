"""In-process cases for veri/resume_start.py, the module resume-start.sh is a shim over (PRD 038.6, #4389)."""
import importlib
import os

import pytest

PLAN_SHA = "c" * 40
PR_URL = "https://github.com/o/r/pull/77"
LEDGER = "# Plan for #12\n\n- [x] one ⟦criterion 1⟧\n- [ ] two ⟦criterion 2⟧\n"
SPEC = "## Problem\n\nA thing.\n\n## Acceptance criteria\n\n- [x] first\n- [ ] second\n"


class Fake:
    """A run_script stand-in: records (basename, args, cwd, env, kw) and answers from <answers>, keyed by
    (basename, first argument or None) -> (code, stdout)."""

    def __init__(self, answers=None, pr=PR_URL + "\n", planned=LEDGER):
        self.answers, self.calls, self.pr, self.planned = dict(answers or {}), [], pr, planned

    def __call__(self, name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        self.calls.append((base, args, cwd, env, kw))
        for (script, first), (code, out) in self.answers.items():
            if base == script and (first is None or args[:1] == (first,)):
                return code, out, ""
        if base == "next-pending-refactor.sh":
            return 3, "", ""
        if base == "next-unchecked.sh":
            return 0, "two ⟦criterion 2⟧\n", ""
        if base == "ledger-steps.sh":
            return 0, "two ⟦criterion 2⟧\n", ""
        if base == "git" and args[:1] == ("log",):
            return 0, PLAN_SHA + " plan: scope #12 into 2 steps (#12)\n", ""
        if base == "ledger-growth.sh" and args[:1] == ("plan-sha",):
            return 0, PLAN_SHA + "\n", ""
        if base == "git" and args[:1] == ("show",):
            return 0, self.planned, ""
        if base == "git" and args == ("branch", "--show-current"):
            return 0, "tdd/12-a-thing\n", ""
        if base == "gh":
            return 0, self.pr, ""
        if base == "stop-requested.sh":
            return 3, "", ""
        return 0, "", ""

    def names(self):
        return [c[0] for c in self.calls]

    def call(self, base, first=None):
        return next(c for c in self.calls if c[0] == base and (first is None or c[1][:1] == (first,)))


BRANCH_BASE = "abc1234"  # the run's recorded branch base (#4375)


@pytest.fixture
def resume(monkeypatch, run_cli, tmp_path):
    """resume(answers=None, fake=None, missing=(), verify_plan="skip", argv=None) runs resume-start for issue 12 from
    the main tree, the run's worktree at .tdd/wt/12; returns (code, stdout, stderr, fake)."""
    fused = importlib.import_module("veri.fused")
    resume_start = importlib.import_module("veri.resume_start")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)

    def go(answers=None, fake=None, missing=(), verify_plan="skip", argv=None, stray=()):
        files = {"branch_base": (wt / ".tdd" / "issue-12-branch-base", BRANCH_BASE + "\n"),
                 "preflight": (wt / ".tdd" / "issue-12-preflight",
                               "worktree=%s\nfast_cmd=make unit\ndefault_branch=main\nrun=resume\n" % wt
                               + "".join("stray=%s\n" % path for path in stray)),
                 "ledger": (wt / ".tdd" / "issue-12.md", LEDGER),
                 "run-start": (wt / ".tdd" / "issue-12-run-start",
                               "run=resume\nspec=.tdd/issue-12-spec.md\nverify_plan=%s\n" % verify_plan),
                 "spec": (wt / ".tdd" / "issue-12-spec.md", SPEC)}
        for key, (path, text) in files.items():
            if key not in missing and not path.exists():
                path.write_text(text)
        fake = fake or Fake(answers)
        monkeypatch.setattr(fused, "run_script", fake)
        code, out, err = run_cli(resume_start, list(argv if argv is not None else ("12",)), cwd=str(tmp_path))
        return code, out, err, fake

    go.wt = wt
    return go


@pytest.mark.parametrize("argv", [(), ("x",), ("12", "13")])
def test_4389_bad_arguments_print_the_usage_and_exit_2_with_no_inner_call(resume, argv):
    code, out, err, fake = resume(argv=argv)

    assert (code, "resume-start.sh <n>" in err, fake.calls) == (2, True, [])


@pytest.mark.parametrize("missing, named", [("preflight", ".tdd/issue-12-preflight"), ("ledger", ".tdd/issue-12.md"),
                                            ("run-start", ".tdd/issue-12-run-start")])
def test_4389_a_missing_input_is_exit_2_before_any_inner_call_named_on_stderr(resume, missing, named):
    code, out, err, fake = resume(missing=(missing,))

    assert (code, fake.calls) == (2, [])
    assert named in err


def _seq(fake):
    return [(c[0], c[1][:2]) for c in fake.calls]


def _scripts(fake):
    return [c[0] for c in fake.calls if c[0] not in ("git", "gh")]


def test_4389_a_clean_resume_asks_for_a_pending_refactor_then_the_step_marks_and_comments_and_reads_the_pr(resume):
    code, out, err, fake = resume(stray=("tests/t.py", "x.py"))

    assert [c for c in _seq(fake) if c[1][:1] not in (("log",), ("show",), ("plan-sha",))] == [
        ("next-pending-refactor.sh", ()), ("next-unchecked.sh", ()), ("ledger-steps.sh", ("current-or-last-done",)),
        ("event.sh", ("resume",)), ("comment.sh", ("12", "resuming")), ("git", ("branch", "--show-current")),
        ("gh", ("api", "repos/{owner}/{repo}/pulls?head={owner}:tdd/12-a-thing"))]
    assert {c[4].get("stdin") for c in fake.calls if c[0] != "git" and c[1][:1] != ("plan-sha",)} - {None} == {LEDGER}
    assert {c[2] for c in fake.calls} == {str(resume.wt)}
    mark = fake.call("event.sh")[3]
    assert (mark["VERI_ISSUE"], mark["VERI_ACTOR"], mark["VERI_STEP"]) == ("12", "conductor", "two ⟦criterion 2⟧")
    comment = fake.call("comment.sh")[1]
    assert comment[2] == "--note-file"
    note = (resume.wt / comment[3]).read_text()
    assert ("two ⟦criterion 2⟧" in note, "`tests/t.py`" in note, "`x.py`" in note) == (True, True, True)
    assert fake.call("gh")[1][2:] == ("-q", ".[0].html_url // empty")
    assert code == 0


def test_4389_a_resume_with_no_stray_path_names_none_in_its_note(resume):
    code, out, err, fake = resume()

    comment = fake.call("comment.sh")[1]
    assert "discarded" not in (resume.wt / comment[3]).read_text()


def test_4389_a_ledger_grown_beyond_its_plan_commit_with_no_record_is_recorded_and_committed_after_no_pending_refactor(
        resume):
    code, out, err, fake = resume(fake=Fake(planned="# Plan for #12\n\n- [x] one ⟦criterion 1⟧\n"))

    assert fake.call("ledger-growth.sh", "plan-sha")[4]["stdin"] == PLAN_SHA + " plan: scope #12 into 2 steps (#12)\n"
    assert fake.call("git", "show")[1] == ("show", PLAN_SHA + ":.tdd/issue-12.md")
    assert [c for c in _seq(fake) if c[0] != "git" or c[1][:1] in (("add",), ("commit",))][:6] == [
        ("next-pending-refactor.sh", ()), ("ledger-growth.sh", ("plan-sha",)),
        ("ledger-growth.sh", ("record-existing", ".tdd/issue-12.md")), ("git", ("add", ".tdd/issue-12-added.md")),
        ("git", ("commit", "-m")), ("next-unchecked.sh", ())]
    assert fake.call("git", "commit")[1][2] == "chore: record the steps the ledger grew before its record (#12)"
    assert code == 0


def test_4389_a_ledger_no_larger_than_its_plan_commit_is_not_recorded(resume):
    code, out, err, fake = resume()

    assert (("record-existing",) in [c[1][:1] for c in fake.calls],
            "commit" in [c[1][0] for c in fake.calls if c[0] == "git"]) == (False, False)


def test_4389_a_ledger_whose_record_exists_is_neither_read_at_its_plan_commit_nor_recorded(resume):
    (resume.wt / ".tdd" / "issue-12-added.md").write_text("- [ ] two ⟦criterion 2⟧\n")
    code, out, err, fake = resume(fake=Fake(planned="# Plan for #12\n"))

    assert ("ledger-growth.sh" in fake.names(), [c for c in fake.calls if c[0] == "git" and c[1][0] != "branch"]) == (
        False, [])


def test_4389_a_saved_branch_red_list_inserts_the_repair_step_after_the_resuming_comment(resume):
    (resume.wt / ".tdd" / "resume-suite-red").write_text("tests/py/test_a.py\n")
    code, out, err, fake = resume()

    assert _scripts(fake)[-2:] == ["comment.sh", "suite-red-resume.sh"]
    assert fake.call("suite-red-resume.sh")[1] == ("insert", ".tdd/issue-12.md", ".tdd/resume-suite-red")
    assert code == 0


def test_4389_no_saved_branch_red_list_inserts_nothing(resume):
    code, out, err, fake = resume()

    assert "suite-red-resume.sh" not in fake.names()


def test_4389_exit_0_settles_the_step_the_pr_and_the_verdict_and_prints_them_last(resume):
    code, out, err, fake = resume()

    settled = "step=two ⟦criterion 2⟧\npr_url=%s\nverify_plan=skip\n" % PR_URL
    assert (code, (resume.wt / ".tdd" / "issue-12-resume-start").read_text(), out.endswith(settled)) == (
        0, settled, True)


def test_4389_every_step_checked_settles_an_empty_step(resume):
    code, out, err, fake = resume(answers={("next-unchecked.sh", None): (3, "")})

    assert (code, (resume.wt / ".tdd" / "issue-12-resume-start").read_text().splitlines()[0]) == (0, "step=")


LAUNCH_TAIL = ("supervise.sh", "verdict-plan", "run-verdict.sh", "--branch-base", BRANCH_BASE, "plan",
               ".tdd/issue-12-spec.md", ".tdd/issue-12.md")


def _after_pr(fake):
    return fake.calls[fake.names().index("gh") + 1:]


def test_4389_an_owed_verify_plan_checks_for_a_stop_launches_verdict_plan_waits_and_comments_on_a_pass(resume):
    (resume.wt / ".tdd" / "verdict-plan.exit").write_text("1\n")
    (resume.wt / ".tdd" / "verdict-plan.pid").write_text("99\n")
    code, out, err, fake = resume(verify_plan="owed")

    tail = _after_pr(fake)
    assert [c[0] for c in tail] == ["stop-requested.sh", "detach-leaf.sh", "wait-leaf.sh", "comment.sh"]
    launch = tail[1]
    assert tuple(os.path.basename(a) if a.endswith(".sh") else a for a in launch[1]) == LAUNCH_TAIL
    assert all(os.path.isabs(a) for a in launch[1] if a.endswith(".sh"))
    assert (launch[3]["VERI_TEST_CMD"], launch[3]["VERI_ISSUE"]) == ("make unit", "12")
    assert (launch[4]["out"], launch[4]["err"]) == (".tdd/verify-plan.reason", ".tdd/verify-plan.err")
    assert (tail[2][1], tail[3][1]) == (("verdict-plan",), ("12", "verify-plan"))
    assert not (resume.wt / ".tdd" / "verdict-plan.exit").exists()
    assert not (resume.wt / ".tdd" / "verdict-plan.pid").exists()
    assert (code, out.splitlines()[-1]) == (0, "verify_plan=PASS")


def test_4389_a_skipped_verify_plan_launches_nothing(resume):
    code, out, err, fake = resume(verify_plan="skip")

    assert (code, _after_pr(fake)) == (0, [])


def test_4389_it_never_opens_the_event_log(resume):
    (resume.wt / ".tdd" / "events.jsonl").mkdir()
    code, out, err, fake = resume(verify_plan="owed")

    assert (code, out.splitlines()[-1]) == (0, "verify_plan=PASS")


def test_4389_a_wait_whose_slice_ran_out_exits_3_on_a_waiting_on_line_and_keeps_a_record(resume):
    code, out, err, fake = resume(verify_plan="owed", answers={("wait-leaf.sh", None): (3, "")})

    assert (code, out.splitlines()[-1], "comment.sh" in fake.names()[-1:]) == (3, "waiting on verdict-plan", False)
    assert (resume.wt / ".tdd" / "issue-12-resume-start-wait").exists()


def test_4389_called_again_after_an_exit_3_it_only_waits_again_then_comments_and_settles(resume):
    resume(verify_plan="owed", answers={("wait-leaf.sh", None): (3, "")})
    code, out, err, fake = resume(verify_plan="owed")

    assert [(c[0], c[1]) for c in fake.calls] == [("wait-leaf.sh", ("verdict-plan",)), ("comment.sh", ("12", "verify-plan"))]
    assert (code, out.splitlines()[-3:]) == (0, ["step=two ⟦criterion 2⟧", "pr_url=" + PR_URL, "verify_plan=PASS"])
    assert not (resume.wt / ".tdd" / "issue-12-resume-start-wait").exists()


def test_4389_called_under_another_conductor_it_discards_the_record_and_starts_from_its_first_call(resume):
    resume(verify_plan="owed", answers={("wait-leaf.sh", None): (3, "")})
    (resume.wt / ".tdd" / "conductor.pid").write_text("4242\nThu Nov 19 10:00:00 2026\n")
    code, out, err, fake = resume(verify_plan="owed")

    assert (code, _scripts(fake)[:2]) == (0, ["next-pending-refactor.sh", "ledger-growth.sh"])


@pytest.mark.parametrize("answers, pr, where, last", [
    ({("next-pending-refactor.sh", None): (0, "one\n")}, PR_URL, "2", "next-pending-refactor.sh"),
    ({("suite-red-resume.sh", None): (1, "")}, PR_URL, "4", "suite-red-resume.sh"),
    ({("suite-red-resume.sh", None): (2, "")}, PR_URL, "4", "suite-red-resume.sh"),
    ({}, "", "4", "gh"),
    ({("wait-leaf.sh", None): (1, "")}, PR_URL, "4", "wait-leaf.sh")])
def test_4389_each_judgement_stops_it_with_exit_1_naming_the_sub_step_and_makes_no_later_call(
        resume, answers, pr, where, last):
    (resume.wt / ".tdd" / "resume-suite-red").write_text("tests/py/test_a.py\n")
    code, out, err, fake = resume(fake=Fake(answers, pr=pr), verify_plan="owed")

    assert (code, out.splitlines()[-1].startswith("stopped at %s " % where), fake.names()[-1]) == (1, True, last)


def test_4389_an_unticked_criterion_no_ledger_step_serves_stops_it_at_3_before_the_pick(resume):
    (resume.wt / ".tdd" / "issue-12-spec.md").write_text(SPEC + "- [ ] third\n")
    code, out, err, fake = resume()

    assert (code, out.splitlines()[-1], "next-unchecked.sh" in fake.names()) == (
        1, "stopped at 3 criterion 3 no ledger step serves", False)


def test_4389_a_ticked_criterion_no_ledger_step_serves_does_not_stop_it(resume):
    (resume.wt / ".tdd" / "issue-12-spec.md").write_text(SPEC + "- [x] third\n")
    code, out, err, fake = resume()

    assert code == 0


def test_4389_every_inner_call_prints_one_line_with_its_exit_and_never_the_leafs_report(resume):
    (resume.wt / ".tdd" / "verify-plan.reason").write_text("LEAF-REPORT\n")
    code, out, err, fake = resume(verify_plan="owed")

    lines = out.splitlines()
    for base, _args, *_ in fake.calls:
        assert [line for line in lines if line.startswith(base + " ") and " exit " in line], base
    assert "LEAF-REPORT" not in out


@pytest.mark.parametrize("answers", [{("next-pending-refactor.sh", None): (0, "one\n")},
                                     {("wait-leaf.sh", None): (1, "")}, {("comment.sh", None): (2, "")}])
def test_4389_a_stop_writes_no_bail_event_and_classifies_no_bail(resume, answers):
    code, out, err, fake = resume(verify_plan="owed", answers=answers)

    assert code != 0
    assert ("classify-bail.sh" in fake.names(), [c for c in fake.calls if c[0] == "event.sh" and "bail" in c[1]]) == (
        False, [])


def test_4389_every_inner_call_in_the_ordered_list_is_a_script_resume_md_or_skill_md_step_2c_names():
    resume_start = importlib.import_module("veri.resume_start")
    here = os.path.join(os.path.dirname(resume_start.__file__), "..", "..")
    with open(os.path.join(here, "RESUME.md")) as f, open(os.path.join(here, "SKILL.md")) as g:
        prose = f.read() + g.read()

    assert [name for name in resume_start.CALLS if "$S/" + name not in prose] == []


def test_4389_a_clean_run_makes_the_calls_of_the_ordered_list_in_its_order(resume):
    resume_start = importlib.import_module("veri.resume_start")
    (resume.wt / ".tdd" / "resume-suite-red").write_text("tests/py/test_a.py\n")
    code, out, err, fake = resume(fake=Fake(planned="# Plan for #12\n"), verify_plan="owed")

    made = [name for name in fake.names() if name not in ("git", "gh")]
    assert code == 0
    assert set(made) | {"supervise.sh", "run-verdict.sh"} == set(resume_start.CALLS)
    firsts = [made.index(name) for name in resume_start.CALLS if name not in ("supervise.sh", "run-verdict.sh")]
    assert firsts == sorted(firsts)


@pytest.mark.parametrize("verify_plan", ["", "maybe"])
def test_4389_a_run_start_record_with_no_resume_verdict_is_exit_2_before_any_inner_call(resume, verify_plan):
    code, out, err, fake = resume(verify_plan=verify_plan)

    assert (code, fake.calls, "verify_plan=" in err) == (2, [], True)


def test_4389_a_grown_ledger_with_no_record_and_a_pending_refactor_stops_at_2_with_no_record_and_no_commit(resume):
    code, out, err, fake = resume(fake=Fake({("next-pending-refactor.sh", None): (0, "one ⟦criterion 1⟧\n")},
                                            planned="# Plan for #12\n"))

    assert (code, out.splitlines()[-1].split(" ")[:3], fake.names()) == (
        1, ["stopped", "at", "2"], ["next-pending-refactor.sh"])
    assert not (resume.wt / ".tdd" / "issue-12-added.md").exists()


def test_4389_a_verify_plan_with_no_answer_is_exit_2_posting_no_verify_plan_comment_and_settling_nothing(resume):
    code, out, err, fake = resume(verify_plan="owed", answers={("wait-leaf.sh", None): (2, "")})

    assert (code, out.splitlines()[-1], fake.names()[-1]) == (2, "stopped at 4 wait-leaf.sh verdict-plan exit 2",
                                                              "wait-leaf.sh")
    assert (("12", "verify-plan") in [c[1][:2] for c in fake.calls if c[0] == "comment.sh"],
            (resume.wt / ".tdd" / "issue-12-resume-start").exists()) == (False, False)


def test_4389_a_stop_requested_with_no_answer_before_verify_plan_is_exit_2_and_launches_nothing(resume):
    code, out, err, fake = resume(verify_plan="owed", answers={("stop-requested.sh", None): (2, "")})

    assert (code, fake.names()[-1], "detach-leaf.sh" in fake.names()) == (2, "stop-requested.sh", False)


def test_4389_a_missing_spec_is_exit_2_at_3_before_the_pick(resume):
    code, out, err, fake = resume(missing=("spec",))

    assert (code, out.splitlines()[-1], "next-unchecked.sh" in fake.names()) == (
        2, "stopped at 3 no .tdd/issue-12-spec.md", False)


@pytest.mark.parametrize("failing, code_given, where", [
    (("git", "log"), 128, "1"), (("git", "show"), 128, "1"), (("git", "add"), 128, "1"), (("git", "commit"), 1, "1"),
    (("git", "branch"), 128, "4"), (("gh", None), 1, "4"), (("gh", None), 4, "4")])
def test_4389_a_failing_git_or_gh_call_is_exit_2_never_its_own_code(resume, failing, code_given, where):
    code, out, err, fake = resume(fake=Fake({failing: (code_given, "")}, planned="# Plan for #12\n"))

    assert (code, out.splitlines()[-1].startswith("stopped at %s %s " % (where, failing[0])),
            fake.names()[-1]) == (2, True, failing[0])
