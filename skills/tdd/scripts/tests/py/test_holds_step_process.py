"""Cases for holds-step.sh that start the real entry point over a real git repository."""
import subprocess

import pytest

from conftest import SCRIPTS
from repo_builder import commit_all, new_repo

HOLDS_STEP = str(SCRIPTS / "holds-step.sh")


def step_start(repo, tests):
    """A committed repository whose `veri: one test file:` command runs a test file with `sh`; returns HEAD's sha."""
    new_repo(repo)
    files = {"tests__" + name: body for name, body in tests.items()}
    return commit_all(repo, "base", **{"CLAUDE.md": 'veri: one test file: sh "$1"\n'}, **files)


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


@pytest.mark.process("holds-step.sh run in a real git repository whose tracked file differs from the step start")
def test_holds_step_exits_2_running_no_case_when_a_tracked_file_differs_from_the_step_start(tmp_path):
    repo, ran = tmp_path / "repo", tmp_path / "ran"
    sha = step_start(repo, {"a.sh": f"touch '{ran}'\n"})
    (repo / "CLAUDE.md").write_text('veri: one test file: sh "$1"\n# edited after the step start\n')

    code, _, _ = holds_step(repo, "42", sha, "tests/a.sh::case_a")

    assert (code, ran.exists()) == (2, False)


@pytest.mark.process("holds-step.sh run in a real git repository holding a commit made after the step start")
def test_holds_step_exits_2_running_no_case_when_a_commit_landed_after_the_step_start_4779(tmp_path):
    """A clean status proves nothing about a commit: only the diff against the step start sees it."""
    repo, ran = tmp_path / "repo", tmp_path / "ran"
    sha = step_start(repo, {"a.sh": f"touch '{ran}'\n"})
    (repo / "CLAUDE.md").write_text('veri: one test file: sh "$1"\n# committed after the step start\n')
    commit_all(repo, "after the start")

    code, _, err = holds_step(repo, "42", sha, "tests/a.sh::case_a")

    assert (code, ran.exists(), "a tracked file changed" in err) == (2, False, True)


@pytest.mark.process("holds-step.sh run in a real git repository whose worktree holds an untracked file")
def test_holds_step_exits_2_when_the_worktree_holds_an_untracked_file(tmp_path):
    repo, ran = tmp_path / "repo", tmp_path / "ran"
    sha = step_start(repo, {"a.sh": f"touch '{ran}'\n"})
    (repo / "tests" / "nested").mkdir()
    (repo / "tests" / "nested" / "new_test.sh").write_text("exit 0\n")

    code, _, _ = holds_step(repo, "42", sha, "tests/a.sh::case_a")

    assert (code, ran.exists()) == (2, False)


@pytest.mark.process("holds-step.sh run in a real git repository, a named id running no case")
@pytest.mark.parametrize("named", ["tests/missing.sh::case_m", "tests/empty.sh::case_e"],
                         ids=["cannot-run", "collects-nothing"])
def test_holds_step_exits_2_when_a_named_id_runs_no_case(tmp_path, named):
    sha = step_start(tmp_path, {"a.sh": "exit 0\n", "b.sh": "exit 1\n", "empty.sh": "echo 'collected 0 items'\nexit 5\n"})

    code, _, _ = holds_step(tmp_path, "42", sha, "tests/a.sh::case_a", "tests/b.sh::case_b", named)

    assert code == 2


@pytest.mark.process("holds-step.sh run in a clean real git repository with no id named")
def test_holds_step_with_n_and_sha_but_no_id_exits_2_with_its_usage_line_4779(tmp_path):
    sha = step_start(tmp_path, {"a.sh": "exit 0\n"})

    code, _, err = holds_step(tmp_path, "42", sha)

    assert code == 2, err
    assert err.splitlines()[-1] == "usage: holds-step.sh <n> <step-start-sha> <id>…"


@pytest.mark.process("holds-step.sh run in a clean real git repository over more ids than COVERING_TESTS: allows")
def test_holds_step_over_more_than_covering_tests_most_ids_exits_2_running_no_case_4779(tmp_path):
    from veri import covering_tests
    names = ["t%d.sh" % i for i in range(covering_tests.MOST + 1)]
    sha = step_start(tmp_path, {name: "touch ran-%s\n" % name for name in names})

    code, _, err = holds_step(tmp_path, "42", sha, *["tests/%s::case" % name for name in names])

    assert code == 2, err
    assert "at most %d" % covering_tests.MOST in err
    assert not list(tmp_path.glob("ran-*"))
