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
