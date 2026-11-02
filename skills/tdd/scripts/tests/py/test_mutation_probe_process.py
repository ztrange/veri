"""Medium cases for mutation-probe.sh: the shim and the command it runs, started for real."""
import os
import signal
import subprocess
import time
from pathlib import Path

import pytest

PROBE = Path(__file__).resolve().parents[2] / "mutation-probe.sh"


@pytest.mark.process("mutation-probe.sh and the sh command it runs against the edited fixture")
def test_command_sees_the_edited_content_and_a_failing_command_exits_0(tmp_path):
    target = tmp_path / "target.txt"
    target.write_text("keep alpha keep\n")
    witness = tmp_path / "witness.txt"
    result = subprocess.run(
        [str(PROBE), str(target), "alpha", "beta", "--", "sh", "-c", 'cp "$1" "$2"; exit 1', "sh", str(target), str(witness)],
        capture_output=True, text=True, timeout=20)
    assert (result.returncode, witness.read_text() if witness.exists() else None) == (0, "keep beta keep\n"), result.stderr


@pytest.mark.process("git, mutation-probe.sh and the sh command it runs, sent SIGTERM midway")
def test_probe_sent_sigterm_while_the_command_runs_restores_the_file_and_leaves_git_status_empty(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout
    git("init", "-q")
    target = tmp_path / "target.txt"
    target.write_text("keep alpha keep\n")
    git("add", "target.txt")
    git("commit", "-q", "-m", "fixture")
    started = tmp_path.parent / (tmp_path.name + "-started")
    probe = subprocess.Popen([str(PROBE), str(target), "alpha", "beta", "--", "sh", "-c", 'echo $$ > "$1"; exec sleep 20', "sh", str(started)],
                             cwd=tmp_path, stderr=subprocess.PIPE, text=True)
    try:
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline and not (started.exists() and started.read_text().endswith("\n")):
            time.sleep(0.02)
        assert started.exists(), "the command never started"
        probe.send_signal(signal.SIGTERM)
        probe.wait(timeout=10)
    finally:
        if started.exists() and started.read_text().strip().isdigit():
            try:
                os.kill(int(started.read_text()), signal.SIGKILL)
            except ProcessLookupError:
                pass
        if probe.poll() is None:
            probe.kill()
            probe.wait()
    assert (target.read_text(), git("status", "--porcelain")) == ("keep alpha keep\n", "")


@pytest.mark.process("git, mutation-probe.sh --before and the sh command it runs against a scratch repo")
def test_issue_2900_before_state_probe_exits_1_when_the_test_stays_green_on_the_branch_point_and_leaves_the_tree_unchanged(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout
    git("init", "-q")
    (tmp_path / "view.txt").write_text("view\n")
    (tmp_path / "quote.txt").write_text("0\n")
    git("add", ".")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD").strip()
    (tmp_path / "quote.txt").write_text("10\n")
    (tmp_path / "test.sh").write_text("grep -q view view.txt\n")
    git("add", ".")
    git("commit", "-q", "-m", "feature")
    scratch = tmp_path / "scratch.txt"
    scratch.write_text("untracked\n")
    result = subprocess.run([str(PROBE), "--before", base, "--keep", "test.sh", "--", "sh", "test.sh"],
                            cwd=tmp_path, capture_output=True, text=True, timeout=20)
    tree = {name: (tmp_path / name).read_text() for name in ("view.txt", "quote.txt", "test.sh", "scratch.txt")}
    assert (result.returncode, tree, git("status", "--porcelain")) == (
        1, {"view.txt": "view\n", "quote.txt": "10\n", "test.sh": "grep -q view view.txt\n", "scratch.txt": "untracked\n"},
        "?? scratch.txt\n"), result.stderr


@pytest.mark.process("git, mutation-probe.sh --before and the sh command it runs against a scratch repo")
def test_issue_2900_before_state_probe_runs_the_kept_file_as_it_is_and_exits_0_when_that_command_fails(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout
    git("init", "-q")
    (tmp_path / "quote.txt").write_text("0\n")
    git("add", ".")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD").strip()
    (tmp_path / "quote.txt").write_text("10\n")
    (tmp_path / "test.sh").write_text("exit 1\n")
    git("add", ".")
    git("commit", "-q", "-m", "feature")
    result = subprocess.run([str(PROBE), "--before", base, "--keep", "test.sh", "--", "sh", "test.sh"],
                            cwd=tmp_path, capture_output=True, text=True, timeout=20)
    assert (result.returncode, (tmp_path / "test.sh").read_text()) == (0, "exit 1\n"), result.stderr


@pytest.mark.process("git, mutation-probe.sh --before and the sh command it runs against a scratch repo")
def test_issue_2900_before_state_probe_leaves_a_kept_file_that_differs_from_the_sha_as_it_is_in_the_working_tree(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout
    git("init", "-q")
    (tmp_path / "quote.txt").write_text("0\n")
    (tmp_path / "test.sh").write_text("exit 0\n")
    git("add", ".")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD").strip()
    (tmp_path / "quote.txt").write_text("10\n")
    (tmp_path / "test.sh").write_text("exit 1\n")
    git("add", ".")
    git("commit", "-q", "-m", "feature")
    result = subprocess.run([str(PROBE), "--before", base, "--keep", "test.sh", "--", "sh", "test.sh"],
                            cwd=tmp_path, capture_output=True, text=True, timeout=20)
    assert (result.returncode, (tmp_path / "test.sh").read_text()) == (0, "exit 1\n"), result.stderr
