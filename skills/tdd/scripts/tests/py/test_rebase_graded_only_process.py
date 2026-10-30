"""Cases for rebase-onto-default.sh --graded-only on a real git repository."""
import subprocess
from pathlib import Path

import pytest

from conftest import INTERPRETER_VENV

SCRIPTS = Path(__file__).resolve().parents[2]


@pytest.mark.process("a real two-branch git repository with a bare origin and rebase-onto-default.sh --graded-only")
def test_2706_graded_only_with_a_conflict_in_a_graded_file_and_another_path_aborts_exits_1_and_names_both(tmp_path):
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV,
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    work = tmp_path / "work"
    (work / "guide").mkdir(parents=True)

    def git(*argv):
        return subprocess.run(["git", *argv], cwd=work, env=env, check=True, capture_output=True, text=True).stdout.strip()

    def commit(graded, other, message):
        (work / "guide" / "GRADED").write_text(graded)
        (work / "guide" / "other.txt").write_text(other)
        git("add", ".")
        git("commit", "-q", "-m", message)

    git("init", "-q", "-b", "main")
    commit("guide/a.md " + "0" * 64 + " 2026-01-01 base\n", "base\n", "base")
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(tmp_path / "origin.git")], cwd=tmp_path, env=env, check=True)
    git("remote", "add", "origin", str(tmp_path / "origin.git"))
    git("push", "-q", "origin", "main")
    git("fetch", "-q", "origin")
    git("remote", "set-head", "origin", "main")
    commit("guide/a.md " + "1" * 64 + " 2026-01-01 upstream\n", "upstream\n", "upstream")
    git("push", "-q", "origin", "main")
    git("checkout", "-q", "-b", "work", "HEAD~1")
    commit("guide/a.md " + "2" * 64 + " 2026-01-01 branch\n", "branch\n", "branch")
    before = git("rev-parse", "HEAD")

    ran = subprocess.run([str(SCRIPTS / "rebase-onto-default.sh"), "--graded-only"], cwd=work, env=env,
                         capture_output=True, text=True)

    assert (ran.returncode, sorted(ran.stdout.split()), git("rev-parse", "HEAD"),
            (work / ".git" / "rebase-merge").exists()) == (1, ["guide/GRADED", "guide/other.txt"], before, False), ran.stderr


@pytest.mark.process("a real two-branch git repository with a bare origin and rebase-onto-default.sh without the flag")
def test_2706_without_the_flag_a_conflict_only_in_a_graded_file_aborts_exits_1_and_names_it(tmp_path):
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV,
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    work = tmp_path / "work"
    (work / "guide").mkdir(parents=True)

    def git(*argv):
        return subprocess.run(["git", *argv], cwd=work, env=env, check=True, capture_output=True, text=True).stdout.strip()

    def commit(graded, message):
        (work / "guide" / "GRADED").write_text(graded)
        git("add", ".")
        git("commit", "-q", "-m", message)

    git("init", "-q", "-b", "main")
    commit("guide/a.md " + "0" * 64 + " 2026-01-01 base\n", "base")
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(tmp_path / "origin.git")], cwd=tmp_path, env=env, check=True)
    git("remote", "add", "origin", str(tmp_path / "origin.git"))
    git("push", "-q", "origin", "main")
    git("fetch", "-q", "origin")
    git("remote", "set-head", "origin", "main")
    commit("guide/a.md " + "1" * 64 + " 2026-01-01 upstream\n", "upstream")
    git("push", "-q", "origin", "main")
    git("checkout", "-q", "-b", "work", "HEAD~1")
    commit("guide/a.md " + "2" * 64 + " 2026-01-01 branch\n", "branch")
    before = git("rev-parse", "HEAD")

    ran = subprocess.run([str(SCRIPTS / "rebase-onto-default.sh")], cwd=work, env=env, capture_output=True, text=True)

    assert (ran.returncode, ran.stdout.split(), git("rev-parse", "HEAD"),
            (work / ".git" / "rebase-merge").exists()) == (1, ["guide/GRADED"], before, False), ran.stderr
