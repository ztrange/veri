"""The throwaway git repositories repo_builder builds for process cases, read back with real git."""
import subprocess

import pytest

import repo_builder


def run(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


@pytest.mark.process("git init in a scratch directory, read back with git symbolic-ref")
def test_new_repo_makes_the_missing_directories_and_a_repository_on_main_and_returns_the_path(tmp_path):
    path = tmp_path / "deep" / "er" / "repo"

    built = repo_builder.new_repo(path)

    assert built == path
    assert run(path, "symbolic-ref", "--short", "HEAD").stdout.strip() == "main"
    assert run(path, "rev-parse", "--show-toplevel").stdout.strip() == str(path.resolve())


@pytest.mark.process("git init in a scratch directory, read back with git symbolic-ref")
def test_new_repo_given_a_branch_starts_the_repository_on_it(tmp_path):
    repo_builder.new_repo(tmp_path / "repo", branch="trunk")

    assert run(tmp_path / "repo", "symbolic-ref", "--short", "HEAD").stdout.strip() == "trunk"


@pytest.mark.process("git init in a directory that already holds a file")
def test_new_repo_in_a_directory_that_exists_keeps_what_is_in_it(tmp_path):
    (tmp_path / "planted.txt").write_text("kept\n")

    repo_builder.new_repo(tmp_path)

    assert (tmp_path / "planted.txt").read_text() == "kept\n"
    assert run(tmp_path, "rev-parse", "--git-dir").stdout.strip() == ".git"


@pytest.mark.process("git init in a scratch directory, config read back with git config")
def test_new_repo_sets_no_identity_in_the_repository_so_a_case_can_prove_a_commit_without_one(tmp_path):
    repo = repo_builder.new_repo(tmp_path / "repo")

    assert run(repo, "config", "--local", "--get", "user.name").returncode == 1


@pytest.mark.process("git add and commit in a scratch repository, read back with git log")
def test_commit_all_writes_each_file_commits_them_under_the_message_and_returns_the_new_head(tmp_path):
    repo = repo_builder.new_repo(tmp_path / "repo")

    sha = repo_builder.commit_all(repo, "feat: two files", top="one\n", src__nested__deep="two\n")

    assert sha == run(repo, "rev-parse", "HEAD").stdout.strip()
    assert run(repo, "log", "-1", "--format=%s|%an|%ae").stdout.strip() == "feat: two files|veri|veri@example.test"
    assert run(repo, "show", "HEAD:src/nested/deep").stdout == "two\n"
    assert run(repo, "show", "HEAD:top").stdout == "one\n"


@pytest.mark.process("git add -A and commit in a scratch repository, read back with git show")
def test_commit_all_with_no_files_commits_the_edits_and_deletions_already_in_the_tree(tmp_path):
    repo = repo_builder.new_repo(tmp_path / "repo")
    repo_builder.commit_all(repo, "feat: first", kept="a\n", gone="b\n")
    (repo / "kept").write_text("a2\n")
    (repo / "gone").unlink()

    repo_builder.commit_all(repo, "chore: edit and delete")

    assert run(repo, "show", "--name-status", "--format=", "HEAD").stdout.split() == ["D", "gone", "M", "kept"]


@pytest.mark.process("git commit with nothing to commit in a scratch repository")
def test_commit_all_with_nothing_to_commit_fails_naming_what_git_said(tmp_path):
    repo = repo_builder.new_repo(tmp_path / "repo")
    repo_builder.commit_all(repo, "feat: first", kept="a\n")

    with pytest.raises(AssertionError, match="nothing to commit"):
        repo_builder.commit_all(repo, "chore: empty")


@pytest.mark.process("an empty commit in a scratch repository, read back with rev-parse and show")
def test_commit_all_allowing_empty_commits_a_tree_with_nothing_to_commit_and_returns_its_head(tmp_path):
    repo = repo_builder.new_repo(tmp_path / "repo")
    first = repo_builder.commit_all(repo, "feat: first", kept="a\n")

    empty = repo_builder.commit_all(repo, "chore: empty", allow_empty=True)

    assert empty != first
    assert empty == run(repo, "rev-parse", "HEAD").stdout.strip()
    assert run(repo, "show", "--name-status", "--format=%s", "HEAD").stdout.split() == ["chore:", "empty"]


@pytest.mark.process("git init for a worker's first repository, then a second new_repo watched through repo_builder.git")
def test_a_second_new_repo_in_one_worker_makes_its_repository_without_an_init_call(tmp_path, monkeypatch):
    repo_builder.new_repo(tmp_path / "first")
    calls = []
    real_git = repo_builder.git

    def spy(repo, *args):
        calls.append(args)
        return real_git(repo, *args)

    monkeypatch.setattr(repo_builder, "git", spy)
    repo_builder.new_repo(tmp_path / "second")

    assert [args for args in calls if "init" in args] == []
    assert run(tmp_path / "second", "symbolic-ref", "--short", "HEAD").stdout.strip() == "main"


@pytest.mark.process("git init for a worker's first template, then the repositories new_repo copies read back with git")
def test_a_workers_first_and_second_new_repo_each_return_what_git_init_makes_on_the_branch(tmp_path, monkeypatch):
    monkeypatch.setattr(repo_builder, "TEMPLATE_ROOT", tmp_path / "fresh-worker-templates")

    for name in ("first", "second"):
        repo = repo_builder.new_repo(tmp_path / name, branch="trunk")

        assert run(repo, "symbolic-ref", "--short", "HEAD").stdout.strip() == "trunk", name
        assert run(repo, "rev-parse", "--verify", "-q", "HEAD").returncode == 1, f"{name} has a commit"
        assert run(repo, "config", "--local", "--get-regexp", "^user\\.").returncode == 1, f"{name} has an identity"
        assert run(repo, "status", "--porcelain").stdout == "", name
