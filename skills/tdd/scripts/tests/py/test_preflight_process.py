"""Cases for veri/preflight.py that start a real process: detach-command.sh itself, not a fake of it."""
import importlib
import os
import subprocess

import pytest


@pytest.fixture
def detached(tmp_path, monkeypatch):
    """preflight.detached in a scratch run directory; every script it names is really run, and its argv kept in `.seen`."""
    preflight = importlib.import_module("veri.preflight")
    (tmp_path / ".tdd").mkdir()
    seen = []

    def run_script(name, *args, cwd=None, env=None):
        seen.append((os.path.basename(name), *args))
        proc = subprocess.run([name, *args], capture_output=True, text=True, cwd=cwd, env=env)
        return proc.returncode, proc.stdout, proc.stderr

    monkeypatch.setattr(preflight, "run_script", run_script)

    def call(name, cmd):
        return preflight.detached(name, cmd, str(tmp_path), dict(os.environ, VERI_POLL="0.05"))

    call.seen = seen
    return call


@pytest.mark.process("the real detach-command.sh, starting and waiting on a detached sh")
def test_a_tier_command_of_several_words_is_run_by_the_real_detach_command_and_its_output_is_recorded(tmp_path, detached):
    code = detached("probe", "sh -c 'echo two words'")

    tdd = tmp_path / ".tdd"
    assert (code, (tdd / "probe.exit").read_text().strip(), (tdd / "probe.out").read_text()) == (0, "0", "two words\n")
    assert detached.seen[0] == ("detach-command.sh", "start", "probe", "sh", "-c", "echo two words")


@pytest.mark.process("the real detach-command.sh, starting and waiting on a detached sh that fails")
def test_a_tier_command_that_fails_comes_back_non_zero_from_the_real_detach_command(tmp_path, detached):
    code = detached("red", "sh -c 'exit 7'")

    assert (code != 0, (tmp_path / ".tdd" / "red.exit").read_text().strip()) == (True, "7")
