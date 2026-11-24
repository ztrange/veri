"""In-process cases for veri/pr_checks.py, the module pr-checks.sh is a shim over (PRD 038.8, #4392)."""
import importlib
import os

import pytest

LEDGER = "# Plan for #12\n\n- [x] one ⟦criterion 1⟧\n- [x] the full suite is green ⟦full-suite⟧ ⟦criterion 2⟧\n"
BASE = "b" * 40
LINT = "make lint"
URL = "https://github.com/o/r/issues/99"


class Fake:
    """A run_script stand-in: records (basename, args, cwd, env, kw) and answers from <answers>, keyed by
    (basename, a tuple of leading arguments, or None) -> (code, stdout). <files> maps a worktree path to the text a
    call writes there: {(basename, leading arguments): {path: text}}."""

    def __init__(self, wt, answers=None, files=None):
        self.wt, self.answers, self.files, self.calls = wt, dict(answers or {}), dict(files or {}), []

    def __call__(self, name, *args, cwd=None, env=None, **kw):
        base = os.path.basename(name)
        self.calls.append((base, args, cwd, env, kw))
        for (script, lead), written in self.files.items():
            if base == script and args[:len(lead)] == lead:
                for path, text in written.items():
                    (self.wt / path).write_text(text)
        for (script, lead), (code, out) in self.answers.items():
            if base == script and (lead is None or args[:len(lead)] == lead):
                return code, out, ""
        if base == "git" and args[:1] == ("merge-base",):
            return 0, BASE + "\n", ""
        if base == "detect-test-command.sh":
            return 0, LINT + "\n", ""
        if base == "detach-command.sh" and args[:1] == ("wait",):
            (self.wt / ".tdd" / "lint.exit").write_text("0\n")
            return 0, "", ""
        if base in ("test-quality.sh", "red-setup.sh", "coupling.sh", "refactor-candidates.sh", "unwired.sh"):
            return 3, "", ""
        return 0, "", ""

    def names(self):
        return [c[0] for c in self.calls]

    def call(self, base, first=None):
        return next(c for c in self.calls if c[0] == base and (first is None or c[1][:1] == (first,)))


@pytest.fixture
def checks(monkeypatch, run_cli, tmp_path):
    """checks(answers=None, files=None, missing=(), argv=None, ledger=LEDGER) runs pr-checks for issue 12 from the main
    tree, the run's worktree at .tdd/wt/12; returns (code, stdout, stderr, fake)."""
    fused = importlib.import_module("veri.fused")
    pr_checks = importlib.import_module("veri.pr_checks")
    monkeypatch.setattr(pr_checks, "default_branch", lambda wt: "main")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)

    def go(answers=None, files=None, missing=(), argv=None, ledger=LEDGER, fake=None):
        given = {"preflight": (wt / ".tdd" / "issue-12-preflight", "worktree=%s\nfast_cmd=make unit\n" % wt),
                 "ledger": (wt / ".tdd" / "issue-12.md", ledger)}
        for key, (path, text) in given.items():
            if key not in missing:
                path.write_text(text)
        fake = fake or Fake(wt, answers, files)
        monkeypatch.setattr(fused, "run_script", fake)
        code, out, err = run_cli(pr_checks, list(argv if argv is not None else ("12",)), cwd=str(tmp_path))
        return code, out, err, fake

    go.wt = wt
    return go


@pytest.mark.parametrize("argv, missing, named", [
    ((), (), "usage: pr-checks.sh <n>"), (("x",), (), "usage: pr-checks.sh <n>"),
    (("12",), ("preflight",), ".tdd/issue-12-preflight"), (("12",), ("ledger",), ".tdd/issue-12.md")])
def test_4392_bad_arguments_or_a_missing_input_is_exit_2_naming_it_before_any_call(checks, argv, missing, named):
    code, out, err, fake = checks(argv=argv, missing=missing)

    assert (code, fake.calls) == (2, [])
    assert named in err


def test_4392_a_clean_run_makes_the_checks_in_order_with_draft_pr_s_arguments_one_line_per_call(checks):
    (checks.wt / ".tdd" / "lint.out").write_text("LINT-OUTPUT-MARKER\n")
    code, out, err, fake = checks()

    assert code == 0, out + err
    assert [(c[0], c[1]) for c in fake.calls if c[0] != "git"] == [
        ("detect-test-command.sh", ("--tier", "lint")),
        ("detach-command.sh", ("start", "lint", "sh", "-c", LINT)),
        ("detach-command.sh", ("wait", "lint", "--total", "1800")),
        ("event.sh", ("lint", "exit=0")),
        ("test-quality.sh", ("files", BASE)),
        ("red-setup.sh", ("worst", "12", ".tdd/issue-12-refactor-owed.md")),
        ("coupling.sh", (BASE,)),
        ("refactor-owed.sh", ("clear", ".tdd/issue-12-refactor-owed.md", "coupling")),
        ("refactor-candidates.sh", ("12", ".tdd/issue-12-refactor-owed.md")),
        ("unwired.sh", ("--accepted", ".tdd/issue-12-unwired-accepted", BASE))]
    assert ("git", ("merge-base", "HEAD", "origin/main")) in [(c[0], c[1]) for c in fake.calls]
    assert {k: v for k, v in fake.call("detach-command.sh", "wait")[4].items() if v} == {
        "out": "/dev/null", "err": ".tdd/lint.wait.err"}
    assert fake.call("test-quality.sh")[4]["out"] == ".tdd/test-quality-files"
    assert (fake.call("coupling.sh")[4]["out"], fake.call("unwired.sh")[4]["out"]) == (".tdd/coupling.out",
                                                                                      ".tdd/unwired.out")
    lint = fake.call("event.sh")[3]
    assert (lint["VERI_ISSUE"], lint["VERI_ACTOR"]) == ("12", "conductor")
    assert all(c[2] == str(checks.wt) for c in fake.calls)
    assert (checks.wt / ".tdd" / "issue-12-lint.md").read_text() == "### Lint\n\n`make lint` passed.\n"
    assert (checks.wt / ".tdd" / "issue-12-test-quality").read_text() == ""
    assert "LINT-OUTPUT-MARKER" not in out
    named = [line for line in out.splitlines() if line.split(" ", 1)[0] in set(fake.names())]
    assert len(named) == len(fake.calls) and all(" exit " in line for line in named)


FORBIDDEN = {"detach-leaf.sh", "supervise.sh", "run-leaf.sh", "wait-leaf.sh", "add-ledger-step.sh", "lint-repair.sh",
             "push-branch.sh", "pr-ready.sh", "pr-ready-wait.sh", "metrics.sh"}


def test_4392_a_clean_run_settles_the_candidates_url_and_launches_appends_commits_pushes_readies_and_renders_nothing(
        checks):
    code, out, err, fake = checks(answers={("refactor-candidates.sh", None): (0, URL + "\n")})

    assert code == 0, out + err
    assert out.endswith("candidates=%s\n" % URL)
    assert (checks.wt / ".tdd" / "issue-12-pr-checks").read_text() == "candidates=%s\n" % URL
    assert FORBIDDEN & set(fake.names()) == set()
    assert [c[1] for c in fake.calls if c[0] == "git" and c[1][:1] in (("commit",), ("push",), ("add",))] == []
    assert (checks.wt / ".tdd" / "issue-12.md").read_text() == LEDGER


def test_4392_touched_test_files_stop_it_with_exit_1_at_test_quality_before_the_leaf_launch(checks):
    code, out, err, fake = checks(answers={("test-quality.sh", ("files",)): (0, "")})

    assert code == 1
    assert out.splitlines()[-1] == ("stopped at test-quality test-quality.sh files %s > .tdd/test-quality-files exit 0"
                                    % BASE)
    assert fake.names()[-1] == "test-quality.sh"
    assert not (checks.wt / ".tdd" / "issue-12-test-quality").exists()


WAITED = "detach-command.sh wait lint --total 1800 > /dev/null 2> .tdd/lint.wait.err"


def test_4392_a_red_lint_writes_its_event_and_section_then_stops_it_at_lint_before_any_repair_step(checks):
    lines = ["line %d" % i for i in range(25)] + ["x" * 400]
    (checks.wt / ".tdd" / "lint.out").write_text("\n".join(lines) + "\n")
    code, out, err, fake = checks(answers={("detach-command.sh", ("wait",)): (1, "2\n")},
                                  files={("detach-command.sh", ("wait",)): {".tdd/lint.exit": "2\n"}})

    assert (code, out.splitlines()[-1]) == (1, "stopped at lint %s exit 1" % WAITED)
    assert (fake.calls[-1][0], fake.calls[-1][1]) == ("event.sh", ("lint", "exit=2"))
    tail = "".join(line[:300] + "\n" for line in lines[-20:])
    assert (checks.wt / ".tdd" / "issue-12-lint.md").read_text() == (
        "### Lint\n\n`make lint` exited 2. The last 20 lines of its output:\n\n~~~text\n" + tail + "~~~\n")
    assert (checks.wt / ".tdd" / "issue-12.md").read_text() == LEDGER


def test_4392_a_coupling_pair_writes_the_coupling_section_then_stops_it_at_coupling_recording_no_row(checks):
    pair = "mutual: src/a.py src/b.py\n"
    code, out, err, fake = checks(answers={("coupling.sh", None): (0, "")},
                                  files={("coupling.sh", ()): {".tdd/coupling.out": pair}})

    assert (code, out.splitlines()[-1]) == (1, "stopped at coupling coupling.sh %s > .tdd/coupling.out exit 0" % BASE)
    assert fake.names()[-1] == "coupling.sh"
    assert (checks.wt / ".tdd" / "issue-12-coupling.md").read_text() == "### Coupling\n\n" + pair


def test_4392_an_unwired_finding_stops_it_at_unwired_writing_no_pending_record_and_no_bail(checks):
    code, out, err, fake = checks(answers={("unwired.sh", None): (1, "")},
                                  files={("unwired.sh", ()): {".tdd/unwired.out": "src/lonely.py\n"}})

    assert (code, out.splitlines()[-1]) == (1, "stopped at unwired unwired.sh --accepted .tdd/issue-12-unwired-accepted "
                                               "%s > .tdd/unwired.out exit 1" % BASE)
    assert fake.names()[-1] == "unwired.sh"
    assert not (checks.wt / ".tdd" / "issue-12-unwired-pending").exists()
    assert not (checks.wt / ".tdd" / "issue-12-pr-checks").exists()


def test_4392_a_lint_wait_that_runs_out_exits_3_and_a_second_call_only_waits_again(checks):
    code, out, err, fake = checks(answers={("detach-command.sh", ("wait",)): (3, "")})

    assert (code, out.splitlines()[-1]) == (3, "waiting on lint")
    assert fake.calls[-1][:2] == ("detach-command.sh", ("wait", "lint", "--total", "1800"))
    assert (checks.wt / ".tdd" / "issue-12-pr-checks-wait").exists()

    code, out, err, again = checks()

    assert code == 0, out + err
    assert [c[1][:2] for c in again.calls if c[0] == "detach-command.sh"] == [("wait", "lint")]
    assert "detect-test-command.sh" not in again.names()
    assert (checks.wt / ".tdd" / "issue-12-lint.md").read_text() == "### Lint\n\n`make lint` passed.\n"
    assert not (checks.wt / ".tdd" / "issue-12-pr-checks-wait").exists()


WEAK = "weak-assertion | tests/test_a.py::test_one | asserts only truthiness\n"
FIXED = "- [ ] fix the weak-assertion case tests/test_a.py::test_one: why ⟦test-quality⟧ ⟦diff-checked⟧\n"
OTHER = "- [ ] fix the weak-assertion case tests/test_b.py::test_two: why ⟦test-quality⟧ ⟦diff-checked⟧\n"


@pytest.mark.parametrize("record, more, code", [
    (WEAK, "", 1), (WEAK.replace("weak-assertion", "implementation-coupled"), "", 1),
    (WEAK.replace("weak-assertion", "redundant"), "", 0), (WEAK, FIXED, 0), (WEAK, OTHER, 0), ("", "", 0)],
    ids=["weak owed", "coupled owed", "redundant gets no step", "already a step", "budget spent", "empty record"])
def test_4392_a_recorded_finding_the_fix_budget_still_owes_a_step_stops_it_at_test_quality(checks, record, more, code):
    (checks.wt / ".tdd" / "issue-12-test-quality").write_text(record)
    code_, out, err, fake = checks(ledger=LEDGER + more)

    assert code_ == code, out + err
    assert "test-quality.sh" not in fake.names()
    if code:
        assert out.splitlines()[-1] == "stopped at test-quality .tdd/issue-12-test-quality owes a fix step"
        assert fake.names()[-1] == "event.sh"


NO_LINT = {("stop-requested.sh", None): (3, "")}
WAIT_2 = {("detach-command.sh", ("wait",)): (2, ""), **NO_LINT}
PAST = {("detach-command.sh", ("wait",)): {".tdd/lint.wait.err": "lint: still running past --total 1800\n"}}


@pytest.mark.parametrize("answers, files, section, code", [
    ({("detect-test-command.sh", None): (3, "")}, None, "", 0),
    ({("detect-test-command.sh", None): (2, "")}, None,
     "### Lint\n\nThe lint command could not be read: detect-test-command.sh --tier lint exited 2.\n", 0),
    (WAIT_2, PAST, "### Lint\n\n`make lint` did not finish within VERI_LINT_TIMEOUT (1800 seconds) and was stopped.\n", 0),
    (WAIT_2, None, "### Lint\n\n`make lint` could not be run: no exit code was recorded.\n", 0),
    ({**WAIT_2, ("stop-requested.sh", None): (0, "now\n")}, None, "", 1)],
    ids=["no lint line", "lint line unreadable", "past the bound", "no exit recorded", "stop requested now"])
def test_4392_a_lint_with_no_exit_code_writes_its_sentence_and_goes_on_unless_a_stop_is_now(checks, answers, files,
                                                                                            section, code):
    code_, out, err, fake = checks(answers=answers, files=files)

    assert code_ == code, out + err
    assert "event.sh" not in fake.names()
    assert (checks.wt / ".tdd" / "issue-12-lint.md").read_text() == section
    if code:
        assert out.splitlines()[-1] == "stopped at lint stop-requested.sh exit 0 now"
    if answers.get(("detect-test-command.sh", None)):
        assert "detach-command.sh" not in fake.names()


def test_4392_a_clear_that_drops_a_stale_coupling_row_stops_it_at_coupling_for_the_conductor_s_commit(checks):
    owed = checks.wt / ".tdd" / "issue-12-refactor-owed.md"
    owed.write_text("| coupling | mutual reference: a b | not-done |\n")
    code, out, err, fake = checks(files={("refactor-owed.sh", ("clear",)): {".tdd/issue-12-refactor-owed.md": ""}})

    assert (code, out.splitlines()[-1]) == (1, "stopped at coupling refactor-owed.sh clear "
                                               ".tdd/issue-12-refactor-owed.md coupling dropped a stale row")
    assert fake.names()[-1] == "refactor-owed.sh"
    assert [c[1][:1] for c in fake.calls if c[0] == "git"] == [("merge-base",)]


ROW = "| testability | red setup of step 2: 5 lines | not-done |\n"


@pytest.mark.parametrize("before, code", [("", 1), (ROW, 0)], ids=["row written", "row unchanged"])
def test_4392_a_red_setup_row_with_no_coupling_pair_stops_it_at_coupling_for_the_conductor_s_commit(checks, before,
                                                                                                  code):
    owed = checks.wt / ".tdd" / "issue-12-refactor-owed.md"
    owed.write_text(before)
    code_, out, err, fake = checks(answers={("red-setup.sh", None): (0, "")},
                                   files={("red-setup.sh", ("worst",)): {".tdd/issue-12-refactor-owed.md": ROW}})

    assert code_ == code, out + err
    assert [c[1][:1] for c in fake.calls if c[0] == "git"] == [("merge-base",)]
    if code:
        assert out.splitlines()[-1] == ("stopped at coupling red-setup.sh worst 12 .tdd/issue-12-refactor-owed.md "
                                        "changed the owed file")
        assert fake.names()[-1] == "refactor-owed.sh"
        assert owed.read_text() == ROW


@pytest.mark.parametrize("failing, inner", [
    (("git", ("merge-base",)), 128), (("detach-command.sh", ("start",)), 1), (("event.sh", None), 1),
    (("stop-requested.sh", None), 2), (("test-quality.sh", ("files",)), 2), (("red-setup.sh", None), 2),
    (("red-setup.sh", None), 1), (("coupling.sh", None), 2), (("refactor-owed.sh", ("clear",)), 1),
    (("coupling.sh", None), 1), (("refactor-candidates.sh", None), 2), (("unwired.sh", None), 2),
    (("unwired.sh", None), 4), (("unwired.sh", None), 127)],
    ids=["merge-base", "lint start", "lint event", "stop-requested", "test-quality files", "red-setup 2",
         "red-setup 1", "coupling", "refactor-owed clear", "coupling 1", "refactor-candidates", "unwired", "unwired 4",
         "unwired 127"])
def test_4392_an_inner_call_that_obtains_no_answer_stops_it_with_exit_2_at_that_call(checks, failing, inner):
    answers = {failing: (inner, "")}
    if failing[0] == "stop-requested.sh":
        answers[("detach-command.sh", ("wait",))] = (2, "")
    code, out, err, fake = checks(answers=answers)

    assert code == 2, out + err
    assert fake.names()[-1] == failing[0]
    assert out.splitlines()[-1].startswith("stopped at ")
    assert out.splitlines()[-1].endswith(" exit %d" % inner)


def test_4392_no_default_branch_stops_it_with_exit_2_before_any_call(checks, monkeypatch):
    monkeypatch.setattr(importlib.import_module("veri.pr_checks"), "default_branch", lambda wt: "")
    code, out, err, fake = checks()

    assert (code, fake.calls, out.splitlines()[-1]) == (2, [], "stopped at branch-base no default branch")


def test_4392_draft_pr_sub_step_1_names_pr_checks_and_every_script_of_its_ordered_list(checks):
    from pathlib import Path
    pr_checks = importlib.import_module("veri.pr_checks")
    draft = (Path(pr_checks.__file__).resolve().parents[2] / "DRAFT-PR.md").read_text()
    sub_step = draft[draft.index("\n1. Run `$S/pr-prepare.sh"):draft.index("\n2. **Mark the PR ready")]

    assert "$S/pr-checks.sh <n>" in sub_step
    assert [name for name in pr_checks.CALLS if "$S/" + name not in sub_step] == []
    code, out, err, fake = checks()
    made = [name for name in fake.names() if name != "git"]
    assert set(pr_checks.CALLS) - set(made) == {"stop-requested.sh"} and set(made) <= set(pr_checks.CALLS)
    firsts = [made.index(name) for name in pr_checks.CALLS if name in made]
    assert firsts == sorted(firsts)


def test_4709_a_step_only_quoting_test_quality_in_its_prose_is_no_existing_test_quality_step(checks):
    (checks.wt / ".tdd" / "issue-12-test-quality").write_text(WEAK)
    quoting = "- [ ] document tests/test_a.py::test_one and the `⟦test-quality⟧` mark ⟦criterion 2⟧\n"
    code, out, err, fake = checks(ledger=LEDGER + quoting)

    assert code == 1, out + err
    assert out.splitlines()[-1] == "stopped at test-quality .tdd/issue-12-test-quality owes a fix step"
