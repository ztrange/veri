"""Process cases for stack-culprit.sh, the shim over veri/stack_culprit.py: a real git clone of a local bare origin whose
default branch is `trunk` and whose CLAUDE.md names the stack branch `stack` and a one-test-file command, a stack whose
second issue turns a case red, and a stub gh answering the runs, the failed log and the reads from files."""
import json
import os
import subprocess

import pytest

from repo_builder import git
from stub_script import write_stub

SHIM = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "..", "stack-culprit.sh"))
GH = """here="$(dirname "$0")"
case "$*" in
  *actions/runs?branch=stack*) cat "$here/runs" ;;
  "run view 42 --log-failed"*) cat "$here/log" ;;
  *check-runs*) echo '{"total_count": 1, "check_runs": [{"status": "completed", "conclusion": "failure"}]}' ;;
  *pulls*) echo '[]' ;;
  *) exit 1 ;;
esac
"""
CASE = "t/test_a.py::test_x"
RUNNER = 'f="${1%%::*}"; [ -f "$f" ] || exit 4; if grep -q red "$f"; then echo "FAILED $1 - red"; exit 1; fi\n'


def culprit_clone(tmp_path):
    """A clone whose stack holds three commits on trunk: #11 adds the case green, #12 turns it red, #13 touches another
    file; their shas, oldest first."""
    origin, seed, work = tmp_path / "origin.git", tmp_path / "seed", tmp_path / "work"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "trunk", str(origin)], cwd=str(tmp_path), check=True)
    subprocess.run(["git", "init", "-q", "-b", "trunk", str(seed)], cwd=str(tmp_path), check=True)
    (seed / "CLAUDE.md").write_text('veri: stack branch: stack\nveri: one test file: sh run.sh "$1"\n')
    (seed / "run.sh").write_text(RUNNER)
    (seed / ".gitignore").write_text(".tdd/\n")
    git(seed, "add", "-A")
    git(seed, "commit", "-q", "-m", "docs: name the stack (#10)")
    git(seed, "remote", "add", "origin", str(origin))
    git(seed, "push", "-q", "origin", "trunk")
    subprocess.run(["git", "clone", "-q", str(origin), str(work)], cwd=str(tmp_path), check=True)
    git(work, "checkout", "-q", "-b", "stack")
    (work / "t").mkdir()
    shas = []
    for path, text, subject in (("t/test_a.py", "green", "feat: a (#11)"), ("t/test_a.py", "red", "feat: b (#12)"),
                                ("other.txt", "x", "feat: c (#13)")):
        (work / path).write_text(text)
        git(work, "add", "-A")
        git(work, "commit", "-q", "-m", subject)
        shas.append(git(work, "rev-parse", "HEAD"))
    git(work, "push", "-q", "origin", "stack")
    git(work, "checkout", "-q", "trunk")
    return work, shas


REPO = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
TINY = "def test_red():\n    assert 0\n\n\ndef test_green():\n    pass\n"


@pytest.mark.process("veri's own `veri: one test file:` command (make test TESTS=\"$1\") run for real on a tiny test file, in a directory holding veri's Makefile and CLAUDE.md and a link to its skills")
@pytest.mark.timeout(300)
def test_on_veris_own_one_test_file_command_a_failing_case_is_red_a_passing_one_not_and_a_missing_id_absent(
        tmp_path, monkeypatch):
    import importlib
    culprit = importlib.import_module("veri.stack_culprit")
    for name in ("Makefile", "CLAUDE.md"):
        (tmp_path / name).write_text(open(os.path.join(REPO, name), encoding="utf-8").read())
    (tmp_path / "skills").symlink_to(os.path.join(REPO, "skills"))
    (tmp_path / "t").mkdir()
    (tmp_path / "t" / "test_tiny.py").write_text(TINY)
    command = culprit._one_file_command(str(tmp_path))
    monkeypatch.setenv("VERI_TIMEOUT", "600")
    monkeypatch.setenv("VERI_PYTEST_WORKERS", "1")

    said = {}
    for name in ("test_red", "test_green", "test_nope"):
        case = "t/test_tiny.py::" + name
        code, output = culprit._run_alone(str(tmp_path), command, case)
        said[name] = (code, culprit._verdict(code, output, case))

    assert (command, said) == ('make test TESTS="$1"', {"test_red": (2, True), "test_green": (0, False),
                                                        "test_nope": (2, culprit.ABSENT)}), said


@pytest.mark.process("stack-culprit.sh run as its /bin/sh shim in a clone of a local bare origin holding a stack, with a stub gh on PATH, adding and removing a real worktree")
def test_stack_culprit_names_the_issue_whose_end_turned_the_case_red_and_removes_its_worktree(tmp_path):
    work, shas = culprit_clone(tmp_path)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    write_stub(str(bin_dir / "gh"), GH)
    (bin_dir / "runs").write_text(json.dumps({"total_count": 1, "workflow_runs": [
        {"head_sha": shas[2], "html_url": "https://github.com/o/r/actions/runs/42", "status": "completed",
         "conclusion": "failure", "created_at": "2026-11-16T10:00:00Z", "repository": {"full_name": "o/r"},
         "head_repository": {"full_name": "o/r"}, "run_attempt": 1, "workflow_id": 7}]}))
    (bin_dir / "log").write_text("tests\tRun\t﻿2026-11-16T10:00:00.1Z FAILED %s - red\n" % CASE)
    env = {**os.environ, "PATH": "%s:%s" % (bin_dir, os.environ["PATH"])}

    done = subprocess.run([SHIM, shas[2]], cwd=str(work), env=env, capture_output=True, text=True,
                          stdin=subprocess.DEVNULL, timeout=60)

    assert (done.returncode, done.stdout.splitlines()) == (0, [
        "red: " + shas[2], "issue: 12", "commit: " + shas[1], "before: " + shas[0], "case: %s\tFAILED %s - red" % (CASE, CASE)
    ]), done.stderr
    worktrees = git(work, "worktree", "list", "--porcelain")
    assert (worktrees.count("worktree "), git(work, "rev-parse", "HEAD") == git(work, "rev-parse", "origin/trunk"),
            os.listdir(work / ".tdd") if (work / ".tdd").exists() else []) == (1, True, []), worktrees
