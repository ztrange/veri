"""Cases for pin-fast-tier.sh that start the real entry point."""
import os
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


@pytest.mark.process("pin-fast-tier.sh run on a failing fast command whose output is exactly the bound")
def test_a_failing_fast_command_with_output_exactly_at_the_bound_leaves_it_unchanged_in_the_reason_file_2909(tmp_path):
    (tmp_path / ".tdd").mkdir()
    fast = stub(tmp_path / "fast-at-bound",
                "i=0\nwhile [ $i -lt 127 ]; do\n"
                "printf 'ok %01020d\\n' 0\n"
                "i=$((i+1))\ndone\n"
                "printf 'ok %01021d' 0\nexit 1\n")
    output = (b"ok " + b"0" * 1020 + b"\n") * 127 + b"ok " + b"0" * 1021

    ran = subprocess.run([CHECK, fast], cwd=tmp_path, capture_output=True, text=True)

    reason = (tmp_path / ".tdd" / "verify-pin.reason").read_bytes()
    assert ran.returncode == 1
    assert len(output) == 128 * 1024
    assert reason == output + b"\n"


@pytest.mark.process("pin-fast-tier.sh, build-develop-prompt.sh and run-leaf.sh chained, with a stub claude")
def test_a_reason_file_at_the_bound_builds_a_revise_prompt_run_leaf_launches_under_arg_max_2882(tmp_path):
    (tmp_path / ".tdd").mkdir()
    arg_max = os.sysconf("SC_ARG_MAX")
    fast = stub(tmp_path / "fast-noisy",
                f"yes '    at passing-noise-frame (src/component.tsx:1:10) padding padding' | head -c {2 * arg_max}\n"
                "echo\necho ' FAIL  src/widget.test.ts > widget > renders'\nexit 1\n")
    claude = stub(tmp_path / "claude", "echo '{\"type\":\"result\",\"result\":\"ok\"}'\n: > \"$STUB_RAN\"\n")
    spec = tmp_path / "spec.md"
    spec.write_text("## Problem\nA bug.\n")
    prompt_file = tmp_path / "revise.prompt"
    env = {**os.environ, "CLAUDE_BIN": claude, "STUB_RAN": str(tmp_path / "ran"), "VERI_ISSUE": "3123"}

    subprocess.run([CHECK, fast], cwd=tmp_path, capture_output=True)
    built = subprocess.run([str(SCRIPTS / "build-develop-prompt.sh"), "revise", "red", str(spec), "step", "make unit",
                            str(tmp_path / ".tdd" / "verify-pin.reason")],
                           cwd=tmp_path, capture_output=True, env=env)
    prompt_file.write_bytes(built.stdout)
    launched = subprocess.run([str(SCRIPTS / "run-leaf.sh"), str(prompt_file)], cwd=tmp_path,
                              capture_output=True, env=env)

    assert built.returncode == 0, built.stderr
    assert prompt_file.stat().st_size < arg_max
    assert (launched.returncode, (tmp_path / "ran").exists()) == (0, True), launched.stderr


@pytest.mark.process("pin-fast-tier.sh run on a failing fast command whose output exceeds the bound and has no FAIL line")
def test_output_over_the_bound_with_no_fail_line_leaves_its_last_line_in_the_reason_file_2909(tmp_path):
    (tmp_path / ".tdd").mkdir()
    fast = stub(tmp_path / "fast-no-fail-marker",
                "i=0\nwhile [ $i -lt 20000 ]; do\n"
                "echo \"    lint-noise-line-$i padding padding padding padding padding padding\"\n"
                "i=$((i+1))\ndone\n"
                "echo 'error: unique-final-tail-marker'\nexit 1\n")

    ran = subprocess.run([CHECK, fast], cwd=tmp_path, capture_output=True, text=True)

    reason = (tmp_path / ".tdd" / "verify-pin.reason").read_bytes()
    assert ran.returncode == 1
    assert reason.strip() != b""
    assert b"error: unique-final-tail-marker" in reason


@pytest.mark.process("pin-fast-tier.sh run on a failing fast command printing far more than the bound, every line a FAIL line")
def test_output_of_many_fail_lines_over_the_bound_leaves_a_reason_file_under_the_cap_2909(tmp_path):
    from pin_fast_tier import BOUND_BYTES

    (tmp_path / ".tdd").mkdir()
    fast = stub(tmp_path / "fast-all-fail",
                "i=0\nwhile [ $i -lt 20000 ]; do\n"
                "echo \" FAIL  src/case-$i.test.ts > case $i padding padding padding\"\n"
                "i=$((i+1))\ndone\n"
                "echo 'error: unique-final-tail-marker'\nexit 1\n")

    ran = subprocess.run([CHECK, fast], cwd=tmp_path, capture_output=True, text=True)

    reason = (tmp_path / ".tdd" / "verify-pin.reason").read_bytes()
    assert ran.returncode == 1
    assert len(reason) < 2 * BOUND_BYTES
    assert b"error: unique-final-tail-marker" in reason


@pytest.mark.process("pin-fast-tier.sh run on failing fast commands whose output is one multi-MB line, with and without FAIL")
def test_a_single_line_longer_than_the_bound_leaves_a_reason_file_of_at_most_the_bound_bytes_2909(tmp_path):
    from pin_fast_tier import BOUND_BYTES

    (tmp_path / ".tdd").mkdir()
    long_line = "yes x | tr -d '\\n' | head -c 3000000\n"
    with_fail = stub(tmp_path / "fast-long-fail-line", "printf ' FAIL  '\n" + long_line + "exit 1\n")
    plain = stub(tmp_path / "fast-long-plain-line", long_line + "exit 1\n")
    reason_file = tmp_path / ".tdd" / "verify-pin.reason"

    subprocess.run([CHECK, with_fail], cwd=tmp_path, capture_output=True)
    sizes = {"fail line": len(reason_file.read_bytes())}
    subprocess.run([CHECK, plain], cwd=tmp_path, capture_output=True)
    sizes["plain line"] = len(reason_file.read_bytes())

    assert {name: size <= BOUND_BYTES for name, size in sizes.items()} == {"fail line": True, "plain line": True}, sizes
