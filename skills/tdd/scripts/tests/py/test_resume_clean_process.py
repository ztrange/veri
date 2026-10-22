"""Cases for veri/resume_clean.py that start a real process."""
import importlib
import subprocess

import pytest


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.com", *args],
                          check=True, stdout=subprocess.PIPE, text=True).stdout


@pytest.mark.process("git")
def test_main_discards_an_untracked_file_and_a_modified_tracked_file_listing_each_and_leaves_tdd_untouched_1967(
        tmp_path, run_cli):
    resume_clean = importlib.import_module("veri.resume_clean")
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    (repo / ".gitignore").write_text(".tdd/*.log\n")
    (repo / "file.txt").write_text("one\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "base")
    (repo / "file.txt").write_text("two\n")
    (repo / "other.txt").write_text("stray\n")
    (repo / ".tdd").mkdir()
    (repo / ".tdd" / "leaf.log").write_text("log\n")
    (repo / ".tdd" / "issue-1-refactor-owed.md").write_text("owed\n")

    code, out, err = run_cli(resume_clean, [], cwd=repo)

    assert (code, sorted(out.splitlines()), err) == (0, ["?? other.txt", " M file.txt"][::-1], "")
    assert git(repo, "status", "--porcelain", "--", ":!.tdd").strip() == ""
    assert (repo / "file.txt").read_text() == "one\n"
    assert not (repo / "other.txt").exists()
    assert (repo / ".tdd" / "leaf.log").read_text() == "log\n"
    assert (repo / ".tdd" / "issue-1-refactor-owed.md").read_text() == "owed\n"
