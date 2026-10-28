"""Cases for restore-production.sh that start the real entry point and real git."""
import shutil
import subprocess

import pytest

from conftest import SCRIPTS

GIT_ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}


def git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True,
                          env={"PATH": __import__("os").environ["PATH"], **GIT_ENV}).stdout


@pytest.mark.process("restore-production.sh run against a real git repository in tmp_path")
def test_issue_2495_restore_production_drops_a_rejected_greens_edits_and_keeps_the_reds_test(tmp_path):
    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    git(repo, "init", "-q")
    (repo / "src" / "prod.py").write_text("VALUE = 1\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "base")
    (repo / "test_new.py").write_text("def test_new():\n    assert False\n")
    (repo / "src" / "prod.py").write_text("VALUE = 2\n")
    (repo / "src" / "added.py").write_text("EXTRA = 1\n")

    ran = subprocess.run(["sh", str(SCRIPTS / "restore-production.sh"), "test_new.py"], cwd=repo,
                         capture_output=True, text=True)

    assert ran.returncode == 0, ran.stderr
    assert (repo / "src" / "prod.py").read_text() == "VALUE = 1\n"
    assert not (repo / "src" / "added.py").exists()
    assert (repo / "test_new.py").read_text() == "def test_new():\n    assert False\n"


@pytest.mark.process("restore-production.sh run against a real git repository in tmp_path")
def test_issue_2495_restore_production_keeps_a_tracked_test_the_red_changed(tmp_path):
    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    git(repo, "init", "-q")
    (repo / "src" / "prod.py").write_text("VALUE = 1\n")
    (repo / "test_old.py").write_text("def test_old():\n    assert True\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "base")
    (repo / "test_old.py").write_text("def test_old():\n    assert True\n\n\ndef test_red():\n    assert False\n")
    (repo / "src" / "prod.py").write_text("VALUE = 2\n")

    ran = subprocess.run(["sh", str(SCRIPTS / "restore-production.sh"), "test_old.py"], cwd=repo,
                         capture_output=True, text=True)

    assert ran.returncode == 0, ran.stderr
    assert (repo / "src" / "prod.py").read_text() == "VALUE = 1\n"
    assert (repo / "test_old.py").read_text() == "def test_old():\n    assert True\n\n\ndef test_red():\n    assert False\n"


@pytest.mark.process("restore-production.sh run outside any git repository in tmp_path")
def test_issue_2579_restore_production_exits_2_with_gits_stderr_when_git_refuses(tmp_path):
    outside = tmp_path / "not-a-repo"
    outside.mkdir()

    ran = subprocess.run(["sh", str(SCRIPTS / "restore-production.sh"), "test_new.py"], cwd=outside,
                         capture_output=True, text=True,
                         env={**__import__("os").environ, "GIT_CEILING_DIRECTORIES": str(tmp_path)})

    assert ran.returncode == 2, ran.stderr
    assert ran.stderr.startswith("restore-production.sh: ")
    assert "not a git repository" in ran.stderr


@pytest.mark.process("restore-production.sh run against a real git repository in tmp_path")
def test_issue_2579_restore_production_names_a_partial_restore_when_clean_fails_after_checkout(tmp_path):
    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    git(repo, "init", "-q")
    (repo / "src" / "prod.py").write_text("VALUE = 1\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "base")
    (repo / "src" / "prod.py").write_text("VALUE = 2\n")
    (repo / "src" / "added.py").write_text("EXTRA = 1\n")
    shim = tmp_path / "bin"
    shim.mkdir()
    (shim / "git").write_text('#!/bin/sh\n[ "$1" = clean ] && { echo "fatal: clean refused" >&2; exit 128; }\n'
                              'exec "%s" "$@"\n' % shutil.which("git"))
    (shim / "git").chmod(0o755)

    ran = subprocess.run(["sh", str(SCRIPTS / "restore-production.sh"), "test_new.py"], cwd=repo,
                         capture_output=True, text=True,
                         env={**__import__("os").environ, "PATH": f"{shim}:{__import__('os').environ['PATH']}"})

    assert (repo / "src" / "prod.py").read_text() == "VALUE = 1\n"
    assert (repo / "src" / "added.py").exists()
    assert ran.returncode == 2, ran.stderr
    assert "partial restore" in ran.stderr
    assert "production" in ran.stderr and "untracked" in ran.stderr


@pytest.mark.process("restore-production.sh run outside any git repository in tmp_path")
def test_issue_2579_restore_production_does_not_claim_a_partial_restore_when_checkout_fails(tmp_path):
    outside = tmp_path / "not-a-repo"
    outside.mkdir()

    ran = subprocess.run(["sh", str(SCRIPTS / "restore-production.sh"), "test_new.py"], cwd=outside,
                         capture_output=True, text=True,
                         env={**__import__("os").environ, "GIT_CEILING_DIRECTORIES": str(tmp_path)})

    assert ran.returncode == 2, ran.stderr
    assert "partial restore" not in ran.stderr


@pytest.mark.process("restore-production.sh run against a real git repository in tmp_path")
def test_issue_2579_restore_production_leaves_a_dirty_ledger_and_graded_untouched(tmp_path):
    repo = tmp_path / "repo"
    (repo / ".tdd").mkdir(parents=True)
    (repo / "skills" / "tdd").mkdir(parents=True)
    git(repo, "init", "-q")
    (repo / ".tdd" / "issue-7.md").write_text("- [ ] step\n")
    (repo / "skills" / "tdd" / "GRADED").write_text("sig-1\n")
    (repo / "prod.py").write_text("VALUE = 1\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "base")
    (repo / ".tdd" / "issue-7.md").write_text("- [x] step\n")
    (repo / "skills" / "tdd" / "GRADED").write_text("sig-2\n")
    (repo / "prod.py").write_text("VALUE = 2\n")

    ran = subprocess.run(["sh", str(SCRIPTS / "restore-production.sh"), "test_new.py"], cwd=repo,
                         capture_output=True, text=True)

    assert (repo / "prod.py").read_text() == "VALUE = 1\n"
    assert (repo / ".tdd" / "issue-7.md").read_text() == "- [x] step\n"
    assert (repo / "skills" / "tdd" / "GRADED").read_text() == "sig-2\n"


@pytest.mark.process("restore-production.sh run against a real git repository in tmp_path")
def test_issue_2579_restore_production_refuses_a_pytest_node_id_with_exit_2_and_restores_nothing(tmp_path):
    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    git(repo, "init", "-q")
    (repo / "src" / "prod.py").write_text("VALUE = 1\n")
    (repo / "test_old.py").write_text("def test_old():\n    assert True\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "base")
    (repo / "test_old.py").write_text("def test_old():\n    assert False\n")
    (repo / "src" / "prod.py").write_text("VALUE = 2\n")
    (repo / "src" / "added.py").write_text("EXTRA = 1\n")

    ran = subprocess.run(["sh", str(SCRIPTS / "restore-production.sh"), "test_old.py::test_old"], cwd=repo,
                         capture_output=True, text=True)

    assert ran.returncode == 2, ran.stderr
    assert (repo / "test_old.py").read_text() == "def test_old():\n    assert False\n"
    assert (repo / "src" / "prod.py").read_text() == "VALUE = 2\n"
    assert (repo / "src" / "added.py").read_text() == "EXTRA = 1\n"


@pytest.mark.process("restore-production.sh run against a real git repository in tmp_path")
def test_issue_2579_restore_production_refuses_a_pathspec_magic_prefix_with_exit_2_and_restores_nothing(tmp_path):
    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    git(repo, "init", "-q")
    (repo / "src" / "prod.py").write_text("VALUE = 1\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "base")
    (repo / "src" / "prod.py").write_text("VALUE = 2\n")
    (repo / "src" / "added.py").write_text("EXTRA = 1\n")

    ran = subprocess.run(["sh", str(SCRIPTS / "restore-production.sh"), ":(bogus)x"], cwd=repo,
                         capture_output=True, text=True)

    assert ran.returncode == 2, ran.stderr
    assert (repo / "src" / "prod.py").read_text() == "VALUE = 2\n"
    assert (repo / "src" / "added.py").read_text() == "EXTRA = 1\n"


@pytest.mark.process("restore-production.sh run from a subdirectory of a real git repository in tmp_path")
def test_issue_2579_restore_production_from_a_subdirectory_restores_the_whole_worktree_or_refuses(tmp_path):
    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    (repo / "other").mkdir()
    git(repo, "init", "-q")
    (repo / "src" / "prod.py").write_text("VALUE = 1\n")
    (repo / "other" / "prod.py").write_text("VALUE = 1\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "base")
    (repo / "src" / "prod.py").write_text("VALUE = 2\n")
    (repo / "other" / "prod.py").write_text("VALUE = 2\n")

    ran = subprocess.run(["sh", str(SCRIPTS / "restore-production.sh"), "test_new.py"], cwd=repo / "src",
                         capture_output=True, text=True)

    assert ran.returncode == 2 or (repo / "other" / "prod.py").read_text() == "VALUE = 1\n", (
        "exit 0 but only the subtree was restored")


@pytest.mark.process("restore-production.sh run against a real git repository in tmp_path")
def test_issue_2579_restore_production_keeps_an_untracked_test_file_the_red_wrote_outside_the_named_path(tmp_path):
    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    (repo / "tests").mkdir()
    git(repo, "init", "-q")
    (repo / "src" / "prod.py").write_text("VALUE = 1\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "base")
    (repo / "tests" / "test_named.py").write_text("def test_named():\n    assert False\n")
    (repo / "tests" / "helper_scratch.py").write_text("HELPER = 1\n")
    (repo / "src" / "prod.py").write_text("VALUE = 2\n")

    ran = subprocess.run(["sh", str(SCRIPTS / "restore-production.sh"), "tests/test_named.py"], cwd=repo,
                         capture_output=True, text=True)

    assert ran.returncode == 0, ran.stderr
    assert (repo / "src" / "prod.py").read_text() == "VALUE = 1\n"
    assert (repo / "tests" / "helper_scratch.py").read_text() == "HELPER = 1\n"
