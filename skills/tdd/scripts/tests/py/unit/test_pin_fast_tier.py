"""In-process cases for veri/pin_fast_tier.py: bounded()'s bound on an over-long fast-tier output, and main through run_cli
as pin-fast-tier.sh, the fast command faked at its process boundary."""
import importlib

import pytest


def test_a_line_over_the_cap_keeps_its_tail_2936():
    pin_fast_tier = importlib.import_module("pin_fast_tier")
    output = b"y" * pin_fast_tier.BOUND_BYTES + b"\n" + b"x" * 2000 + b" FAIL  src/a.test.ts"

    assert len(output) > pin_fast_tier.BOUND_BYTES
    assert b" FAIL  src/a.test.ts" in pin_fast_tier.bounded(output)


def test_a_clip_inside_a_multibyte_character_still_decodes_as_utf8_2936():
    pin_fast_tier = importlib.import_module("pin_fast_tier")
    output = b"y" * pin_fast_tier.BOUND_BYTES + b"\n" + "€".encode() * 2000

    assert len(output) > pin_fast_tier.BOUND_BYTES
    pin_fast_tier.bounded(output).decode("utf-8")


def test_many_fail_blocks_stay_within_the_fail_cap_plus_one_block_and_the_tail_2936():
    pin_fast_tier = importlib.import_module("pin_fast_tier")
    filler = b"f" * 1000
    block = [b" FAIL  src/a.test.ts"] + [filler] * (pin_fast_tier.FAIL_BLOCK_LINES - 1)
    tail = [b"z"] * pin_fast_tier.TAIL_LINES
    output = b"\n".join(block * 20 + tail)

    assert len(output) > pin_fast_tier.BOUND_BYTES
    one_block = sum(len(line) + 1 for line in block)
    tail_bytes = sum(len(line) + 1 for line in tail)
    limit = pin_fast_tier.FAIL_CAP_BYTES + one_block + tail_bytes
    assert len(pin_fast_tier.bounded(output)) <= limit < pin_fast_tier.BOUND_BYTES - 1024


# main through run_cli as `pin-fast-tier.sh <fast-cmd>`. The fast command, a shell stub in the process cases these came
# from, is answered by fake_processes with the output that stub printed: fast_command(...) answers exactly
# `sh -c <fast>`, so a different command line fails the case as an unexpected process.

@pytest.fixture
def pin_fast_tier():
    return importlib.import_module("pin_fast_tier")


def fast_command(fake_processes, tmp_path, *runs):
    """Each of <runs> is (name, output, code): `sh -c <tmp_path>/<name>` prints <output> and exits <code>."""
    fast = {name: str(tmp_path / name) for name, _, _ in runs}
    fake_processes.answers({"sh -c " + fast[name]: (code, output, "") for name, output, code in runs}, exact=True)
    return fast


def noise(template, count=20000):
    return "".join(template % (i, i) if template.count("%") == 2 else template % i for i in range(count))


def test_a_failing_fast_command_exits_1_and_leaves_its_output_in_the_reason_file(
        tmp_path, pin_fast_tier, run_cli, fake_processes):
    (tmp_path / ".tdd").mkdir()
    output = "FAIL - a suite builds its own scratch instead of the harness's\n0 passed, 1 failed\n"
    fast = fast_command(fake_processes, tmp_path, ("fast-red", output, 1))

    code, out, err = run_cli(pin_fast_tier, [fast["fast-red"]], cwd=tmp_path)

    reason = (tmp_path / ".tdd" / "verify-pin.reason").read_text()
    assert code == 1
    assert "builds its own scratch instead of the harness's" in reason


def test_no_argument_prints_usage_on_stderr_and_exits_2_without_a_reason_file(
        tmp_path, pin_fast_tier, run_cli, fake_processes):
    fake_processes.answers({}, exact=True)

    code, out, err = run_cli(pin_fast_tier, [], cwd=tmp_path)

    assert code == 2
    assert out == ""
    assert "usage: pin-fast-tier.sh" in err
    assert not (tmp_path / ".tdd" / "verify-pin.reason").exists()


def test_a_passing_fast_command_exits_0_silent_without_a_reason_file(tmp_path, pin_fast_tier, run_cli, fake_processes):
    fast = fast_command(fake_processes, tmp_path, ("fast-green", "0 failed\n", 0))

    code, out, err = run_cli(pin_fast_tier, [fast["fast-green"]], cwd=tmp_path)

    assert code == 0
    assert out + err == ""
    assert not (tmp_path / ".tdd" / "verify-pin.reason").exists()


def test_a_noisy_failing_fast_command_leaves_a_bounded_reason_file_with_its_fail_block_2882(
        tmp_path, pin_fast_tier, run_cli, fake_processes):
    (tmp_path / ".tdd").mkdir()
    output = (noise("    at passing-noise-frame-%d (src/component.tsx:%d:10) padding padding padding padding padding padding\n")
              + " FAIL  src/widget.test.ts > widget > renders the unique-failure-marker\n"
              + "  AssertionError: expected 1 to be 2\n")
    fast = fast_command(fake_processes, tmp_path, ("fast-noisy", output, 1))

    code, out, err = run_cli(pin_fast_tier, [fast["fast-noisy"]], cwd=tmp_path)

    reason = (tmp_path / ".tdd" / "verify-pin.reason").read_bytes()
    assert code == 1
    assert len(reason) < 512 * 1024
    assert b"unique-failure-marker" in reason
    assert b"AssertionError: expected 1 to be 2" in reason


def test_a_noisy_reason_keeps_a_fail_block_that_lies_before_the_tail_and_a_small_one_is_unchanged_2882(
        tmp_path, pin_fast_tier, run_cli, fake_processes):
    (tmp_path / ".tdd").mkdir()
    noisy = (" FAIL  src/early.test.ts > early > early-failure-marker\n"
             "  early-detail-line: expected 1 to be 2\n"
             + noise("    at passing-noise-frame-%d (src/component.tsx:%d:10) padding padding padding padding padding\n"))
    small = " FAIL  src/s.test.ts > small-failure-marker\n  small-detail-line\n1 failed\n"
    fast = fast_command(fake_processes, tmp_path, ("fast-noisy-suffix", noisy, 1), ("fast-small", small, 1))
    reason_file = tmp_path / ".tdd" / "verify-pin.reason"

    run_cli(pin_fast_tier, [fast["fast-noisy-suffix"]], cwd=tmp_path)
    noisy_reason = reason_file.read_bytes()
    run_cli(pin_fast_tier, [fast["fast-small"]], cwd=tmp_path)
    small_reason = reason_file.read_bytes()

    assert len(noisy_reason) < 512 * 1024
    assert b"early-failure-marker" in noisy_reason
    assert b"early-detail-line: expected 1 to be 2" in noisy_reason
    assert small_reason == (b" FAIL  src/s.test.ts > small-failure-marker\n  small-detail-line\n1 failed\n")


def test_a_failing_fast_command_with_output_exactly_at_the_bound_leaves_it_unchanged_in_the_reason_file_2909(
        tmp_path, pin_fast_tier, run_cli, fake_processes):
    (tmp_path / ".tdd").mkdir()
    output = (b"ok " + b"0" * 1020 + b"\n") * 127 + b"ok " + b"0" * 1021
    fast = fast_command(fake_processes, tmp_path, ("fast-at-bound", output.decode(), 1))

    code, out, err = run_cli(pin_fast_tier, [fast["fast-at-bound"]], cwd=tmp_path)

    reason = (tmp_path / ".tdd" / "verify-pin.reason").read_bytes()
    assert code == 1
    assert len(output) == 128 * 1024
    assert reason == output + b"\n"


def test_output_over_the_bound_with_no_fail_line_leaves_its_last_line_in_the_reason_file_2909(
        tmp_path, pin_fast_tier, run_cli, fake_processes):
    (tmp_path / ".tdd").mkdir()
    output = (noise("    lint-noise-line-%d padding padding padding padding padding padding\n")
              + "error: unique-final-tail-marker\n")
    fast = fast_command(fake_processes, tmp_path, ("fast-no-fail-marker", output, 1))

    code, out, err = run_cli(pin_fast_tier, [fast["fast-no-fail-marker"]], cwd=tmp_path)

    reason = (tmp_path / ".tdd" / "verify-pin.reason").read_bytes()
    assert code == 1
    assert reason.strip() != b""
    assert b"error: unique-final-tail-marker" in reason


def test_output_of_many_fail_lines_over_the_bound_leaves_a_reason_file_under_the_cap_2909(
        tmp_path, pin_fast_tier, run_cli, fake_processes):
    (tmp_path / ".tdd").mkdir()
    output = noise(" FAIL  src/case-%d.test.ts > case %d padding padding padding\n") + "error: unique-final-tail-marker\n"
    fast = fast_command(fake_processes, tmp_path, ("fast-all-fail", output, 1))

    code, out, err = run_cli(pin_fast_tier, [fast["fast-all-fail"]], cwd=tmp_path)

    reason = (tmp_path / ".tdd" / "verify-pin.reason").read_bytes()
    assert code == 1
    assert len(reason) < 2 * pin_fast_tier.BOUND_BYTES
    assert b"error: unique-final-tail-marker" in reason


def test_a_single_line_longer_than_the_bound_leaves_a_reason_file_of_at_most_the_bound_bytes_2909(
        tmp_path, pin_fast_tier, run_cli, fake_processes):
    (tmp_path / ".tdd").mkdir()
    long_line = "x" * 3000000
    fast = fast_command(fake_processes, tmp_path,
                        ("fast-long-fail-line", " FAIL  " + long_line, 1), ("fast-long-plain-line", long_line, 1))
    reason_file = tmp_path / ".tdd" / "verify-pin.reason"

    run_cli(pin_fast_tier, [fast["fast-long-fail-line"]], cwd=tmp_path)
    sizes = {"fail line": len(reason_file.read_bytes())}
    run_cli(pin_fast_tier, [fast["fast-long-plain-line"]], cwd=tmp_path)
    sizes["plain line"] = len(reason_file.read_bytes())

    assert {name: size <= pin_fast_tier.BOUND_BYTES for name, size in sizes.items()} == {"fail line": True, "plain line": True}, sizes
