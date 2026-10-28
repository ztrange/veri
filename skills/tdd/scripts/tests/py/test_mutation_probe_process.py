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
