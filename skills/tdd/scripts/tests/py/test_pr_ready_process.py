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
