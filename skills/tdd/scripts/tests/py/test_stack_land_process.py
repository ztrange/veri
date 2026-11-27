"""Entry-point contract case for stack-land.sh (PRD 034.4a, #4317)."""
import importlib
import os
import subprocess

import pytest

from conftest import SCRIPTS
from repo_builder import git
from stub_script import write_stub


@pytest.mark.process("stack-land.sh's /bin/sh shim exec'd on the interpreter with a commit name for an argument")
def test_4317_any_argument_other_than_now_exits_2_with_the_usage_line(tmp_path):
    ran = subprocess.run([str(SCRIPTS / "stack-land.sh"), "abc1234"], cwd=tmp_path, stdin=subprocess.DEVNULL,
                         capture_output=True, text=True, timeout=60)

    assert (ran.returncode, ran.stdout, ran.stderr) == (2, "", "usage: stack-land.sh [--now]\n")


def _landed_world(tmp_path):
    """A main clone (`work`) of a bare origin whose stack holds two commits, the first landed on trunk: (work, the cut).
    origin answers `work`'s first call (stack-branch.sh's ls-remote) and hangs on every later one, the carry's fetch:
    its upload-pack sleeps first."""
    origin, author, work = tmp_path / "origin.git", tmp_path / "author", tmp_path / "work"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "trunk", str(origin)], cwd=tmp_path, check=True)
    subprocess.run(["git", "init", "-q", "-b", "trunk", str(author)], cwd=tmp_path, check=True)
    (author / "CLAUDE.md").write_text("veri: stack branch: stack\n")
    (author / ".gitignore").write_text(".tdd/\n")
    git(author, "add", "-A")
    git(author, "commit", "-q", "-m", "docs: the base (#1)")
    git(author, "checkout", "-q", "-b", "stack")
    for n in (1, 2):
        (author / ("s%d.txt" % n)).write_text("stack %d\n" % n)
        git(author, "add", "-A")
        git(author, "commit", "-q", "-m", "feat: s%d (#%d)" % (n, 10 + n))
    git(author, "remote", "add", "origin", str(origin))
    git(author, "push", "-q", "origin", "stack", "stack~1:refs/heads/trunk")
    subprocess.run(["git", "clone", "-q", str(origin), str(work)], cwd=tmp_path, check=True)
    pack = write_stub(str(tmp_path / "upload-pack"), 'served="$(dirname "$0")/served"\n[ -e "$served" ] && sleep 30\n'
                      ': > "$served"\nexec git-upload-pack "$@"\n')
    git(work, "config", "remote.origin.uploadpack", pack)
    return work, git(work, "rev-parse", "origin/stack~1")


@pytest.mark.process("stack-carry.sh and merge-lock.sh run as their /bin/sh shims, from stack-land's post-landing step"
                     " run in-process, in a real clone of a local bare origin whose upload-pack hangs")
@pytest.mark.timeout(90)
def test_4318_a_carry_over_whose_fetch_hangs_past_the_network_bound_leaves_no_merge_lock_held(
        tmp_path, monkeypatch, capfd):
    work, cut = _landed_world(tmp_path)
    monkeypatch.chdir(work)
    monkeypatch.setenv("VERI_GIT_NETWORK_TIMEOUT", "2")
    stack_fix = importlib.import_module("veri.stack_fix")
    real = stack_fix.script
    monkeypatch.setattr(stack_fix, "script", lambda name, *args, **kwargs: (
        (0, "") if name == "stack-tag.sh" else real(name, *args, **kwargs)))
    url = "https://github.com/owner/repo/pull/90"

    code = importlib.import_module("veri.stack_land")._after(url, cut, "owner/repo", [])

    lock = str(SCRIPTS / "merge-lock.sh")
    holder = subprocess.run([lock, "holder"], cwd=work, stdin=subprocess.DEVNULL, capture_output=True, text=True,
                            timeout=60)
    taken = subprocess.run([lock, "take", "--pid", str(os.getpid())], cwd=work, stdin=subprocess.DEVNULL,
                           capture_output=True, text=True, timeout=60)
    subprocess.run([lock, "release", "--pid", str(os.getpid())], cwd=work, stdin=subprocess.DEVNULL,
                   capture_output=True, timeout=60)
    err = capfd.readouterr().err
    assert (code, "owed: stack-carry.sh " + cut in err, holder.returncode, taken.returncode) == (2, True, 3, 0), (
        err, holder.stdout, taken.stderr)
