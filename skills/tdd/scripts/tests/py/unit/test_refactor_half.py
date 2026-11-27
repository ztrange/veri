"""In-process cases for veri/refactor_half.py, the module refactor-half.sh is a shim over (PRD 027.6, #4028)."""
import hashlib
import importlib
import json
import os

import pytest

STEP = "one thing works ⟦criterion 1⟧"
LEDGER = "# Plan for #12\n\n- [x] %s ⟂ refactor pending\n- [ ] two ⟦criterion 2⟧\n"
RED_HALF = ("step=%s\ntest_path=tests/test_a.py\ntarget_test=tests/test_a.py::test_one\n"
            "red_test_id=tests/test_a.py::test_one\nagainst_unmodified=FAILS\n")
GREEN_SHA = "d" * 40
GREEN_HALF = "step=%s\ngreen_sha=" + GREEN_SHA + "\ntest_path=tests/test_a.py\n"
TOUCHED = "src/a.py,tests/test_a.py"
# Records naming a test path of their own, so a case can tell which record was read (SC8).
HAND_RED_HALF = ("step=%s\ntest_path=checks/red_check.py\ntarget_test=checks/red_check.py::red_case\n"
                 "red_test_id=checks/red_check.py::red_case\nagainst_unmodified=FAILS\n")
HAND_GREEN_HALF = "step=%s\ngreen_sha=" + GREEN_SHA + "\ntest_path=checks/green_check.py\n"
REPORT = ("RESULT: extract f\nCANDIDATES: structural | src/a.py | split g\nCANDIDATES: cosmetic | src/a.py | rename h\n"
          "CANDIDATES: structural | src/a.py | inline k\nFLAGS: beyond-spec | negative sizes\n"
          "FLAGS: uncovered-spec | empty input returns 0\n")
# `git log -p --unified=0` over the ledger, one entry per commit: (sha, the patch's changed lines).
LEDGER_LOG = "".join("\0%s\n\ndiff --git a/.tdd/issue-12.md b/.tdd/issue-12.md\n--- a/.tdd/issue-12.md\n"
                     "+++ b/.tdd/issue-12.md\n@@ -3 +3 @@\n%s" % entry for entry in (
                         (GREEN_SHA, "-- [ ] %s\n+- [x] %s ⟂ refactor pending\n" % (STEP, STEP)),))
VERDICT = "FLAGS: overfit | the size is hard-coded\nFLAGS: uncovered-spec | a tab separates too\nVERDICT: PASS\n"


class Fake:
    """A run_script stand-in: records (basename, args, cwd, env, kw) and answers from <answers>, keyed by
    (basename, first argument or None) -> (code, stdout)."""

    def __init__(self, answers=None, report=REPORT, verdict=VERDICT, porcelain="", subjects="refactor: extract f (#12)\n",
                 count="1\n", ledger_log=LEDGER_LOG, last_ledger_commit=GREEN_SHA):
        self.answers, self.calls = dict(answers or {}), []
        self.ledger_log, self.last_ledger_commit = ledger_log, last_ledger_commit
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
            return 0, self.last_ledger_commit + "\n", ""
        if base == "git" and args[:2] == ("log", "--format=%x00%H"):
            return 0, self.ledger_log, ""
        if base == "git" and args[:1] == ("log",):
            return 0, self.subjects, ""
        if base == "git" and args[:1] == ("rev-list",):
            return 0, self.count, ""
        if base == "git" and args == ("status", "--porcelain", "--untracked-files=all"):
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


BRANCH_BASE = "abc1234"  # the run's recorded branch base (#4375)


@pytest.fixture
def tidy(monkeypatch, run_cli, tmp_path):
    """tidy(answers=None, fake=None, missing=(), step=STEP, red_step=None, argv=None) runs refactor-half for issue
    12 from the main tree, the run's worktree at .tdd/wt/12; returns (code, stdout, stderr, fake)."""
    fused = importlib.import_module("veri.fused")
    refactor_half = importlib.import_module("veri.refactor_half")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)

    def go(answers=None, fake=None, missing=(), step=STEP, red_step=None, argv=None):
        files = {"branch_base": (wt / ".tdd" / "issue-12-branch-base", BRANCH_BASE + "\n"),
                 "preflight": (wt / ".tdd" / "issue-12-preflight", "worktree=%s\nfast_cmd=make unit\n" % wt),
                 "ledger": (wt / ".tdd" / "issue-12.md", LEDGER % step),
                 "spec": (wt / ".tdd" / "issue-12-spec.md", "# spec\n"),
                 "red-half": (wt / ".tdd" / "issue-12-red-half", RED_HALF % (red_step or step)),
                 "green-half": (wt / ".tdd" / "issue-12-green-half", GREEN_HALF % (red_step or step)),
                 "out": (wt / ".tdd" / "develop-refactor.out", "{\"report\": 1}\n"),
                 "log": (wt / ".tdd" / "verify-refactor.log", VERDICT)}
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
                                            ("spec", ".tdd/issue-12-spec.md")])
def test_4028_a_missing_input_is_exit_2_before_any_inner_call_named_on_stderr(tidy, missing, named):
    code, out, err, fake = tidy(missing=(missing,))

    assert (code, fake.calls) == (2, [])
    assert named in err


@pytest.mark.parametrize("given", [{"missing": ("green-half", "red-half")}, {"red_step": "zero ⟦criterion 1⟧"}])
def test_no_green_half_or_red_half_record_for_the_step_is_exit_1_on_the_seam_line_before_any_call_4342(tidy, given):
    """SC4, replacing #4028's exit 2: neither green-half's record nor, failing it, red-half's names the step, a
    designed hand-off (S1); the seam line names green-half's contract."""
    code, out, err, fake = tidy(**given)

    assert (code, fake.calls) == (1, [])
    assert out.splitlines()[-1] == "seam=refactor-half code=1 reason=record next=seam-settle.sh 12 green-half test_path=…"


def test_it_runs_after_a_plan_rewrite_that_changed_only_the_open_steps_marks_4310_4342(tidy):
    """SC8, #4310: a `plan: rewrite` changed only the open step's marks after its record was written."""
    code, out, err, fake = tidy(answers={("wait-leaf.sh", "develop-refactor"): (3, "")},
                                red_step="one thing works ⟦added⟧ ⟦criterion 1⟧")

    assert (code, fake.launched()) == (3, ["develop-refactor"])


def test_4028_no_refactor_pending_step_is_exit_2_before_any_inner_call(tidy):
    (tidy.wt / ".tdd" / "issue-12.md").write_text("# Plan\n\n- [x] %s\n- [ ] two ⟦criterion 2⟧\n" % STEP)
    code, out, err, fake = tidy()

    assert (code, fake.calls) == (2, [])


def _short(args):
    return tuple(os.path.basename(a) if a.endswith(".sh") else a for a in args)


def _after(fake, name, first=None):
    at = fake.calls.index(fake.call(name, first))
    return fake.calls[at + 1:]


def test_4028_it_opens_the_refactor_loop_stage_asks_the_budget_and_launches_develop_refactor(tidy):
    code, out, err, fake = tidy(answers={("wait-leaf.sh", "verdict-refactor"): (3, "")})

    assert [(c[0], c[1][:1]) for c in fake.calls[:10]] == [
        ("event.sh", ("stage-start",)), ("git", ("log",)), ("git", ("log",)), ("refactor-budget.sh", ("0",)),
        ("refactor-touched.sh", (GREEN_SHA,)), ("near-duplicates.sh", (GREEN_SHA,)),
        ("build-develop-prompt.sh", ("refactor",)), ("stop-requested.sh", ()),
        ("detach-leaf.sh", (fake.calls[8][1][0],)), ("wait-leaf.sh", ("develop-refactor",))]
    assert fake.calls[0][1] == ("stage-start", "stage=refactor-loop")
    assert (tidy.wt / ".tdd" / "stage-rl.t").read_text().strip().isdigit()
    assert fake.calls[1][1] == ("log", "-1", "--format=%H", "--", ".tdd/issue-12.md")
    assert fake.calls[2][1] == ("log", "--format=%x00%H", "-p", "--unified=0", "HEAD", "--", ".tdd/issue-12.md")
    assert fake.calls[6][1][:5] == ("refactor", ".tdd/issue-12-spec.md", STEP, "make unit", TOUCHED)
    assert fake.calls[6][4]["out"] == ".tdd/develop-refactor.prompt"
    launch = fake.calls[8]
    assert _short(launch[1]) == ("supervise.sh", "develop-refactor", "run-leaf.sh", ".tdd/develop-refactor.prompt",
                                 "--permission-mode", "bypassPermissions")
    assert (launch[3]["VERI_TEST_CMD"], launch[3]["VERI_ISSUE"], launch[3]["VERI_STEP"]) == ("make unit", "12", STEP)
    assert (launch[4]["out"], launch[4]["err"]) == (".tdd/develop-refactor.out", ".tdd/develop-refactor.err")



PAIR = "src/a.py:10-14 src/b.py:3-7\n"


class Redirecting(Fake):
    """A Fake whose call given <out> writes its stdout to that file under <cwd>, as run_script does."""

    def __call__(self, name, *args, cwd=None, env=None, **kw):
        code, out, err = super().__call__(name, *args, cwd=cwd, env=env, **kw)
        if kw.get("out") is not None:
            with open(os.path.join(cwd, kw["out"]), "w") as f:
                f.write(out)
            out = ""
        return code, out, err


def test_4577_the_near_duplicate_pair_of_the_steps_own_green_tick_reaches_the_refactor_prompts_pairs_file(tidy):
    """Criterion 2: near-duplicates.sh runs on the step's own green tick, the commit refactor-touched.sh is handed, and
    what it printed is the pairs file build-develop-prompt.sh fills the prompt's near-duplicates section from."""
    code, out, err, fake = tidy(fake=Redirecting({("near-duplicates.sh", None): (0, PAIR),
                                                  ("wait-leaf.sh", "develop-refactor"): (3, "")}))

    assert fake.call("near-duplicates.sh")[1] == (GREEN_SHA,), err
    build = fake.call("build-develop-prompt.sh", "refactor")
    assert len(build[1]) == 6
    assert (tidy.wt / build[1][5]).read_text() == PAIR


def test_4577_near_duplicates_exit_3_still_launches_the_refactor_leaf_its_pairs_file_empty(tidy):
    """Criterion 3: no pair (exit 3) is not a stop; the leaf launches on a prompt built from an empty pairs file,
    which build-develop-prompt.sh renders as the near-duplicates section reading `none`."""
    code, out, err, fake = tidy(fake=Redirecting({("near-duplicates.sh", None): (3, ""),
                                                  ("wait-leaf.sh", "develop-refactor"): (3, "")}))

    assert fake.launched() == ["develop-refactor"], out
    build = fake.call("build-develop-prompt.sh", "refactor")
    assert (tidy.wt / build[1][5]).read_text() == ""


def test_4577_near_duplicates_exit_2_stops_refactor_half_with_exit_2_before_any_leaf_is_launched(tidy):
    """Criterion 3: near-duplicates.sh obtaining no answer (exit 2) is not "no pair"; the leaf is never launched on a
    pairs file nobody vouches for, and refactor-half.sh says so with exit 2."""
    code, out, err, fake = tidy(fake=Redirecting({("near-duplicates.sh", None): (2, "")}))

    assert (code, fake.launched()) == (2, []), out
    assert "build-develop-prompt.sh" not in fake.names()


def test_4028_a_spent_budget_launches_no_refactor_leaf(tidy):
    code, out, err, fake = tidy(fake=Fake({("refactor-budget.sh", None): (3, "refactor 0/0 — budget spent\n")},
                                          count="0\n", subjects=""))

    assert (code, fake.launched()) == (0, [])
    assert "stopped=budget" in fake.call("event.sh", "refactor")[1]
    assert fake.call("refactor-owed.sh")[4]["stdin"] == ""


def test_4028_a_refactor_budget_exit_2_stops_it(tidy):
    code, out, err, fake = tidy(answers={("refactor-budget.sh", None): (2, "")})

    assert (code, fake.names()[-1], out.splitlines()[-1]) == (2, "refactor-budget.sh",
                                                              "stopped at 1 refactor-budget.sh 0 exit 2")


@pytest.mark.parametrize("leaf", [1, 2])
def test_4028_a_develop_refactor_wait_exit_1_or_2_stops_it(tidy, leaf):
    code, out, err, fake = tidy(answers={("wait-leaf.sh", "develop-refactor"): (leaf, "")})

    assert (code, out.splitlines()[-1]) == (leaf, "stopped at 1 wait-leaf.sh develop-refactor exit %d" % leaf)


def test_4028_after_the_leaf_it_asks_git_for_the_tree_the_subjects_and_the_count(tidy):
    code, out, err, fake = tidy()

    tail = [(c[0], c[1]) for c in _after(fake, "wait-leaf.sh", "develop-refactor")[:3]]
    assert tail == [("git", ("status", "--porcelain", "--untracked-files=all")), ("git", ("log", "--format=%s", GREEN_SHA + "..HEAD")),
                    ("git", ("rev-list", "--count", GREEN_SHA + "..HEAD"))]


@pytest.mark.parametrize("fake_args", [{"porcelain": " M src/a.py\n"}, {"subjects": "refactor: a (#12)\nfeat: b\n"}],
                         ids=["dirty tree", "off-route subject"])
def test_4028_a_dirty_tree_or_an_off_route_subject_stops_it_with_exit_1_resetting_nothing(tidy, fake_args):
    code, out, err, fake = tidy(fake=Fake(**fake_args))

    assert (code, out.splitlines()[-1].split(" ")[:3] == ["stopped", "at", "2"]) == (1, True)
    assert not [c for c in fake.calls if c[0] == "git" and c[1][:1] in (("reset",), ("clean",))]
    assert "comment.sh" not in fake.names()


@pytest.mark.parametrize("line, where", [("FLAGS: overfit | hard-coded 3", "3"),
                                         ("CANDIDATES: in-step | src/b.py | move f", "6")])
def test_4028_an_overfit_flag_or_an_in_step_candidate_stops_it_with_exit_1(tidy, line, where):
    code, out, err, fake = tidy(fake=Fake(report=REPORT + line + "\n"))

    assert (code, out.splitlines()[-1]) == (1, "stopped at %s %s" % (where, line))
    assert "verdict-refactor" not in fake.launched()


CRITERIA = "# spec\n\n## Acceptance criteria\n\n- [ ] one thing works\n- [ ] a stage exiting 1 stops the run\n"
LATER = "two ⟦criterion 2⟧"
WHAT = "src/a.py ignores exit codes"


def _flagged(tidy, case, ledger=None, step=STEP, criteria=CRITERIA):
    (tidy.wt / ".tdd" / "issue-12-spec.md").write_text(criteria)
    if ledger is not None:
        (tidy.wt / ".tdd" / "issue-12.md").write_text(ledger)
    line = "FLAGS: overfit | %s | %s" % (WHAT, case)
    code, out, err, fake = tidy(fake=Fake(report=REPORT + line + "\n"), step=step)
    return code, out, line


@pytest.mark.parametrize("case, ledger", [
    ("one thing works", None),
    ("an empty list sums to 0", None),
    ("a stage exiting 1 stops the run", "# Plan for #12\n\n- [x] %s ⟂ refactor pending\n- [x] %s\n" % (STEP, LATER)),
    ("a stage exiting 1 stops the run", "# Plan for #12\n\n- [ ] %s\n- [x] %s ⟂ refactor pending\n" % (LATER, STEP)),
    ("", None),
    ("   ", None)],
    ids=["this step's own criterion", "no step's criterion", "a later step already checked",
         "an earlier unchecked step", "an empty case", "a whitespace-only case"])
def test_4438_an_overfit_flag_no_later_unchecked_step_owns_still_stops_at_3(tidy, case, ledger):
    code, out, line = _flagged(tidy, case, ledger)

    assert (code, out.splitlines()[-1]) == (1, "stopped at 3 " + line.rstrip())


def test_4438_an_overfit_flag_whose_case_a_later_unchecked_step_owns_is_narrated_as_owed_and_does_not_stop_it(tidy):
    code, out, line = _flagged(tidy, "a stage exiting 1 stops the run")

    assert code == 0
    note = (tidy.wt / ".tdd" / "refactor-half-note.md").read_text()
    assert "- overfit | %s | a stage exiting 1 stops the run (owed by %s)\n" % (WHAT, LATER) in note


# Run #4432's step 3, its later steps and its spec, as its ledger and spec held them, cut to the criteria they name.
RUN_STEP = ("run-pr.sh <n> runs branch-gate.sh, pr-prepare.sh and pr-checks.sh in that order, each through "
            "fused.script(), and after pr-checks.sh exits 0 prints seam=pr-ready-wait code=1 reason=title and exits 1 "
            "⟦criterion 1⟧")
RUN_OWNER = ("at the first stage exiting 1 or 2 it stops, prints seam=<stage> code=<c> next=DRAFT-PR.md#4. Draft PR "
             "after that stage's own output (its stopped at line), calls no later stage and exits c ⟦criterion 3⟧")
RUN_LEDGER = ("# Plan for #12\n\n- [x] %s ⟂ refactor pending\n"
              "- [ ] called again after the body seam it calls no stage and exits 0 ⟦criterion 2⟧\n- [ ] %s\n"
              % (RUN_STEP, RUN_OWNER))
RUN_SPEC = ("# spec\n\n## Acceptance criteria\n\n"
            "- [x] RPR1: `run-pr.sh <n>` runs `branch-gate.sh`, `pr-prepare.sh` and `pr-checks.sh` in that order.\n"
            "- [ ] RPR2: called again after the `title` seam, it runs `pr-ready-wait.sh`, then `pr-finish.sh`.\n"
            "- [ ] RPR3: at the first stage that exits non-zero it stops, prints `seam=<stage> code=<c> next=<anchor or "
            "run-pr.sh <n>>` after that stage's own `stopped at` line, and exits with `c`.\n")
RUN_CASE = "a case where a stage exits non-zero and the run must stop with `seam=<stage> code=<c>` (RPR3)"


@pytest.mark.parametrize("case", [RUN_CASE, "a stage exits non-zero and stops (criterion 3)",
                                  "a stage exits non-zero and stops ⟦criterion 3⟧"],
                         ids=["a requirement id", "criterion k", "the criterion mark"])
def test_4438_an_overfit_flag_naming_a_later_unchecked_steps_identifier_is_owed_by_it_as_in_run_4432(tidy, case):
    code, out, line = _flagged(tidy, case, RUN_LEDGER, step=RUN_STEP, criteria=RUN_SPEC)

    assert code == 0
    note = (tidy.wt / ".tdd" / "refactor-half-note.md").read_text()
    assert "- overfit | %s | %s (owed by %s)\n" % (WHAT, case, RUN_OWNER) in note


def test_4438_an_identifier_no_later_unchecked_step_carries_still_stops_at_3(tidy):
    code, out, line = _flagged(tidy, "a stage exits non-zero and stops (RPR30, criterion 7)", RUN_LEDGER,
                               step=RUN_STEP, criteria=RUN_SPEC)

    assert (code, out.splitlines()[-1]) == (1, "stopped at 3 " + line)


ID_LEDGER = "# Plan for #12\n\n- [x] %s ⟂ refactor pending\n- [ ] %s\n"
ID_SPEC = "# spec\n\n## Acceptance criteria\n\n- [ ] %s: one thing works\n- [ ] %s: a stage exiting 1 stops the run\n"


@pytest.mark.parametrize("case, later, own, ledger_later", [
    ("a stage exits non-zero and stops (RPR1)", "RPR10", "RPR0", LATER),
    ("RPR1", "RPR10", "RPR0", LATER),
    ("a stage exits non-zero and stops (RPR1)", "RPR2", "RPR1", "two, as RPR1 requires ⟦criterion 2⟧")],
    ids=["an id a later step carries only as a prefix", "a case that is only an id token",
         "an id the current step carries, a later step citing it too"])
def test_4438_an_id_that_names_no_later_step_whole_or_names_the_current_step_still_stops_at_3(
        tidy, case, later, own, ledger_later):
    code, out, line = _flagged(tidy, case, ID_LEDGER % (STEP, ledger_later), criteria=ID_SPEC % (own, later))

    assert (code, out.splitlines()[-1]) == (1, "stopped at 3 " + line)


def test_4438_an_id_only_a_later_unchecked_steps_ledger_text_carries_defers_to_it(tidy):
    later = "two, as RPR7 requires ⟦criterion 2⟧"
    code, out, line = _flagged(tidy, "a stage exits non-zero and stops (RPR7)", ID_LEDGER % (STEP, later),
                               criteria=ID_SPEC % ("RPR0", "RPR2"))

    assert code == 0
    note = (tidy.wt / ".tdd" / "refactor-half-note.md").read_text()
    assert "(owed by %s)\n" % later in note


def test_4438_an_id_only_the_current_steps_ledger_text_carries_still_stops_at_3(tidy):
    step = "one thing works, as RPR7 requires ⟦criterion 1⟧"
    code, out, line = _flagged(tidy, "a stage exits non-zero and stops (RPR7)", ID_LEDGER % (step, LATER), step=step,
                               criteria=ID_SPEC % ("RPR0", "RPR7"))

    assert (code, out.splitlines()[-1]) == (1, "stopped at 3 " + line)


@pytest.mark.parametrize("budget, count, result, triage, stopped", [
    ("refactor 0/1", "1\n", "RESULT: extract f\n", 0, "budget"),
    ("refactor 0/5", "1\n", "RESULT: nothing left to tidy\n", 0, "nothing-left"),
    ("refactor 0/5", "1\n", "RESULT: extract f\n", 0, "structural-owed"),
    ("refactor 0/5", "1\n", "RESULT: extract f\n", 3, "nothing-structural"),
    ("refactor 0/5", "1\n", "RESULT: extract f\n", 2, "malformed")])
def test_4028_why_the_tidying_stopped_follows_the_precedence_and_never_stops_on_triage(
        tidy, budget, count, result, triage, stopped):
    report = result + "".join(line + "\n" for line in REPORT.splitlines() if not line.startswith("RESULT:"))
    code, out, err, fake = tidy(fake=Fake({("refactor-budget.sh", None): (0, budget + " — another\n"),
                                           ("refactor-triage.sh", None): (triage, "")}, report=report, count=count))

    assert code == 0
    assert fake.call("event.sh", "refactor")[1] == ("refactor", "transforms=1", "budget=%s" % budget[-1],
                                                    "stopped=" + stopped, "pass=1")


def test_4028_nothing_landed_marks_the_skip_posts_the_skipped_comment_and_launches_no_verifier(tidy):
    code, out, err, fake = tidy(fake=Fake(count="0\n", subjects=""))

    assert (code, fake.launched()) == (0, ["develop-refactor"])
    mark = fake.call("event.sh", "verify-refactor-skipped")
    assert mark[1] == ("verify-refactor-skipped", "reason=nothing-landed")
    assert (mark[3]["VERI_ACTOR"], mark[3]["VERI_STEP"]) == ("conductor", STEP)
    comments = [c[1][1:] for c in fake.calls if c[0] == "comment.sh"]
    assert comments == [("verify-refactor", "--skipped"), ("refactor", "--note-file", ".tdd/refactor-half-note.md")]


def test_a_nothing_landed_refactor_replaces_an_earlier_steps_verdict_with_skipped_4555(tidy):
    (tidy.wt / ".tdd" / "verdict-refactor.exit").write_text("0\n")
    tidy(fake=Fake(count="0\n", subjects=""))

    assert (tidy.wt / ".tdd" / "verdict-refactor.exit").read_text().strip() == "skipped"


def test_4028_with_refactor_switched_off_it_marks_the_skip_writes_skipped_and_posts_verify_refactor_once(tidy):
    (tidy.wt / ".tdd" / "issue-12-skip-verify").write_text("refactor\n")
    code, out, err, fake = tidy()

    assert (code, fake.launched()) == (0, ["develop-refactor"])
    assert fake.call("event.sh", "verify-refactor-skipped")[1] == ("verify-refactor-skipped", "reason=switched-off")
    assert (tidy.wt / ".tdd" / "verdict-refactor.exit").read_text().strip() == "skipped"
    comments = [c[1][1:] for c in fake.calls if c[0] == "comment.sh"]
    assert comments == [("verify-refactor",), ("refactor", "--note-file", ".tdd/refactor-half-note.md")]


@pytest.mark.parametrize("given", [{"fake_kw": {"count": "0\n", "subjects": ""}}, {"switched_off": True}],
                         ids=["nothing landed", "switched off"])
def test_a_skipped_verify_records_the_leftover_logs_hash_but_none_of_its_uncovered_spec_flags_4342(tidy, given):
    """#4029's flags come with the hash from one read of the log, but a skipped verify's log is an earlier step's:
    its `uncovered-spec` flags are not this step's, so only the leaf's are recorded."""
    if given.get("switched_off"):
        (tidy.wt / ".tdd" / "issue-12-skip-verify").write_text("refactor\n")
    code, out, err, fake = tidy(fake=Fake(**given.get("fake_kw", {})))

    record = (tidy.wt / ".tdd" / "issue-12-refactor-half").read_text().splitlines()
    assert (code, fake.launched()) == (0, ["develop-refactor"])
    assert "verdict_log=" + hashlib.sha256(VERDICT.encode()).hexdigest() in record
    assert [line for line in record if line.startswith("uncovered_spec=")] == ["uncovered_spec=empty input returns 0"]


def test_4028_otherwise_it_launches_verdict_refactor_with_refactor_5s_arguments(tidy):
    code, out, err, fake = tidy()

    launch = [c for c in fake.calls if c[0] == "detach-leaf.sh"][1]
    assert _short(launch[1]) == ("supervise.sh", "verdict-refactor", "run-verdict.sh", "--step", STEP, "--fast-cmd",
                                 "make unit", "--branch-base", BRANCH_BASE, "--step-green", GREEN_SHA, "refactor",
                                 ".tdd/issue-12-spec.md",
                                 "tests/test_a.py", GREEN_SHA)
    assert (launch[3]["VERI_TEST_CMD"], launch[3]["VERI_STEP"]) == ("make unit", STEP)
    assert (launch[4]["out"], launch[4]["err"]) == (".tdd/verify-refactor.reason", ".tdd/verify-refactor.err")


@pytest.mark.parametrize("verdict", [1, 2])
def test_4028_a_verdict_of_1_or_2_stops_it_before_any_comment(tidy, verdict):
    code, out, err, fake = tidy(answers={("wait-leaf.sh", "verdict-refactor"): (verdict, "")})

    assert (code, out.splitlines()[-1]) == (verdict, "stopped at 5 wait-leaf.sh verdict-refactor exit %d" % verdict)
    assert not {"comment.sh", "event.sh"} & set(fake.names()[1:])


def test_4028_a_tree_dirtied_before_the_first_comment_stops_it_with_exit_1(tidy):
    class Dirtied(Fake):
        def __call__(self, name, *args, **kw):
            if args == ("status", "--porcelain", "--untracked-files=all") and "wait-leaf.sh" in [c[0] for c in self.calls if
                                                                      c[1] == ("verdict-refactor",)]:
                self.calls.append(("git", args, kw.get("cwd"), kw.get("env"), kw))
                return 0, " M src/a.py\n", ""
            return super().__call__(name, *args, **kw)

    code, out, err, fake = tidy(fake=Dirtied())

    assert (code, out.splitlines()[-1], "comment.sh" in fake.names()) == (1, "stopped at 6 tree-check", False)


def test_4028_on_a_pass_it_posts_the_noted_refactor_and_verify_refactor_marks_the_log_records_and_settles(tidy):
    code, out, err, fake = tidy()

    tail = [(c[0], c[1]) for c in _after(fake, "wait-leaf.sh", "verdict-refactor")]
    assert tail[-5:] == [
        ("git", ("status", "--porcelain", "--untracked-files=all")),
        ("comment.sh", ("12", "refactor", "--note-file", ".tdd/refactor-half-note.md")),
        ("comment.sh", ("12", "verify-refactor")),
        ("event.sh", ("refactor", "transforms=1", "budget=5", "stopped=nothing-structural", "pass=1")),
        ("refactor-owed.sh", ("append", ".tdd/issue-12-refactor-owed.md", STEP, TOUCHED))]
    mark = fake.call("event.sh", "refactor")
    assert (mark[3]["VERI_PHASE"], mark[3]["VERI_ACTOR"], mark[3]["VERI_STEP"]) == ("refactor", "conductor", STEP)
    assert fake.call("refactor-owed.sh")[4]["stdin"] == "{\"report\": 1}\n"
    note = (tidy.wt / ".tdd" / "refactor-half-note.md").read_text()
    for part in ("refactor 1/5", "nothing-structural", "Structural (2)", "- split g", "- inline k", "Cosmetic (1)",
                 "- rename h", "beyond-spec | negative sizes", "overfit | the size is hard-coded"):
        assert part in note
    assert "overrun" not in note
    expected = ["step=" + STEP, "green_sha=" + GREEN_SHA, "count=1", "budget=5", "stopped=nothing-structural",
                "touched=" + TOUCHED, "verdict_log=" + hashlib.sha256(VERDICT.encode()).hexdigest(),
                "uncovered_spec=empty input returns 0", "uncovered_spec=a tab separates too"]
    assert (tidy.wt / ".tdd" / "issue-12-refactor-half").read_text().splitlines() == expected
    assert out.splitlines()[-len(expected):] == expected


def test_4028_a_count_over_the_budget_is_narrated_as_an_overrun_never_clamped(tidy):
    code, out, err, fake = tidy(fake=Fake({("refactor-budget.sh", None): (0, "refactor 0/2 — another\n")}, count="7\n",
                                          subjects="refactor: a\n" * 7))

    assert "refactor 7/2 — overrun" in (tidy.wt / ".tdd" / "refactor-half-note.md").read_text()
    assert "count=7" in out.splitlines()


def test_4028_it_commits_nothing_and_leaves_the_pending_mark(tidy):
    code, out, err, fake = tidy()

    assert code == 0
    assert not [c for c in fake.calls if c[0] == "git" and c[1][:1] in (("commit",), ("add",), ("push",))]
    assert not {"clear-refactor-pending.sh", "push-branch.sh", "tick-ledger.sh"} & set(fake.names())
    assert "⟂ refactor pending" in (tidy.wt / ".tdd" / "issue-12.md").read_text()


def test_4028_it_launches_no_leaf_but_through_supervise_and_no_cover_leaf(tidy):
    code, out, err, fake = tidy()

    assert not {"run-leaf.sh", "run-verdict.sh", "claude", "supervise.sh"} & set(fake.names())
    assert fake.launched() == ["develop-refactor", "verdict-refactor"]


@pytest.mark.parametrize("code, mode, launches", [(3, "", True), (0, "at-ledger\n", True), (0, "at-leaf\n", False),
                                                  (0, "now\n", False), (2, "", False)])
def test_4028_the_stop_check_before_develop_refactor(tidy, code, mode, launches):
    got, out, err, fake = tidy(answers={("stop-requested.sh", None): (code, mode)})

    assert ("develop-refactor" in fake.launched()) == launches
    if not launches:
        assert (got, out.splitlines()[-1].startswith("stopped at 1 stop-requested.sh")) == (2 if code == 2 else 1, True)


def _pid(tidy, text):
    (tidy.wt / ".tdd" / "conductor.pid").write_text(text)


@pytest.mark.parametrize("leaf", ["develop-refactor", "verdict-refactor"])
def test_4028_a_wait_whose_slice_ran_out_exits_3_on_a_waiting_on_line(tidy, leaf):
    code, out, err, fake = tidy(answers={("wait-leaf.sh", leaf): (3, "")})

    assert (code, out.splitlines()[-1]) == (3, "waiting on " + leaf)


@pytest.mark.parametrize("leaf, launched", [("develop-refactor", ["verdict-refactor"]), ("verdict-refactor", [])])
def test_4028_called_again_after_an_exit_3_it_only_waits_again_then_goes_on_once(tidy, leaf, launched):
    _pid(tidy, "111\nTue Nov 17 07:00:00 2026\n")
    first = tidy(answers={("wait-leaf.sh", leaf): (3, "")})[0]
    code, out, err, fake = tidy()

    assert (first, code) == (3, 0)
    assert fake.calls[0][:2] == ("wait-leaf.sh", (leaf,))
    assert fake.launched() == launched
    assert [c[1][0] for c in fake.calls if c[0] == "event.sh"] == ["refactor"]
    assert [c[1][1] for c in fake.calls if c[0] == "comment.sh"] == ["refactor", "verify-refactor"]
    assert "count=1" in out.splitlines() and "green_sha=" + GREEN_SHA in out.splitlines()
    assert not (tidy.wt / ".tdd" / "issue-12-refactor-half-wait").exists()


def test_4028_the_wait_record_names_the_conductor_by_the_pid_and_start_time_its_pid_file_held(tidy):
    _pid(tidy, "111\nTue Nov 17 07:00:00 2026\n")
    tidy(answers={("wait-leaf.sh", "develop-refactor"): (3, "")})

    record = json.loads((tidy.wt / ".tdd" / "issue-12-refactor-half-wait").read_text())
    assert (record["conductor"], record["at"]) == ({"pid": "111", "started": "Tue Nov 17 07:00:00 2026"},
                                                   "develop-refactor")


@pytest.mark.parametrize("second", ["222\nTue Nov 17 07:00:00 2026\n", "111\nTue Nov 17 08:00:00 2026\n", None],
                         ids=["another pid", "another start time", "no pid file"])
def test_4028_called_under_another_conductor_it_discards_the_record_and_starts_from_its_first_call(tidy, second):
    _pid(tidy, "111\nTue Nov 17 07:00:00 2026\n")
    tidy(answers={("wait-leaf.sh", "verdict-refactor"): (3, "")})
    if second is None:
        (tidy.wt / ".tdd" / "conductor.pid").unlink()
    else:
        _pid(tidy, second)
    code, out, err, fake = tidy()

    assert (code, fake.calls[0][1]) == (0, ("stage-start", "stage=refactor-loop"))


READ = ("extract-result.sh", "refactor-budget.sh", "refactor-touched.sh", "git")  # stdout read as a value


def test_4028_every_inner_call_prints_its_name_and_exit_then_its_stdout_and_its_stderr(tidy):
    class Marked(Fake):
        def __call__(self, name, *args, **kw):
            code, out, err = super().__call__(name, *args, **kw)
            if os.path.basename(name) in READ:
                return code, out, err
            return code, "OUT<%d>\n" % len(self.calls) + out, "ERR<%d>\n" % len(self.calls)

    code, out, err, fake = tidy(fake=Marked())

    lines = out.splitlines()
    assert code == 0
    for i, c in enumerate(fake.calls, 1):
        if c[0] in READ:
            continue
        assert "OUT<%d>" % i in lines and "ERR<%d>" % i in err
        named = lines[lines.index("OUT<%d>" % i) - 1]
        assert named.startswith(c[0]) and named.endswith(" exit %d" % (
            3 if c[0] in ("stop-requested.sh", "refactor-triage.sh") else 0))
    assert "CANDIDATES:" not in out and "VERDICT:" not in out


# Inner calls the Refactor loop section does not name, each by name with its reason.
NAMED_ELSEWHERE = {
    "extract-result.sh": "FC2: *Launching a leaf* reads a leaf's report only through it",
}


def test_4028_every_inner_call_in_the_ordered_list_is_a_script_the_refactor_loop_section_names():
    from pathlib import Path
    refactor_half = importlib.import_module("veri.refactor_half")
    skill = (Path(refactor_half.__file__).resolve().parents[2] / "SKILL.md").read_text()
    section = skill[skill.index("#### Refactor loop — one leaf"):skill.index("#### A `⟦diff-checked⟧` step")]

    assert [name for name in refactor_half.CALLS if "$S/" + name not in section and name not in NAMED_ELSEWHERE] == []


def test_4028_a_clean_run_makes_the_calls_of_the_ordered_list_in_its_order(tidy):
    refactor_half = importlib.import_module("veri.refactor_half")
    code, out, err, fake = tidy()

    made = [c[0] for c in fake.calls if c[0] != "git"]
    made += [os.path.basename(a) for c in fake.calls if c[0] == "detach-leaf.sh" for a in c[1] if a.endswith(".sh")]
    assert code == 0
    assert set(made) == set(refactor_half.CALLS)
    firsts = [made.index(name) for name in refactor_half.CALLS if name not in (
        "supervise.sh", "run-leaf.sh", "run-verdict.sh")]
    assert firsts == sorted(firsts)


def test_it_takes_green_sha_from_git_and_rewrites_a_stale_one_in_green_halfs_record_4342(tidy):
    """SC1: green_sha comes from git, the last commit that changed the ledger; the record's stale one is rewritten."""
    record = tidy.wt / ".tdd" / "issue-12-green-half"
    record.write_text("step=%s\ngreen_sha=%s\ntest_path=tests/test_a.py\n" % (STEP, "e" * 40))
    code, out, err, fake = tidy(answers={("wait-leaf.sh", "develop-refactor"): (3, "")})

    assert code == 3
    assert record.read_text() == GREEN_HALF % STEP
    events = [json.loads(line) for line in (tidy.wt / ".tdd" / "events.jsonl").read_text().splitlines()]
    assert [(e["stage"], e["key"], e["old"], e["new"]) for e in events if e["event"] == "record-refreshed"] == [
        ("refactor-half", "green_sha", "e" * 40, GREEN_SHA)]


@pytest.mark.parametrize("green", [None, "zero ⟦criterion 1⟧"], ids=["no green-half record", "one for another step"])
def test_a_green_not_finished_by_green_half_falls_back_to_red_halfs_record_4342(tidy, green):
    """SC8: a Green green-half.sh did not finish (a revise-green loop, a ⟦replaces-case⟧ or ⟦ci-repair⟧ step, a stop
    at Green 3) leaves no green-half record for the step, so refactor-half reads red-half's, as before PRD 038.1."""
    (tidy.wt / ".tdd" / "issue-12-red-half").write_text(HAND_RED_HALF % STEP)
    if green is not None:
        (tidy.wt / ".tdd" / "issue-12-green-half").write_text(GREEN_HALF % green)
    code, out, err, fake = tidy(missing=("green-half",))

    launch = [c for c in fake.calls if c[0] == "detach-leaf.sh"][1]
    assert (code, _short(launch[1])[-2:]) == (0, ("checks/red_check.py", GREEN_SHA))
    assert "green_sha=" not in (tidy.wt / ".tdd" / "issue-12-red-half").read_text()


def test_green_halfs_record_for_the_step_wins_over_red_halfs_4342(tidy):
    """SC8: when green-half.sh (or seam-settle.sh green-half) left a record for this step, its values are read."""
    (tidy.wt / ".tdd" / "issue-12-red-half").write_text(HAND_RED_HALF % STEP)
    (tidy.wt / ".tdd" / "issue-12-green-half").write_text(HAND_GREEN_HALF % STEP)
    code, out, err, fake = tidy()

    launch = [c for c in fake.calls if c[0] == "detach-leaf.sh"][1]
    assert (code, _short(launch[1])[-2:]) == (0, ("checks/green_check.py", GREEN_SHA))


@pytest.mark.parametrize("at", ["verdict-refactor", "skipped"])
def test_re_entered_after_a_revised_pass_it_finishes_once_without_a_second_verify_comment_4433(tidy, at):
    """PRD 038.9 RVS5: revise.sh posted verify-revised before re-saving the wait (`revised`)."""
    values = {"green_sha": GREEN_SHA, "budget": 5, "touched": TOUCHED, "test_path": "tests/test_a.py", "ran": True,
              "count": 1, "stopped": "nothing-left", "candidates": [], "flags": [], "revised": True}
    if at == "skipped":
        values["posted"] = True
    (tidy.wt / ".tdd" / "issue-12-refactor-half-wait").write_text(json.dumps({"conductor": None, "at": at,
                                                                               "values": values}))
    code, out, err, fake = tidy()

    assert (code, fake.launched()) == (0, [])
    assert [c[1][1] for c in fake.calls if c[0] == "comment.sh"] == ["refactor"]
    assert "refactor-budget.sh" not in fake.names()
