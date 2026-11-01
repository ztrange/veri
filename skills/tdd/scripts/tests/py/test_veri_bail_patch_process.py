"""Cases for the vbail skill's save and restore of a leaf's uncommitted edit that start a real process."""
import hashlib
import subprocess

import pytest


def git(repo, *words):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=repo,
                          check=True, capture_output=True).stdout


@pytest.mark.process("git")
def test_a_saved_binary_patch_restores_a_tracked_and_an_untracked_binary_edit_with_matching_hashes_2205(tmp_path):
    repo = tmp_path / "wt"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "tracked.bin").write_bytes(bytes(range(256)))
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "base")
    tracked = bytes(reversed(range(256))) + b"\x00\xff\x00"
    untracked = b"\x89PNG\r\n\x1a\n\x00\x00\xff\xfe" * 7
    (repo / "tracked.bin").write_bytes(tracked)
    (repo / "new.bin").write_bytes(untracked)
    (repo / ".tdd").mkdir()

    git(repo, "add", "-A")
    (repo / ".tdd" / "leaf.patch").write_bytes(git(repo, "diff", "--cached", "--binary", "HEAD"))
    git(repo, "reset", "-q", "--hard")
    git(repo, "clean", "-fdq")
    assert not (repo / "new.bin").exists()
    git(repo, "apply", ".tdd/leaf.patch")

    assert (hashlib.sha256((repo / "tracked.bin").read_bytes()).hexdigest(),
            hashlib.sha256((repo / "new.bin").read_bytes()).hexdigest()) == (
        hashlib.sha256(tracked).hexdigest(), hashlib.sha256(untracked).hexdigest())
