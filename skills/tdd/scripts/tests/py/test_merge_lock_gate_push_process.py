"""merge-lock.sh gate around a rebased force-with-lease push, against a real local bare remote."""
import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2]
BRANCH = "tdd/feature"


def _git(cwd, *args):
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@e", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@e"}
    return subprocess.run(["git", "-c", "protocol.file.allow=always", *args], cwd=cwd, env=env,
                          stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=30)


def _rebased_clone(root):
    """A clone whose branch is rebased onto an advanced main; returns (clone, sha recorded before the rebase)."""
    bare = root / "origin.git"
    seed = root / "seed"
    clone = root / "clone"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(bare)], check=True, cwd=root)
    subprocess.run(["git", "clone", "-q", str(bare), str(seed)], check=True, cwd=root, stderr=subprocess.DEVNULL)
    (seed / "a").write_text("a\n")
    for step in (("add", "a"), ("commit", "-qm", "a"), ("push", "-q", "origin", "HEAD:main")):
        assert _git(seed, *step).returncode == 0
    subprocess.run(["git", "clone", "-q", str(bare), str(clone)], check=True, cwd=root, stderr=subprocess.DEVNULL)
    (clone / "f").write_text("f\n")
    for step in (("checkout", "-qb", BRANCH), ("add", "f"), ("commit", "-qm", "f"),
                 ("push", "-q", "origin", BRANCH)):
        assert _git(clone, *step).returncode == 0
    recorded = _git(clone, "rev-parse", "HEAD").stdout.strip()
    (seed / "b").write_text("b\n")
    for step in (("add", "b"), ("commit", "-qm", "b"), ("push", "-q", "origin", "HEAD:main")):
        assert _git(seed, *step).returncode == 0
    assert _git(clone, "fetch", "-q", "origin").returncode == 0
    assert _git(clone, "rebase", "-q", "origin/main").returncode == 0
    return clone, recorded


@pytest.mark.process("merge-lock.sh gate --keep around a real git push --force-with-lease to a local bare remote")
def test_3431_a_rebased_push_through_merge_lock_gate_is_accepted_exactly_as_the_same_push_run_directly(tmp_path):
    direct_root, gated_root = tmp_path / "direct", tmp_path / "gated"
    direct_root.mkdir()
    gated_root.mkdir()
    direct_clone, direct_sha = _rebased_clone(direct_root)
    gated_clone, gated_sha = _rebased_clone(gated_root)
    push = ["git", "-c", "protocol.file.allow=always", "push", "-q",
            "--force-with-lease={}:{}", "origin", BRANCH]

    def cmd(sha):
        return [part.format(BRANCH, sha) for part in push]

    direct = subprocess.run(cmd(direct_sha), cwd=direct_clone, stdin=subprocess.DEVNULL,
                            capture_output=True, text=True, timeout=30)
    pid = str(os.getpid())
    shim = ["/bin/sh", str(SCRIPTS / "merge-lock.sh")]
    taken = subprocess.run([*shim, "take", "--pid", pid], cwd=gated_clone, stdin=subprocess.DEVNULL,
                           capture_output=True, text=True, timeout=10)
    gated = subprocess.run([*shim, "gate", "--keep", "--pid", pid, "--owner", "tok", "--", *cmd(gated_sha)],
                           cwd=gated_clone, stdin=subprocess.DEVNULL, capture_output=True, text=True,
                           timeout=30)
    assert (taken.returncode, direct.returncode, gated.returncode) == (0, 0, 0), (
        f"direct stderr: {direct.stderr!r}\ngated stderr: {gated.stderr!r}")
    assert gated.stderr == direct.stderr
