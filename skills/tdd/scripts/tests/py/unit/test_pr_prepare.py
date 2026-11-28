"""In-process cases for veri/pr_prepare.py, the module pr-prepare.sh is a shim over (PRD 027.9, #4031)."""
import importlib
import json
import os

import pytest

LEDGER = "# Plan for #12\n\n- [x] one ⟦criterion 1⟧\n- [ ] the full suite is green ⟦full-suite⟧ ⟦criterion 2⟧\n"
PRE = "a" * 40
BASE = "b" * 40
FULL = "make test"
SIGNED = "skills/tdd/REQUIREMENTS.md\tskills/tdd/SKILL.md#Two words\nREQUIREMENTS.md\tREADME.md\n"


class Fake:
    """A run_script stand-in: records (basename, args, cwd, env, kw) and answers from <answers>, keyed by
    (basename, first argument, a tuple of leading arguments, or None) -> (code, stdout)."""

    def __init__(self, answers=None, porcelain=("", ""), mode="local"):
        self.answers, self.calls, self.mode = dict(answers or {}), [], mode
        self.porcelain = list(porcelain)

    def __call__(self, name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        self.calls.append((base, args, cwd, env, kw))
        for (script, first), (code, out) in self.answers.items():
            lead = first if isinstance(first, tuple) else (first,)
            if base == script and (first is None or args[:len(lead)] == lead):
                return code, out, ""
        if base == "git" and args[:2] == ("status", "--porcelain"):
            return 0, self.porcelain.pop(0) if self.porcelain else "", ""
        if base == "git" and args[:1] == ("merge-base",):
            return 0, BASE + "\n", ""
        if base == "grade-prose.sh" and args[:1] == ("--signed",):
            return 0, SIGNED, ""
        if base == "git" and args[:1] == ("branch",):
            return 0, "tdd/12-x\n", ""
        if base == "next-pending-refactor.sh":
            return 3, "", ""
        if base == "rebase-onto-default.sh":
            return 0, PRE + "\nrebased onto origin/main\n", ""
        if base == "rebased-tip-suite.sh":
            return 0, self.mode + "\n", ""
        if base == "detect-test-command.sh":
            return 0, FULL + "\n", ""
        if base == "detach-command.sh" and args[:1] == ("wait",):
            return 0, "PASSED 812\n", ""
        if base == "refactor-owed.sh":
            return 3, "", ""
        return 0, "", ""

    def names(self):
        return [c[0] for c in self.calls]

    def call(self, base, first=None):
        return next(c for c in self.calls if c[0] == base and (first is None or c[1][:1] == (first,)))


@pytest.fixture
def prep(monkeypatch, run_cli, tmp_path):
    """prep(answers=None, fake=None, missing=(), argv=None) runs pr-prepare for issue 12 from the main tree, the
    run's worktree at .tdd/wt/12; returns (code, stdout, stderr, fake)."""
    fused = importlib.import_module("veri.fused")
    pr_prepare = importlib.import_module("veri.pr_prepare")
    monkeypatch.setattr(pr_prepare, "default_branch", lambda wt: "main")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)

    def go(answers=None, fake=None, missing=(), argv=None):
        files = {"preflight": (wt / ".tdd" / "issue-12-preflight", "worktree=%s\nfast_cmd=make unit\n" % wt),
                 "ledger": (wt / ".tdd" / "issue-12.md", LEDGER)}
        for key, (path, text) in files.items():
            if key not in missing:
                path.write_text(text)
        fake = fake or Fake(answers)
        monkeypatch.setattr(fused, "run_script", fake)
        code, out, err = run_cli(pr_prepare, list(argv if argv is not None else ("12",)), cwd=str(tmp_path))
        return code, out, err, fake

    go.wt = wt
    return go


def test_4031_no_argument_prints_the_usage_and_exits_2_with_no_inner_call(prep):
    code, out, err, fake = prep(argv=())

    assert (code, "pr-prepare.sh <n>" in err, fake.calls) == (2, True, [])
    here = os.path.dirname(importlib.import_module("veri.pr_prepare").__file__)
    assert os.path.exists(os.path.join(here, "..", "pr-prepare.sh"))


@pytest.mark.parametrize("missing, named", [("preflight", ".tdd/issue-12-preflight"), ("ledger", ".tdd/issue-12.md")])
def test_4031_a_missing_input_is_exit_2_before_any_inner_call_named_on_stderr(prep, missing, named):
    code, out, err, fake = prep(missing=(missing,))

    assert (code, fake.calls) == (2, [])
    assert named in err


def test_4031_a_dirty_tree_stops_it_with_exit_1_before_any_other_call(prep):
    code, out, err, fake = prep(fake=Fake(porcelain=(" M src/a.py\n",)))

    assert (code, out.splitlines()[-1]) == (1, "stopped at 1 tree-check")
    assert [c[0] for c in fake.calls] == ["git"]


def test_4031_a_step_still_only_green_stops_it_with_exit_1_before_the_rebase(prep):
    code, out, err, fake = prep(answers={("next-pending-refactor.sh", None): (0, "one ⟦criterion 1⟧\n")})

    assert (code, out.splitlines()[-1]) == (1, "stopped at 1 next-pending-refactor.sh exit 0")
    assert fake.names() == ["git", "next-pending-refactor.sh"]
    assert fake.call("next-pending-refactor.sh")[4]["stdin"] == LEDGER


def test_4031_a_next_pending_refactor_with_no_answer_stops_it_with_exit_2(prep):
    code, out, err, fake = prep(answers={("next-pending-refactor.sh", None): (2, "")})

    assert (code, fake.names()[-1]) == (2, "next-pending-refactor.sh")


def _calls(fake):
    return [(c[0], c[1]) for c in fake.calls]


def test_4031_a_clean_rebase_regrades_runs_the_local_suite_checks_the_tree_pushes_under_the_lease_and_skips_the_pass(
        prep):
    pr_prepare = importlib.import_module("veri.pr_prepare")
    code, out, err, fake = prep()

    assert code == 0, out + err
    assert _calls(fake) == [
        ("git", ("status", "--porcelain", "--untracked-files=all")), ("next-pending-refactor.sh", ()),
        ("rebase-onto-default.sh", ()),
        ("git", ("merge-base", "HEAD", "origin/main")),
        ("grade-prose.sh", ("--signed", BASE)),
        ("git", ("status", "--porcelain", "--untracked-files=all")),
        ("detach-command.sh", ("start", "regrade-12", "sh", "-c", pr_prepare.BLOCK, "sh",
                               os.path.dirname(pr_prepare.fused.script("grade-prose.sh")),
                               "skills/tdd/REQUIREMENTS.md", "skills/tdd/SKILL.md#Two words", "REQUIREMENTS.md",
                               "README.md")),
        ("detach-command.sh", ("wait", "regrade-12")),
        ("git", ("status", "--porcelain", "--untracked-files=all")),
        ("rebased-tip-suite.sh", ()), ("detect-test-command.sh", ("--tier", "all")),
        ("detach-command.sh", ("start", "rebased-full-12", "sh", "-c", "make test")),
        ("detach-command.sh", ("wait", "rebased-full-12")),
        ("git", ("status", "--porcelain", "--untracked-files=all")), ("git", ("branch", "--show-current")),
        ("push-branch.sh", ("--force-with-lease=tdd/12-x:" + PRE,)),
        ("refactor-owed.sh", ("list", ".tdd/issue-12-refactor-owed.md")),
        ("event.sh", ("structural-pass", "stopped=nothing-structural"))]
    skip = fake.call("event.sh")[3]
    assert (skip["VERI_ISSUE"], skip["VERI_ACTOR"]) == ("12", "conductor")
    assert all(c[2] == str(prep.wt) for c in fake.calls)
    settled = "rebased=1\nrebased_from=%s\nrebased_tip_suite=local\n" % PRE
    assert out.endswith(settled)
    assert (prep.wt / ".tdd" / "issue-12-pr-prepare").read_text() == settled


def test_4031_under_ci_the_rebased_tip_gets_no_local_run_and_is_pushed(prep):
    code, out, err, fake = prep(fake=Fake(mode="ci"))

    assert code == 0
    assert [c[1][:2] for c in fake.calls if c[0] == "detach-command.sh"] == [("start", "regrade-12"),
                                                                           ("wait", "regrade-12")]
    assert "push-branch.sh" in fake.names()
    assert out.splitlines()[-1] == "rebased_tip_suite=ci"


def test_4031_no_rebase_regrades_then_goes_to_the_refactor_owed_list_pushing_nothing(prep):
    code, out, err, fake = prep(answers={("rebase-onto-default.sh", None): (3, "")})

    assert code == 0
    assert not {"rebased-tip-suite.sh", "push-branch.sh"} & set(fake.names())
    assert [c[1][:2] for c in fake.calls if c[0] == "detach-command.sh"] == [("start", "regrade-12"),
                                                                           ("wait", "regrade-12")]
    assert out.endswith("rebased=0\nrebased_from=\nrebased_tip_suite=none\n")


@pytest.mark.parametrize("inner", [1, 2])
def test_4031_a_conflicted_or_refused_rebase_stops_it_with_its_code(prep, inner):
    code, out, err, fake = prep(answers={("rebase-onto-default.sh", None): (inner, "src/a.py\n")})

    assert (code, fake.names()[-1]) == (inner, "rebase-onto-default.sh")
    assert out.splitlines()[-1] == "stopped at 1 rebase-onto-default.sh exit %d" % inner


@pytest.mark.parametrize("inner", [1, 2])
def test_4031_a_regrade_block_whose_highest_exit_is_1_or_2_stops_it_after_the_block(prep, inner):
    code, out, err, fake = prep(answers={("detach-command.sh", ("wait", "regrade-12")): (1, "%d\n" % inner)})

    assert code == inner
    assert fake.calls[-1][:2] == ("detach-command.sh", ("wait", "regrade-12"))
    assert out.splitlines()[-1] == "stopped at 1 regrade block exit %d" % inner


def test_4390_a_regrade_block_that_died_with_no_code_stops_it_with_exit_2(prep):
    code, out, err, fake = prep(answers={("detach-command.sh", ("wait", "regrade-12")): (2, "")})

    assert (code, out.splitlines()[-1]) == (2, "stopped at 1 detach-command.sh wait regrade-12 exit 2")
    assert not {"rebased-tip-suite.sh", "push-branch.sh"} & set(fake.names())


@pytest.mark.parametrize("inner", [1, 2])
def test_4031_a_red_rebased_tip_stops_it_with_the_waits_code_before_any_resume_or_push(prep, inner):
    code, out, err, fake = prep(answers={("detach-command.sh", ("wait", "rebased-full-12")): (inner, "FAILED 2\n")})

    assert (code, out.splitlines()[-1]) == (inner, "stopped at 1 detach-command.sh wait rebased-full-12 exit %d" % inner)
    assert not {"suite-red-resume.sh", "push-branch.sh", "refactor-owed.sh"} & set(fake.names())


@pytest.mark.parametrize("before, after, pushed, clean", [
    ("", " M skills/tdd/GRADED\nM  GRADED\n", "", True),
    ("", "", " D skills/tdd/x.py\n", False),
    ("", " M skills/tdd/GRADED.bak\n", " M skills/tdd/GRADED.bak\n", False),
    (" D docs/GRADED\n", " D docs/GRADED\n", " D docs/GRADED\n", False),
    (" M docs/GRADED\n", " M docs/GRADED\n", " M docs/GRADED\n", False),
    ("", " D docs/GRADED\n", " D docs/GRADED\n", False),
    ("", "", " M docs/GRADED\n", False)],
    ids=["regraded files committed", "another path", "a GRADED lookalike", "a GRADED the rebase left deleted",
         "a GRADED modified before the regrade", "a GRADED the regrade deleted", "a GRADED changed after the regrade"])
def test_4031_immediately_before_the_push_a_path_beyond_the_files_the_regrade_modified_stops_it_with_exit_1(
        prep, before, after, pushed, clean):
    code, out, err, fake = prep(fake=Fake(porcelain=("", before, after, pushed)))

    if clean:
        assert code == 0 and "push-branch.sh" in fake.names()
        return
    assert (code, out.splitlines()[-1]) == (1, "stopped at 1 tree-check")
    assert "push-branch.sh" not in fake.names()


@pytest.mark.parametrize("failing", [("status", 1), ("status", 2), ("status", 3), ("status", 4), ("branch", 1)],
                         ids=["the first question", "before the regrade", "after the regrade", "before the push",
                              "the branch name"])
def test_4031_a_git_read_that_fails_is_exit_2_not_gits_own_code(prep, failing):
    class Failing(Fake):
        seen = 0

        def __call__(self, name, *args, **kw):
            if os.path.basename(name) == "git" and args[:1] == (failing[0],):
                self.seen += 1
                if self.seen == failing[1]:
                    self.calls.append(("git", args, kw.get("cwd"), kw.get("env"), kw))
                    return 128, "", "fatal: not a git repository\n"
            return super().__call__(name, *args, **kw)

    code, out, err, fake = prep(fake=Failing())

    assert code == 2 and "push-branch.sh" not in fake.names()
    assert out.splitlines()[-1].startswith("stopped at 1 git " + failing[0])


def test_4031_a_git_call_of_the_regrade_block_that_fails_is_exit_2_not_gits_own_code(prep):
    code, out, err, fake = prep(answers={("git", "merge-base"): (128, "")})

    assert code == 2 and "grade-prose.sh" not in fake.names()
    assert out.splitlines()[-1].startswith("stopped at 1 git merge-base")


@pytest.mark.parametrize("inner", [1, 2, 3])
def test_4429_a_signed_listing_that_fails_stops_it_with_exit_2_before_the_regrade_block_starts(prep, inner):
    code, out, err, fake = prep(answers={("grade-prose.sh", "--signed"): (inner, "")})

    assert code == 2 and "detach-command.sh" not in fake.names()
    assert out.splitlines()[-1].startswith("stopped at 1 grade-prose.sh --signed")


@pytest.mark.parametrize("script, first, inner", [("push-branch.sh", None, 1), ("push-branch.sh", None, 2),
                                                  ("rebased-tip-suite.sh", None, 2), ("refactor-owed.sh", None, 2),
                                                  ("event.sh", None, 2)])
def test_4031_a_push_suite_list_or_event_that_fails_stops_it_with_its_code(prep, script, first, inner):
    code, out, err, fake = prep(answers={(script, first): (inner, "")})

    assert code == inner and fake.names()[-1] == script


def test_4031_a_structural_candidate_stops_it_with_exit_1_for_structural_md(prep):
    code, out, err, fake = prep(answers={("refactor-owed.sh", None): (0, "src/a.py | split f\n")})

    assert (code, out.splitlines()[-1]) == (
        1, "stopped at 1 refactor-owed.sh list .tdd/issue-12-refactor-owed.md exit 0")
    assert "event.sh" not in fake.names()


def test_4031_it_runs_nothing_after_the_skip_event_and_handles_no_refusal_itself(prep):
    for answers in ({}, {("push-branch.sh", None): (1, "")}):
        code, out, err, fake = prep(answers=answers)
        assert not {"refactor-candidates.sh", "unwired.sh", "coupling.sh", "red-setup.sh", "test-quality.sh",
                    "lint-repair.sh", "suite-red-resume.sh", "classify-bail.sh", "preflight-refused.sh",
                    "add-ledger-step.sh", "detach-leaf.sh", "supervise.sh", "comment.sh"} & set(fake.names())
        assert not [c for c in fake.calls if c[0] == "git" and c[1][:1] in (("reset",), ("clean",), ("commit",))]
        assert [c[1][0] for c in fake.calls if c[0] == "event.sh"] in ([], ["structural-pass"])


READ = ("git", "rebase-onto-default.sh", "rebased-tip-suite.sh", "detect-test-command.sh")  # stdout read as a value


def test_4031_every_inner_call_prints_its_name_and_exit_then_its_stdout_and_its_stderr(prep):
    class Marked(Fake):
        def __call__(self, name, *args, **kw):
            code, out, err = super().__call__(name, *args, **kw)
            if os.path.basename(name) in READ:
                return code, out, err
            return code, "OUT<%d>\n" % len(self.calls) + out, "ERR<%d>\n" % len(self.calls)

    code, out, err, fake = prep(fake=Marked())

    lines = out.splitlines()
    assert code == 0
    for i, c in enumerate(fake.calls, 1):
        if c[0] in READ:
            assert any(line.startswith(c[0]) for line in lines)
            continue
        named = lines[lines.index("OUT<%d>" % i) - 1]
        assert named.startswith(c[0]) and "ERR<%d>" % i in err
    assert "PASSED 812" in lines


# Inner calls sub-step 1 does not name, each by name with its reason.
NAMED_ELSEWHERE = {
    "rebased-tip-suite.sh": "the step's opening paragraphs settle the mode with it; sub-step 1 reads it as "
                            "`VERI_REBASED_TIP_SUITE=local` or `ci`",
}


def test_4031_every_inner_call_in_the_ordered_list_is_a_script_draft_pr_sub_step_1_names():
    from pathlib import Path
    pr_prepare = importlib.import_module("veri.pr_prepare")
    draft = (Path(pr_prepare.__file__).resolve().parents[2] / "DRAFT-PR.md").read_text()
    sub_step = draft[draft.index("\n1. Run `$S/pr-prepare.sh"):draft.index("\n2. **Mark the PR ready")]

    assert [name for name in pr_prepare.CALLS if "$S/" + name not in sub_step and name not in NAMED_ELSEWHERE] == []
    assert all("$S/" + name in draft for name in NAMED_ELSEWHERE)


def test_4031_a_local_rebase_makes_the_calls_of_the_ordered_list_in_its_order(prep):
    pr_prepare = importlib.import_module("veri.pr_prepare")
    code, out, err, fake = prep()

    made = [name for name in fake.names() if name != "git"]
    assert code == 0 and set(made) == set(pr_prepare.CALLS)
    firsts = [made.index(name) for name in pr_prepare.CALLS]
    assert firsts == sorted(firsts)


def _pid(prep, text):
    (prep.wt / ".tdd" / "conductor.pid").write_text(text)


def test_4031_a_wait_whose_slice_ran_out_exits_3_on_a_waiting_on_line(prep):
    code, out, err, fake = prep(answers={("detach-command.sh", ("wait", "rebased-full-12")): (3, "")})

    assert (code, out.splitlines()[-1]) == (3, "waiting on rebased-full-12")
    assert "push-branch.sh" not in fake.names()


def test_4031_called_again_after_an_exit_3_it_only_waits_again_then_pushes_and_marks_once(prep):
    _pid(prep, "111\nTue Nov 17 07:00:00 2026\n")
    first = prep(answers={("detach-command.sh", ("wait", "rebased-full-12")): (3, "")})[0]
    code, out, err, fake = prep()

    assert (first, code) == (3, 0)
    assert fake.calls[0][:2] == ("detach-command.sh", ("wait", "rebased-full-12"))
    assert not {"rebase-onto-default.sh", "grade-prose.sh", "next-pending-refactor.sh"} & set(fake.names())
    assert [c[0] for c in fake.calls].count("push-branch.sh") == 1
    assert fake.call("push-branch.sh")[1] == ("--force-with-lease=tdd/12-x:" + PRE,)
    assert out.endswith("rebased=1\nrebased_from=%s\nrebased_tip_suite=local\n" % PRE)
    assert not (prep.wt / ".tdd" / "issue-12-pr-prepare-wait").exists()


def test_4390_a_git_commit_of_the_regrade_that_fails_is_exit_2_naming_it_not_gits_own_code(prep):
    code, out, err, fake = prep(fake=Fake(answers={("git", "commit"): (1, "")}, porcelain=("", "", " M GRADED\n")))

    assert code == 2 and "push-branch.sh" not in fake.names()
    assert out.splitlines()[-1].startswith("stopped at 1 git commit")


@pytest.mark.parametrize("after", ["?? skills/tdd/GRADED\n", "?? skills/tdd/GRADED\n M GRADED\n"],
                         ids=["only untracked", "beside a modified one"])
def test_4390_a_graded_file_the_block_left_untracked_is_not_committed(prep, after):
    code, out, err, fake = prep(fake=Fake(porcelain=("", "", after)))

    committed = [c[1] for c in fake.calls if c[0] == "git" and c[1][:1] == ("commit",)]
    assert all("skills/tdd/GRADED" not in args for args in committed)
    assert committed == ([] if after.count("\n") == 1 else [("commit", "-q", "-m", "docs: regrade the prose the branch signed (#12)", "--", "GRADED")])


def test_4031_the_wait_record_names_the_conductor_by_the_pid_and_start_time_its_pid_file_held(prep):
    _pid(prep, "111\nTue Nov 17 07:00:00 2026\n")
    prep(answers={("detach-command.sh", ("wait", "rebased-full-12")): (3, "")})

    record = json.loads((prep.wt / ".tdd" / "issue-12-pr-prepare-wait").read_text())
    assert (record["conductor"], record["at"]) == ({"pid": "111", "started": "Tue Nov 17 07:00:00 2026"},
                                                   "rebased-full-12")


@pytest.mark.parametrize("second", ["222\nTue Nov 17 07:00:00 2026\n", "111\nTue Nov 17 08:00:00 2026\n", None],
                         ids=["another pid", "another start time", "no pid file"])
def test_4031_called_under_another_conductor_it_discards_the_record_and_starts_from_its_first_call(prep, second):
    _pid(prep, "111\nTue Nov 17 07:00:00 2026\n")
    prep(answers={("detach-command.sh", ("wait", "rebased-full-12")): (3, "")})
    if second is None:
        (prep.wt / ".tdd" / "conductor.pid").unlink()
    else:
        _pid(prep, second)
    code, out, err, fake = prep()

    assert (code, fake.calls[0][1]) == (0, ("status", "--porcelain", "--untracked-files=all"))
    assert not (prep.wt / ".tdd" / "issue-12-pr-prepare-wait").exists()


class SlowRegrade(Fake):
    """A Fake whose wait on the detached regrade block answers <regrade_waits> in turn, then 0."""

    def __init__(self, regrade_waits=(), **kw):
        super().__init__(**kw)
        self.regrade_waits = list(regrade_waits)

    def __call__(self, name, *args, **kw):
        if os.path.basename(name) == "detach-command.sh" and args[:2] == ("wait", "regrade-12"):
            self.calls.append(("detach-command.sh", args, kw.get("cwd"), kw.get("env"), kw))
            code, out = self.regrade_waits.pop(0) if self.regrade_waits else (0, "")
            return code, out, ""
        return super().__call__(name, *args, **kw)


def test_4390_the_regrade_block_runs_detached_its_slice_running_out_is_exit_3_and_a_second_call_only_waits_again(
        prep):
    _pid(prep, "111\nTue Nov 17 07:00:00 2026\n")
    code, out, err, fake = prep(fake=SlowRegrade(regrade_waits=[(3, "")]))

    assert (code, out.splitlines()[-1]) == (3, "waiting on regrade-12")
    start = fake.call("detach-command.sh", "start")[1]
    assert start[:2] == ("start", "regrade-12")
    assert [c[1] for c in fake.calls if c[0] == "grade-prose.sh"] == [("--signed", BASE)]
    assert [a for a in start if a.endswith(("REQUIREMENTS.md", "SKILL.md#Two words", "README.md"))] == [
        "skills/tdd/REQUIREMENTS.md", "skills/tdd/SKILL.md#Two words", "REQUIREMENTS.md", "README.md"]
    assert json.loads((prep.wt / ".tdd" / "issue-12-pr-prepare-wait").read_text())["at"] == "regrade-12"
    assert not {"rebased-tip-suite.sh", "push-branch.sh", "event.sh"} & set(fake.names())

    code, out, err, fake = prep(fake=SlowRegrade())

    assert code == 0, out + err
    assert fake.calls[0][:2] == ("detach-command.sh", ("wait", "regrade-12"))
    assert not {"next-pending-refactor.sh", "rebase-onto-default.sh"} & set(fake.names())
    assert ("detach-command.sh", "start", "regrade-12") not in [(c[0],) + c[1][:2] for c in fake.calls]
    assert fake.names().count("push-branch.sh") == 1


SUBJECT = "docs: regrade the prose the branch signed (#12)"


@pytest.mark.parametrize("before, after, committed", [
    ("", " M skills/tdd/GRADED\nM  GRADED\n", ["skills/tdd/GRADED", "GRADED"]),
    (" M docs/GRADED\n", " M docs/GRADED\n M GRADED\n", ["GRADED"]),
    ("", "", None)],
    ids=["the files the block modified", "not a GRADED modified before the block", "none modified, no commit"])
def test_4390_with_no_rebase_it_commits_exactly_the_graded_files_the_regrade_block_modified_under_the_fixed_subject(
        prep, before, after, committed):
    code, out, err, fake = prep(fake=Fake(answers={("rebase-onto-default.sh", None): (3, "")},
                                          porcelain=("", before, after)))

    assert code == 0, out + err
    commits = [c[1] for c in fake.calls if c[0] == "git" and c[1][:1] == ("commit",)]
    assert commits == ([] if committed is None else [("commit", "-q", "-m", SUBJECT, "--", *committed)])


@pytest.mark.parametrize("mode", ["local", "ci"])
def test_4390_after_a_rebase_the_regrade_is_committed_before_the_pinned_lease_push_and_the_tree_it_pushes_is_clean(
        prep, mode):
    code, out, err, fake = prep(fake=Fake(porcelain=("", "", " M GRADED\n", ""), mode=mode))

    assert code == 0, out + err
    made = _calls(fake)
    commit = made.index(("git", ("commit", "-q", "-m", SUBJECT, "--", "GRADED")))
    assert commit < fake.names().index("push-branch.sh")


@pytest.mark.parametrize("answers", [{("rebase-onto-default.sh", None): (3, "")},
                                     {("detach-command.sh", ("wait", "regrade-12")): (1, "1\n")}],
                         ids=["no rebase, exit 0", "a regrade block that stopped it"])
def test_4390_once_the_regrade_wait_answered_no_record_is_left_so_the_next_call_starts_from_its_first_call(
        prep, answers):
    _pid(prep, "111\nTue Nov 17 07:00:00 2026\n")
    prep(answers=answers)

    assert not (prep.wt / ".tdd" / "issue-12-pr-prepare-wait").exists()


def test_4856_a_compound_full_command_on_the_rebased_tip_starts_through_sh_c_so_and_and_never_reaches_the_tool(prep):
    code, out, err, fake = prep(fake=Fake({("detect-test-command.sh", None): (0, "make lint && make test\n")}))

    starts = [c[1] for c in fake.calls if c[0] == "detach-command.sh" and c[1][:2] == ("start", "rebased-full-12")]
    assert starts == [("start", "rebased-full-12", "sh", "-c", "make lint && make test")]
