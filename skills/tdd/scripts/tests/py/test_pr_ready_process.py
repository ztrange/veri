"""Cases for pr-ready.sh that start the real entry point, from zsh as a conductor's shell may be (#2147)."""
import os
import shutil
import subprocess

import pytest

from conftest import SCRIPTS


def run_from_zsh(tmp_path, gh_body, command):
    """(completed process, gh calls) of zsh -c <command>, with "$1" the real pr-ready.sh and an
    executable gh running <gh_body> first on PATH."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    calls = tmp_path / "calls"
    calls.write_text("")
    gh = bin_dir / "gh"
    gh.write_text('#!/bin/sh\necho "gh $*" >> "$CALLS"\n' + gh_body)
    gh.chmod(0o755)
    env = {"PATH": os.pathsep.join([str(bin_dir), os.path.dirname(shutil.which("bash")), "/usr/bin", "/bin"]),
           "CALLS": str(calls), "VERI_GH_DRIVER": "auto", "VERI_POLL": "0"}
    ran = subprocess.run(["zsh", "-c", command, "zsh", str(SCRIPTS / "pr-ready.sh")],
                         capture_output=True, text=True, env=env)
    return ran, calls.read_text().splitlines()


@pytest.mark.skipif(shutil.which("zsh") is None, reason="no zsh installed")
@pytest.mark.process("zsh -c runs pr-ready.sh, a /bin/sh shim over veri/pr_ready.py")
def test_issue_2147_pr_ready_script_marks_a_draft_ready_from_zsh_and_is_listed_with_its_caller(tmp_path):
    ready, calls = run_from_zsh(tmp_path, '[ "$1" = api ] && echo abc123\nexit 0\n', '"$1" 42 abc123')
    (tmp_path / "bare").mkdir()
    bare, _ = run_from_zsh(tmp_path / "bare", "exit 0\n", '"$1"')
    listed = [line for line in (SCRIPTS.parent / "SCRIPTS.md").read_text().splitlines()
              if line.startswith("- `$S/pr-ready.sh")]

    assert (ready.returncode, ready.stdout, ready.stderr) == (0, "", "")
    assert "gh pr ready 42" in calls
    assert bare.returncode == 2 and "usage" in bare.stderr.lower()
    assert len(listed) == 1 and "conductor" in listed[0]


@pytest.mark.skipif(shutil.which("zsh") is None, reason="no zsh installed")
@pytest.mark.process("zsh -c runs pr-ready.sh, a /bin/sh shim over veri/pr_ready.py")
def test_issue_2147_pr_ready_script_run_from_zsh_exits_2_when_github_answers_on_no_route(tmp_path):
    refused, calls = run_from_zsh(tmp_path, 'case "$*" in *--jq*) echo abc123; exit 0 ;; esac\nexit 1\n',
                                  '"$1" 42 abc123')

    assert refused.returncode == 2, (refused.stdout, refused.stderr)
    assert "gh pr ready 42" in calls


@pytest.mark.process("real git repository and bare remote holding the sha, a fake gh, and pr-ready.sh as a subprocess")
def test_issue_2858_pr_ready_keeps_polling_while_the_remote_holds_the_sha_and_readies_once_the_head_matches(tmp_path):
    git_env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
               "GIT_COMMITTER_EMAIL": "t@t", "PATH": "/usr/bin:/bin:" + os.path.dirname(shutil.which("git"))}

    def git(*args, cwd):
        return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True,
                              env=git_env).stdout.strip()

    bare, repo = tmp_path / "bare.git", tmp_path / "repo"
    repo.mkdir()
    git("init", "-q", "--bare", str(bare), cwd=tmp_path)
    git("init", "-q", "-b", "feature", cwd=repo)
    git("commit", "-q", "--allow-empty", "-m", "old", cwd=repo)
    old = git("rev-parse", "HEAD", cwd=repo)
    git("commit", "-q", "--allow-empty", "-m", "new", cwd=repo)
    new = git("rev-parse", "HEAD", cwd=repo)
    git("remote", "add", "origin", str(bare), cwd=repo)
    git("push", "-q", "origin", "feature", cwd=repo)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    heads = tmp_path / "heads"
    heads.write_text("%s\n%s\n%s\n" % (old, old, new))
    calls = tmp_path / "calls"
    calls.write_text("")
    gh = bin_dir / "gh"
    gh.write_text('#!/bin/sh\necho "gh $*" >> "$CALLS"\n'
                  'case "$*" in\n'
                  '  *head.ref*) echo feature ;;\n'
                  '  *--jq*) head -n 1 "$HEADS"; sed 1d "$HEADS" > "$HEADS.next"; mv "$HEADS.next" "$HEADS" ;;\n'
                  'esac\nexit 0\n')
    gh.chmod(0o755)
    env = {"PATH": os.pathsep.join([str(bin_dir), os.path.dirname(shutil.which("bash")), "/usr/bin", "/bin"]),
           "CALLS": str(calls), "HEADS": str(heads), "VERI_GH_DRIVER": "auto", "VERI_POLL": "0"}

    ran = subprocess.run([str(SCRIPTS / "pr-ready.sh"), "42", new], cwd=repo, capture_output=True, text=True,
                         env=env, timeout=20)

    reads = [c for c in calls.read_text().splitlines() if "head.sha" in c]
    assert (ran.returncode, ran.stderr) == (0, "")
    assert len(reads) == 3
    assert "gh pr ready 42" in calls.read_text().splitlines()


@pytest.mark.process("real git repository whose origin is unreachable, a fake gh, and pr-ready.sh as a subprocess")
def test_issue_2858_pr_ready_falls_through_to_the_poll_and_exits_2_when_the_origin_cannot_be_asked(tmp_path):
    git_env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
               "GIT_COMMITTER_EMAIL": "t@t", "PATH": "/usr/bin:/bin:" + os.path.dirname(shutil.which("git"))}

    def git(*args):
        return subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True, text=True,
                              env=git_env).stdout.strip()

    git("init", "-q", "-b", "feature")
    git("commit", "-q", "--allow-empty", "-m", "old")
    old = git("rev-parse", "HEAD")
    git("commit", "-q", "--allow-empty", "-m", "new")
    new = git("rev-parse", "HEAD")
    git("remote", "add", "origin", str(tmp_path / "no-such-remote.git"))
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text('#!/bin/sh\ncase "$*" in\n  *head.ref*) echo feature ;;\n  *--jq*) echo %s ;;\nesac\nexit 0\n' % old)
    gh.chmod(0o755)
    env = {"PATH": os.pathsep.join([str(bin_dir), os.path.dirname(shutil.which("bash")), "/usr/bin", "/bin"]),
           "VERI_GH_DRIVER": "auto", "VERI_POLL": "0"}

    ran = subprocess.run([str(SCRIPTS / "pr-ready.sh"), "42", new], cwd=tmp_path, capture_output=True, text=True,
                         env=env, timeout=20)

    assert ran.returncode == 2, (ran.stdout, ran.stderr)
    assert "PR 42 head is %s after 30 reads, expected %s" % (old, new) in ran.stderr
