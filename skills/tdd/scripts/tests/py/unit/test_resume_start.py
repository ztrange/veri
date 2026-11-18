"""In-process cases for veri/resume_start.py, the module resume-start.sh is a shim over (PRD 038.6, #4389)."""
import importlib
import os

import pytest

PR_URL = "https://github.com/o/r/pull/77"
LEDGER = "# Plan for #12\n\n- [x] one ⟦criterion 1⟧\n- [ ] two ⟦criterion 2⟧\n"
SPEC = "## Problem\n\nA thing.\n\n## Acceptance criteria\n\n- [x] first\n- [ ] second\n"


class Fake:
    """A run_script stand-in: records (basename, args, cwd, env, kw) and answers from <answers>, keyed by
    (basename, first argument or None) -> (code, stdout)."""

    def __init__(self, answers=None, pr=PR_URL + "\n"):
        self.answers, self.calls, self.pr = dict(answers or {}), [], pr

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


@pytest.fixture
def resume(monkeypatch, run_cli, tmp_path):
    """resume(answers=None, fake=None, missing=(), verify_plan="skip", argv=None) runs resume-start for issue 12 from
    the main tree, the run's worktree at .tdd/wt/12; returns (code, stdout, stderr, fake)."""
    fused = importlib.import_module("veri.fused")
    resume_start = importlib.import_module("veri.resume_start")
    wt = tmp_path / ".tdd" / "wt" / "12"
    (wt / ".tdd").mkdir(parents=True)

    def go(answers=None, fake=None, missing=(), verify_plan="skip", argv=None, stray=()):
        files = {"preflight": (wt / ".tdd" / "issue-12-preflight",
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


def test_4389_a_clean_resume_asks_for_a_pending_refactor_then_the_step_marks_and_comments_and_reads_the_pr(resume):
    code, out, err, fake = resume(stray=("tests/t.py", "x.py"))

    assert _seq(fake) == [
        ("next-pending-refactor.sh", ()), ("next-unchecked.sh", ()), ("ledger-steps.sh", ("current-or-last-done",)),
        ("event.sh", ("resume",)), ("comment.sh", ("12", "resuming")), ("git", ("branch", "--show-current")),
        ("gh", ("api", "repos/{owner}/{repo}/pulls?head={owner}:tdd/12-a-thing"))]
    assert {c[4].get("stdin") for c in fake.calls[:3]} == {LEDGER}
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
