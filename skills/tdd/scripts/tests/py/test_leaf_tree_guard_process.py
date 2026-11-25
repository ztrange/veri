"""Cases for veri/leaf_tree_guard.py against a real repository: the fakes in test_verify.py pin the argv
verify's guard runs, these pin that git answers the way the guard reads it."""
import importlib
import os
import subprocess

import pytest


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.com", *args],
                          check=True, stdout=subprocess.PIPE, text=True).stdout.strip()


@pytest.fixture
def repo(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    (repo / ".tdd").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    (repo / "a.txt").write_text("one\n")
    (repo / "run.sh").write_text("echo hi\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "first")
    home = tmp_path / "home"
    home.mkdir()
    (home / ".gitconfig").write_text("[user]\n\tname = t\n")
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.chdir(repo)
    return repo


def guard_module():
    return importlib.import_module("veri.leaf_tree_guard")


@pytest.mark.process("git")
def test_an_unchanged_repository_has_no_changes(repo):
    guard = guard_module().snapshot()

    assert (bool(guard.tree), guard.changes()) == (True, None)


@pytest.mark.process("git")
@pytest.mark.parametrize("change, paths", [
    (lambda repo: (repo / "a.txt").write_text("two\n"), ["a.txt"]),
    (lambda repo: (repo / "new.txt").write_text("new\n"), ["new.txt"]),
    (lambda repo: git(repo, "commit", "-q", "--allow-empty", "-m", "moved"), ["HEAD"]),
], ids=["tracked-edit", "file-added", "head-moved"])
def test_a_change_to_the_tree_or_head_is_reported_by_path_with_head_last(repo, change, paths):
    module = guard_module()
    guard = module.snapshot()
    change(repo)

    found = guard.changes()

    assert (type(found).__name__, found.paths, found.before == guard.tree) == ("Changed", paths, True)


@pytest.mark.process("git")
def test_a_mode_only_flip_is_put_back_on_the_spot_and_not_reported(repo):
    guard = guard_module().snapshot()
    os.chmod(repo / "run.sh", 0o755)

    assert (guard.changes(), os.stat(repo / "run.sh").st_mode & 0o777) == (None, 0o644)


@pytest.mark.process("git")
def test_a_changed_global_git_config_is_reported_by_its_path(repo):
    module = guard_module()
    guard = module.snapshot()
    config = os.environ["HOME"] + "/.gitconfig"
    with open(config, "a") as f:
        f.write("[core]\n\tpager = cat\n")

    found = guard.changes()

    assert (type(found).__name__, found.path) == ("ConfigChanged", config)


@pytest.mark.process("git")
def test_an_unreadable_global_git_config_is_reported_with_its_error(repo):
    config = os.environ["HOME"] + "/.gitconfig"
    os.replace(config, config + ".kept")
    os.mkdir(config)

    found = guard_module().snapshot()

    assert (type(found).__name__, found.path, found.strerror) == ("ConfigUnreadable", config, "Is a directory")


@pytest.mark.process("git")
def test_restore_puts_back_an_edit_an_added_file_and_a_moved_head(repo):
    guard = guard_module().snapshot()
    head = git(repo, "rev-parse", "HEAD")
    (repo / "a.txt").write_text("two\n")
    (repo / "new.txt").write_text("new\n")
    git(repo, "commit", "-q", "--allow-empty", "-m", "moved")
    found = guard.changes()

    restored = guard.restore(found)

    assert (restored, (repo / "a.txt").read_text(), (repo / "new.txt").exists(), git(repo, "rev-parse", "HEAD"),
            guard.changes()) == (True, "one\n", False, head, None)
