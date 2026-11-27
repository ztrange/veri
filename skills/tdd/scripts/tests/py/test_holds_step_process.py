"""Cases for holds-step.sh that start the real entry point over a real git repository."""
import subprocess

import pytest

from conftest import SCRIPTS

HOLDS_STEP = str(SCRIPTS / "holds-step.sh")


def git(repo, *argv):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *argv], cwd=repo, check=True,
                          capture_output=True, text=True).stdout.strip()


def step_start(repo, tests):
    """A committed repository whose `veri: one test file:` command runs a test file with `sh`; returns HEAD's sha."""
    (repo / "tests").mkdir(parents=True)
    (repo / "CLAUDE.md").write_text('veri: one test file: sh "$1"\n')
    for name, body in tests.items():
        (repo / "tests" / name).write_text(body)
    git(repo, "init", "-q")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "base")
    return git(repo, "rev-parse", "HEAD")


def holds_step(repo, *argv):
    done = subprocess.run([HOLDS_STEP, *argv], cwd=repo, stdin=subprocess.DEVNULL, capture_output=True, text=True)
    return done.returncode, done.stdout, done.stderr


@pytest.mark.process("holds-step.sh run in a real git repository, each case through its one-test-file command")
def test_holds_step_exits_0_when_every_named_case_passes(tmp_path):
    sha = step_start(tmp_path, {"a.sh": "exit 0\n", "b.sh": "exit 0\n"})

    code, _, err = holds_step(tmp_path, "42", sha, "tests/a.sh::case_a", "tests/b.sh::case_b")

    assert (code, err) == (0, "")


@pytest.mark.process("holds-step.sh run with no arguments")
def test_holds_step_with_no_arguments_exits_2_with_its_usage_line(tmp_path):
    code, _, err = holds_step(tmp_path)

    assert code == 2
    assert err.splitlines()[-1] == "usage: holds-step.sh <n> <step-start-sha> <id>…"


@pytest.mark.process("holds-step.sh run in a real git repository, each case through its one-test-file command")
def test_holds_step_exits_1_when_a_named_case_fails(tmp_path):
    sha = step_start(tmp_path, {"a.sh": "exit 0\n", "b.sh": "exit 1\n"})

    code, _, _ = holds_step(tmp_path, "42", sha, "tests/a.sh::case_a", "tests/b.sh::case_b")

    assert code == 1
