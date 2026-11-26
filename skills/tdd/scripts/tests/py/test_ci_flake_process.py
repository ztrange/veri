"""ci-flake.sh's entry point: the shim runs veri/ci_flake.py, its alone runs are real `sh` processes, and its exit code
and output pass through. No case reaches `gh`, which the suite refuses. The module's logic is tested in-process, in
tests/py/unit/test_ci_flake.py."""
import importlib
import os
import subprocess

import pytest

from conftest import SCRIPTS

FLAKE = str(SCRIPTS / "ci-flake.sh")
HEAD = "0123456789abcdef0123456789abcdef01234567"
LOG = "test\tRun make test\t2026-11-13T18:30:00.1234567Z FAILED a/test_x.py::test_one - boom\n"


def run(*argv, cwd=None):
    ran = subprocess.run([FLAKE, *argv], cwd=cwd, stdin=subprocess.DEVNULL, capture_output=True, text=True)
    return ran.returncode, ran.stdout, ran.stderr


def committed(tmp_path):
    """A clean git worktree at <tmp_path> with one commit, the CI log ignored; its HEAD sha."""
    def git(*args):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=tmp_path,
                              stdin=subprocess.DEVNULL, capture_output=True, text=True, check=True).stdout
    git("init", "-q")
    (tmp_path / ".gitignore").write_text("failed.log\n.tdd/\n")
    git("add", ".gitignore")
    git("commit", "-q", "-m", "one")
    return git("rev-parse", "HEAD").strip()


@pytest.mark.process("ci-flake.sh run as a script in a real git worktree, its alone command a real sh that fails")
def test_the_shim_passes_exit_1_through_when_a_target_stays_red_alone_writing_no_event(tmp_path):
    head = committed(tmp_path)
    (tmp_path / "failed.log").write_text(LOG)

    assert run("7", head, "555", 'test "$1" = other', "failed.log", cwd=tmp_path) == (1, "", "")
    assert not (tmp_path / ".tdd" / "events.jsonl").exists()


@pytest.mark.process("ci-flake.sh run as a script in a real git worktree whose HEAD is not the given head")
def test_the_shim_passes_exit_2_through_when_head_is_not_the_ci_head(tmp_path):
    committed(tmp_path)
    (tmp_path / "failed.log").write_text(LOG)

    code, out, err = run("7", HEAD, "555", "true", "failed.log", cwd=tmp_path)

    assert (code, out, len(err.splitlines()), "not the CI run's head" in err) == (2, "", 1, True)


@pytest.mark.process("ci-flake.sh run as a script")
def test_the_shim_passes_exit_3_through_when_the_knob_is_0(tmp_path):
    (tmp_path / "failed.log").write_text(LOG)

    ran = subprocess.run([FLAKE, "7", HEAD, "555", "true", "failed.log"], cwd=tmp_path, stdin=subprocess.DEVNULL,
                         capture_output=True, text=True, env=dict(os.environ, VERI_CI_FLAKE_RERUNS="0"))

    assert (ran.returncode, ran.stdout, ran.stderr) == (3, "", "")


@pytest.mark.process("ci-flake.sh run as a script")
def test_the_shim_passes_exit_2_and_the_usage_through_for_four_arguments(tmp_path):
    usage = importlib.import_module("veri.ci_flake").USAGE + "\n"

    assert run("7", HEAD, "555", "true", cwd=tmp_path) == (2, "", usage)
