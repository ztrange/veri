"""Cases for pin-fast-tier.sh that start the real entry point."""
import subprocess

import pytest

from conftest import SCRIPTS

CHECK = str(SCRIPTS / "pin-fast-tier.sh")


def stub(path, body):
    path.write_text("#!/bin/sh\n" + body)
    path.chmod(0o755)
    return str(path)


@pytest.mark.process("pin-fast-tier.sh run on a fast command that fails")
def test_a_failing_fast_command_exits_1_and_leaves_its_output_in_the_reason_file(tmp_path):
    (tmp_path / ".tdd").mkdir()
    fast = stub(tmp_path / "fast-red",
                "echo \"FAIL - a suite builds its own scratch instead of the harness's\"\necho '0 passed, 1 failed'\nexit 1\n")

    ran = subprocess.run([CHECK, fast], cwd=tmp_path, capture_output=True, text=True)

    reason = (tmp_path / ".tdd" / "verify-pin.reason").read_text()
    assert ran.returncode == 1
    assert "builds its own scratch instead of the harness's" in reason


@pytest.mark.process("pin-fast-tier.sh run with no argument")
def test_no_argument_prints_usage_on_stderr_and_exits_2_without_a_reason_file(tmp_path):
    ran = subprocess.run([CHECK], cwd=tmp_path, capture_output=True, text=True)

    assert ran.returncode == 2
    assert ran.stdout == ""
    assert "usage: pin-fast-tier.sh" in ran.stderr
    assert not (tmp_path / ".tdd" / "verify-pin.reason").exists()


@pytest.mark.process("pin-fast-tier.sh run on a fast command that passes")
def test_a_passing_fast_command_exits_0_silent_without_a_reason_file(tmp_path):
    fast = stub(tmp_path / "fast-green", "echo '0 failed'\nexit 0\n")

    ran = subprocess.run([CHECK, fast], cwd=tmp_path, capture_output=True, text=True)

    assert ran.returncode == 0
    assert ran.stdout + ran.stderr == ""
    assert not (tmp_path / ".tdd" / "verify-pin.reason").exists()


@pytest.mark.process("pin-fast-tier.sh and git run for real, from a subdirectory of a throwaway repo")
def test_pin_fast_tier_run_from_a_subdirectory_writes_the_reason_under_the_repo_root_1895(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    sub = tmp_path / "skills"
    sub.mkdir()
    fast = stub(tmp_path / "fast-red", "echo 'FAIL - a case'\nexit 1\n")

    ran = subprocess.run([CHECK, fast], cwd=sub, capture_output=True, text=True)

    assert ran.returncode == 1, ran.stderr
    assert ((tmp_path / ".tdd" / "verify-pin.reason").exists(), (sub / ".tdd").exists()) == (True, False)
