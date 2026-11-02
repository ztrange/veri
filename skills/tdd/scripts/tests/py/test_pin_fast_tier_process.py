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


@pytest.mark.process("pin-fast-tier.sh run on a fast command whose passing noise dwarfs its one failure")
def test_a_noisy_failing_fast_command_leaves_a_bounded_reason_file_with_its_fail_block_2882(tmp_path):
    (tmp_path / ".tdd").mkdir()
    fast = stub(tmp_path / "fast-noisy",
                "i=0\nwhile [ $i -lt 20000 ]; do\n"
                "echo \"    at passing-noise-frame-$i (src/component.tsx:$i:10) padding padding padding padding padding padding\"\n"
                "i=$((i+1))\ndone\n"
                "echo ' FAIL  src/widget.test.ts > widget > renders the unique-failure-marker'\n"
                "echo '  AssertionError: expected 1 to be 2'\nexit 1\n")

    ran = subprocess.run([CHECK, fast], cwd=tmp_path, capture_output=True, text=True)

    reason = (tmp_path / ".tdd" / "verify-pin.reason").read_bytes()
    assert ran.returncode == 1
    assert len(reason) < 512 * 1024
    assert b"unique-failure-marker" in reason
    assert b"AssertionError: expected 1 to be 2" in reason


@pytest.mark.process("pin-fast-tier.sh run on a failure followed by far more passing noise than the bound, and on a small output")
def test_a_noisy_reason_keeps_a_fail_block_that_lies_before_the_tail_and_a_small_one_is_unchanged_2882(tmp_path):
    (tmp_path / ".tdd").mkdir()
    noisy = stub(tmp_path / "fast-noisy-suffix",
                 "echo ' FAIL  src/early.test.ts > early > early-failure-marker'\n"
                 "echo '  early-detail-line: expected 1 to be 2'\n"
                 "i=0\nwhile [ $i -lt 20000 ]; do\n"
                 "echo \"    at passing-noise-frame-$i (src/component.tsx:$i:10) padding padding padding padding padding\"\n"
                 "i=$((i+1))\ndone\nexit 1\n")
    small = stub(tmp_path / "fast-small",
                 "echo ' FAIL  src/s.test.ts > small-failure-marker'\necho '  small-detail-line'\necho '1 failed'\nexit 1\n")
    reason_file = tmp_path / ".tdd" / "verify-pin.reason"

    subprocess.run([CHECK, noisy], cwd=tmp_path, capture_output=True, text=True)
    noisy_reason = reason_file.read_bytes()
    subprocess.run([CHECK, small], cwd=tmp_path, capture_output=True, text=True)
    small_reason = reason_file.read_bytes()

    assert len(noisy_reason) < 512 * 1024
    assert b"early-failure-marker" in noisy_reason
    assert b"early-detail-line: expected 1 to be 2" in noisy_reason
    assert small_reason == (b" FAIL  src/s.test.ts > small-failure-marker\n  small-detail-line\n1 failed\n")
