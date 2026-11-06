"""Cases for pin-recheck.sh against a real git repository."""
import os
import subprocess

import pytest

from conftest import SCRIPTS

RECHECK = str(SCRIPTS / "pin-recheck.sh")


def record(path, **fields):
    path.write_text("".join(f"{name} {len(value)}\n{value}\n" for name, value in fields.items()) + "\n")


@pytest.mark.process("git, and pin-recheck.sh run over a range that leaves the recorded file alone")
def test_2506_a_record_naming_a_file_the_range_does_not_touch_exits_3_and_runs_nothing(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / "other.txt").write_text("one\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-835-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="touch ran.witness")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "other.txt").write_text("two\n")
    git("commit", "-q", "-am", "touch only other.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, (tmp_path / "ran.witness").exists()) == (3, False), ran.stderr


@pytest.mark.process("pin-recheck.sh run with no argument")
def test_2506_no_argument_exits_2_prints_nothing_on_stdout_and_its_usage_line_on_stderr(tmp_path):
    ran = subprocess.run(["sh", RECHECK], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, ran.stdout, ran.stderr) == (2, "", "usage: pin-recheck.sh <base-sha>\n")


@pytest.mark.process("git, and pin-recheck.sh run over a range that touches the recorded file")
def test_2506_a_record_whose_command_passes_unmutated_and_fails_mutated_exits_0_and_leaves_the_file_alone(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-835-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="sh -c \"echo result; grep -q 'if guard' guard.txt\"")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "touch guard.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, (tmp_path / "guard.txt").read_bytes()) == (0, b"if guard\nmore\n"), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a range whose later commit disarms the recorded pin")
def test_2506_a_record_whose_command_stays_green_under_its_mutation_exits_1_naming_the_pin_and_restores_the_file(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\nthrows\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-835-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="grep -q throws guard.txt")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nthrows\nsafe\n")
    git("commit", "-q", "-am", "later commit makes the test pass with the guard reverted")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, "guard.txt" in ran.stdout + ran.stderr, (tmp_path / "guard.txt").read_bytes()) == (
        1, True, b"if guard\nthrows\nsafe\n"), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a range whose later commit removes the recorded old text")
def test_2506_a_record_whose_old_text_is_gone_prints_the_pin_as_needing_a_look_and_exits_0(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\nthrows\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-835-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="grep -q throws guard.txt")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if safeguard\nthrows\n".replace("safeguard", "checked"))
    git("commit", "-q", "-am", "later commit rewrites the guard line")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, "guard.txt" in ran.stdout, "stayed green" in ran.stderr) == (0, True, False), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a range where the recorded command fails before any mutation")
def test_2506_a_record_whose_command_fails_unmutated_prints_the_pin_as_needing_a_look_and_exits_0(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-835-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="grep -q throws guard.txt")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "touch guard.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, "guard.txt" in ran.stdout, (tmp_path / "guard.txt").read_bytes()) == (
        0, True, b"if guard\nmore\n"), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run with a base-sha the repository cannot resolve")
def test_2506_a_base_sha_that_does_not_resolve_exits_2_with_nothing_on_stdout(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-835-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="touch ran.witness")
    git("add", "-A")
    git("commit", "-q", "-m", "base")

    ran = subprocess.run(["sh", RECHECK, "0" * 40], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, ran.stdout, (tmp_path / "ran.witness").exists()) == (2, "", False), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a range with a mutations record it cannot parse")
def test_2506_a_mutations_record_that_cannot_be_parsed_exits_2_with_nothing_on_stdout(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-835-mutations.md").write_text("this is not a record\n")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "touch guard.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, ran.stdout) == (2, ""), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a record whose wrapper path no longer exists")
def test_2814_a_record_through_a_vanished_timed_test_run_path_is_replayed_and_not_reported_as_needing_a_look(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / ".tdd").mkdir()
    gone = tmp_path / "gone-scratch" / "scripts" / "timed-test-run.sh"
    record(tmp_path / ".tdd" / "issue-2814-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command=f"{gone} unit guard sh -c \"echo result; grep -q 'if guard' guard.txt\"")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "touch guard.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=60)

    assert (ran.returncode, ran.stdout, (tmp_path / "guard.txt").read_bytes()) == (
        0, "", b"if guard\nmore\n"), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a record whose wrapper path still exists")
def test_2814_a_record_through_a_timed_test_run_path_that_still_exists_is_replayed_through_that_path(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / ".tdd").mkdir()
    kept = tmp_path / "kept-scratch" / "scripts" / "timed-test-run.sh"
    kept.parent.mkdir(parents=True)
    kept.write_text(f'#!/bin/sh\necho used >> {tmp_path}/marker\nshift 2\nexec "$@"\n')
    kept.chmod(0o755)
    record(tmp_path / ".tdd" / "issue-2814-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command=f"{kept} unit guard sh -c \"echo result; grep -q 'if guard' guard.txt\"")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "touch guard.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=60)

    marker = tmp_path / "marker"
    assert (ran.returncode, ran.stdout, marker.read_text() if marker.exists() else "") == (
        0, "", "used\nused\n"), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a vanished-wrapper record whose command cannot run")
def test_2814_a_record_through_a_vanished_timed_test_run_path_whose_command_still_fails_prints_needs_a_look(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / ".tdd").mkdir()
    gone = tmp_path / "gone-scratch" / "scripts" / "timed-test-run.sh"
    record(tmp_path / ".tdd" / "issue-2814-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command=f"{gone} unit guard grep -q absent-text guard.txt")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "touch guard.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=60)

    assert (ran.returncode, ran.stdout, (tmp_path / "guard.txt").read_bytes()) == (
        0, "needs a look: guard.txt\n", b"if guard\nmore\n"), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a record whose mutated run fails a real test")
def test_2827_a_mutated_run_that_exits_non_zero_and_still_prints_the_unmutated_result_line_counts_as_red_and_exits_0(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-2827-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="echo 'FAIL: TestGuard' >&2; grep -q 'if guard' guard.txt")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "touch guard.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, ran.stdout, (tmp_path / "guard.txt").read_bytes()) == (
        0, "", b"if guard\nmore\n"), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a record whose mutated run prints none of the unmutated lines")
def test_2827_a_mutated_run_that_exits_non_zero_and_prints_none_of_the_unmutated_lines_needs_a_look_and_exits_1(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-2827-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="if grep -q 'if guard' guard.txt; then echo 'ok TestGuard'; else echo 'error: build failed'; exit 1; fi")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "touch guard.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, ran.stdout, (tmp_path / "guard.txt").read_bytes()) == (
        1, "needs a look: guard.txt (mutation did not build)\n", b"if guard\nmore\n"), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a record whose unmutated run prints its result line on stderr only")
def test_2827_a_result_line_printed_only_on_stderr_still_tells_a_build_failure_from_a_red_test(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-2827-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="if grep -q 'if guard' guard.txt; then echo 'ok TestGuard' >&2; else echo 'error: build failed' >&2; exit 1; fi")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "touch guard.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, ran.stdout, (tmp_path / "guard.txt").read_bytes()) == (
        1, "needs a look: guard.txt (mutation did not build)\n", b"if guard\nmore\n"), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a record whose unmutated run prints nothing")
def test_2843_a_mutated_run_that_exits_non_zero_after_a_silent_unmutated_run_needs_a_look_and_exits_1(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-2843-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="if grep -q 'if guard' guard.txt; then :; else echo 'error: build failed'; exit 1; fi")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "touch guard.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, ran.stdout.startswith("needs a look: guard.txt"), (tmp_path / "guard.txt").read_bytes()) == (
        1, True, b"if guard\nmore\n"), ran.stdout + ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a record whose mutated run prints more than 40 lines")
def test_2843_a_mutation_that_did_not_build_writes_the_last_40_lines_of_the_mutated_output_to_stderr(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-2843-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="if grep -q 'if guard' guard.txt; then echo 'ok TestGuard'; "
                   "else for i in $(seq 1 30); do echo \"out $i\"; echo \"err $i\" >&2; done; exit 1; fi")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "touch guard.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    lines = ran.stderr.splitlines()
    assert (ran.returncode, len(lines), "err 30" in lines, "out 1" in lines) == (1, 40, True, False), ran.stdout + ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a record whose unmutated run fails and prints more than 40 lines")
def test_2843_an_unmutated_run_that_exits_non_zero_writes_the_last_40_lines_of_its_output_to_stderr(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-2843-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="for i in $(seq 1 30); do echo \"out $i\"; echo \"err $i\" >&2; done; exit 1")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "touch guard.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    lines = ran.stderr.splitlines()
    assert (ran.stdout.startswith("needs a look: guard.txt"), len(lines), "err 30" in lines, "out 1" in lines) == (
        True, 40, True, False), ran.stdout + ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a record whose unmutated run is silent and whose mutated run fails to build")
def test_2843_a_silent_unmutated_run_and_a_mutated_build_failure_writes_the_mutated_output_to_stderr(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-2843-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="if grep -q 'if guard' guard.txt; then :; else echo 'error: build failed'; exit 1; fi")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "touch guard.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, ran.stdout.startswith("needs a look: guard.txt"), ran.stderr) == (
        1, True, "error: build failed\n"), ran.stdout


@pytest.mark.process("git, and pin-recheck.sh run over a record whose mutated run fails a Go test and shares no output line with the unmutated run")
def test_2875_a_go_test_failure_on_the_mutated_run_counts_as_red_and_exits_0_and_restores_the_file(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-2875-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="if grep -q 'if guard' guard.txt; then printf 'ok  \\tpkg\\t0.1s\\n'; "
                   "else echo '--- FAIL: TestX (0.00s)'; echo FAIL; printf 'FAIL\\tpkg\\t0.2s\\n'; exit 1; fi")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "touch guard.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, ran.stdout, (tmp_path / "guard.txt").read_bytes()) == (
        0, "", b"if guard\nmore\n"), ran.stdout + ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a record whose mutated run fails to build a Go package")
def test_2875_a_go_build_failure_on_the_mutated_run_still_needs_a_look_and_exits_1_and_restores_the_file(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-2875-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="if grep -q 'if guard' guard.txt; then printf 'ok  \\tpkg\\t0.1s\\n'; "
                   "else printf 'FAIL\\tpkg [build failed]\\n'; exit 1; fi")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "touch guard.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, ran.stdout, (tmp_path / "guard.txt").read_bytes()) == (
        1, "needs a look: guard.txt (mutation did not build)\n", b"if guard\nmore\n"), ran.stdout + ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a record whose unquoted bash -c command runs no test")
def test_2876_a_bash_c_command_with_its_script_unquoted_runs_no_test_and_needs_a_look_and_exits_0(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-2876-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="bash -c echo hello world")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "touch guard.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, ran.stdout, (tmp_path / "guard.txt").read_bytes()) == (
        0, "needs a look: guard.txt\n", b"if guard\nmore\n"), ran.stdout + ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a record whose command runs its test, passes clean and fails mutated")
def test_2876_a_command_that_runs_its_test_passing_clean_and_failing_mutated_reports_the_pin_held_and_exits_0(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-2876-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="bash -c \"echo result; grep -q 'if guard' guard.txt\"")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "touch guard.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, ran.stdout, ran.stderr, (tmp_path / "guard.txt").read_bytes()) == (
        0, "", "", b"if guard\nmore\n")


@pytest.mark.process("git, and pin-recheck.sh run over a record whose command reads the file and passes clean and mutated")
def test_2876_a_command_that_reads_its_file_and_passes_clean_and_mutated_still_reports_the_pin_stayed_green_and_exits_1(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\nthrows\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-2876-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="grep -q throws guard.txt")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nthrows\nmore\n")
    git("commit", "-q", "-am", "touch guard.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, ran.stdout, ran.stderr, (tmp_path / "guard.txt").read_bytes()) == (
        1, "", "pin stayed green under its mutation: guard.txt\n", b"if guard\nthrows\nmore\n")


@pytest.mark.process("git, and pin-recheck.sh run over a record whose command runs no test, so the control run happens")
def test_2876_after_the_control_run_of_a_command_that_runs_no_test_the_pinned_file_holds_its_original_bytes(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-2876-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="true")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    original = b"if guard\r\n\xff\x00 tail without newline"
    (tmp_path / "guard.txt").write_bytes(original)
    git("commit", "-q", "-am", "touch guard.txt")

    subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (tmp_path / "guard.txt").read_bytes() == original


@pytest.mark.process("git, and pin-recheck.sh run over a record whose mutated run fails, so no control run happens")
def test_2876_a_mutated_run_that_fails_makes_no_control_run_so_the_command_never_sees_the_control_content(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-2876-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="echo result; head -c 7 guard.txt >> ../runs.log; echo >> ../runs.log; grep -q 'if guard' guard.txt")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "touch guard.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, (tmp_path.parent / "runs.log").read_bytes()) == (0, b"if guar\nif (tru\n")


@pytest.mark.process("git, and pin-recheck.sh run over a record whose command is not bash -c and runs no test")
def test_2876_a_command_that_is_not_bash_c_and_runs_no_test_needs_a_look_and_exits_0(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-2876-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="true")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "touch guard.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, ran.stdout, (tmp_path / "guard.txt").read_bytes()) == (
        0, "needs a look: guard.txt\n", b"if guard\nmore\n"), ran.stdout + ran.stderr


@pytest.mark.process("git, mutation-probe.sh recording a pin and pin-recheck.sh replaying it, over a title with an apostrophe and spaces")
def test_2877_a_recorded_pin_whose_title_has_an_apostrophe_and_spaces_is_replayed_with_the_title_as_one_argument(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    title = "that shell's own job spec"
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / "runner.sh").write_text('echo result\nprintf "%s:%s" "$#" "$1" > seen.txt\ngrep -q "if guard" guard.txt\n')
    (tmp_path / ".tdd").mkdir()
    record_path = tmp_path / ".tdd" / "issue-2877-mutations.md"
    probed = subprocess.run(
        ["sh", str(SCRIPTS / "mutation-probe.sh"), "guard.txt", "if guard", "if (true)", "--", "sh", "runner.sh", title],
        cwd=tmp_path, capture_output=True, text=True, timeout=20, env={**os.environ, "VERI_MUTATION_RECORD": str(record_path)})
    assert probed.returncode == 0, probed.stderr
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "touch guard.txt")
    (tmp_path / "seen.txt").unlink()

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, ran.stdout, (tmp_path / "seen.txt").read_text()) == (0, "", f"1:{title}"), ran.stderr


@pytest.mark.process("git, mutation-probe.sh probing through the real timed-test-run.sh and pin-recheck.sh replaying the record")
def test_2877_a_probe_through_timed_test_run_records_the_test_command_alone_and_it_replays_green(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / "runner.sh").write_text('echo result\ngrep -q "if guard" guard.txt\n')
    (tmp_path / ".tdd").mkdir()
    record_path = tmp_path / ".tdd" / "issue-2877-mutations.md"
    probed = subprocess.run(
        ["sh", str(SCRIPTS / "mutation-probe.sh"), "guard.txt", "if guard", "if (true)", "--",
         str(SCRIPTS / "timed-test-run.sh"), "affected", "runner", "sh", "runner.sh"],
        cwd=tmp_path, capture_output=True, text=True, timeout=20, env={**os.environ, "VERI_MUTATION_RECORD": str(record_path)})
    assert probed.returncode == 0, probed.stderr
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "touch guard.txt")
    other = tmp_path / "other"
    git("clone", "-q", ".", "other")

    ran = subprocess.run(["sh", RECHECK, base], cwd=other, capture_output=True, text=True, timeout=20)

    recorded = record_path.read_text()
    assert (ran.returncode, ran.stdout, "command 12\nsh runner.sh\n" in recorded, "timed-test-run" in recorded) == (
        0, "", True, False), ran.stderr + recorded


@pytest.mark.process("git, mutation-probe.sh probing through a symlinked scripts directory and pin-recheck.sh replaying the record from a clone")
def test_2919_a_probe_through_a_symlinked_scripts_directory_records_the_test_command_alone_and_it_replays_green_from_another_directory(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    def git(*words, cwd=repo):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=cwd,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (repo / "guard.txt").write_text("if guard\n")
    (repo / "runner.sh").write_text('echo result\ngrep -q "if guard" guard.txt\n')
    (repo / ".tdd").mkdir()
    link = tmp_path / "scripts-link"
    link.symlink_to(SCRIPTS)
    record_path = repo / ".tdd" / "issue-2919-mutations.md"
    probed = subprocess.run(
        ["sh", str(SCRIPTS / "mutation-probe.sh"), "guard.txt", "if guard", "if (true)", "--",
         str(link / "timed-test-run.sh"), "affected", "runner", "sh", "runner.sh"],
        cwd=repo, capture_output=True, text=True, timeout=20, env={**os.environ, "VERI_MUTATION_RECORD": str(record_path)})
    assert probed.returncode == 0, probed.stderr
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (repo / "guard.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "touch guard.txt")
    other = tmp_path / "other"
    git("clone", "-q", str(repo), str(other), cwd=tmp_path)

    ran = subprocess.run(["sh", RECHECK, base], cwd=other, capture_output=True, text=True, timeout=20)

    recorded = record_path.read_text()
    assert (ran.returncode, ran.stdout, "command 12\nsh runner.sh\n" in recorded, "timed-test-run" in recorded) == (
        0, "", True, False), ran.stderr + recorded


@pytest.mark.process("git, and pin-recheck.sh run over a before/keep record whose command is red on the restored files")
def test_2959_a_before_keep_record_whose_command_is_red_on_the_restored_files_exits_0_without_a_keyerror(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "src.txt").write_text("old behaviour\n")
    (tmp_path / "pin.txt").write_text("pin v0\n")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "src.txt").write_text("fixed behaviour\n")
    (tmp_path / "pin.txt").write_text("pin v1\n")
    git("commit", "-q", "-am", "fix and pin")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-2959-mutations.md", before=base, keep="pin.txt",
           command="grep -q fixed src.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, "KeyError" in ran.stderr, (tmp_path / "src.txt").read_bytes()) == (
        0, False, b"fixed behaviour\n"), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a before/keep record whose command reads the keep path and a .tdd file")
def test_2959_a_before_keep_record_leaves_the_keep_path_and_tdd_files_at_their_current_content_while_the_command_runs(
        tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "src.txt").write_text("old behaviour\n")
    (tmp_path / "pin.txt").write_text("pin v0\n")
    (tmp_path / ".tdd" / "notes.md").write_text("ledger v0\n")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "src.txt").write_text("fixed behaviour\n")
    (tmp_path / "pin.txt").write_text("pin v1\n")
    (tmp_path / ".tdd" / "notes.md").write_text("ledger v1\n")
    git("commit", "-q", "-am", "fix, pin and ledger")
    record(tmp_path / ".tdd" / "issue-2959-mutations.md", before=base, keep="pin.txt",
           command="! { grep -q 'pin v1' pin.txt && grep -q 'ledger v1' .tdd/notes.md; }")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, ran.stderr) == (0, ""), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a before/keep record whose command is red only if the keep path or a .tdd file was restored")
def test_2959_a_before_keep_record_whose_command_is_green_on_the_current_keep_path_and_tdd_files_exits_1(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "src.txt").write_text("old behaviour\n")
    (tmp_path / "pin.txt").write_text("pin v0\n")
    (tmp_path / ".tdd" / "notes.md").write_text("ledger v0\n")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "src.txt").write_text("fixed behaviour\n")
    (tmp_path / "pin.txt").write_text("pin v1\n")
    (tmp_path / ".tdd" / "notes.md").write_text("ledger v1\n")
    git("commit", "-q", "-am", "fix, pin and ledger")
    record(tmp_path / ".tdd" / "issue-2959-mutations.md", before=base, keep="pin.txt",
           command="grep -q 'pin v1' pin.txt && grep -q 'ledger v1' .tdd/notes.md")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert ran.returncode == 1, ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a before/keep record whose command is green on the restored files")
def test_2959_a_before_keep_record_whose_command_is_green_on_the_restored_files_names_the_record_on_stderr_and_exits_1(
        tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "src.txt").write_text("old behaviour\n")
    (tmp_path / "pin.txt").write_text("pin v0\n")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "src.txt").write_text("fixed behaviour\n")
    (tmp_path / "pin.txt").write_text("pin v1\n")
    git("commit", "-q", "-am", "fix and pin")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-2959-mutations.md", before=base, keep="pin.txt",
           command="grep -q old src.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, "pin.txt" in ran.stderr, "KeyError" in ran.stderr) == (1, True, False), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over an old-format record that holds and a before/keep record that stays green")
def test_2959_a_green_before_keep_record_beside_an_old_format_record_is_reported_and_exits_1_while_the_old_format_record_holds(
        tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "src.txt").write_text("old behaviour\n")
    (tmp_path / "pin.txt").write_text("pin v0\n")
    (tmp_path / "guard.txt").write_text("if guard\n")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "src.txt").write_text("fixed behaviour\n")
    (tmp_path / "pin.txt").write_text("pin v1\n")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "fix, pin and touch guard")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-2959-mutations.md", before=base, keep="pin.txt",
           command="grep -q old src.txt")
    record(tmp_path / ".tdd" / "issue-835-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="sh -c \"echo result; grep -q 'if guard' guard.txt\"")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, "pin.txt" in ran.stderr, "guard.txt" in ran.stdout + ran.stderr, "KeyError" in ran.stderr,
            (tmp_path / "guard.txt").read_bytes()) == (1, True, False, False, b"if guard\nmore\n"), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a record that is neither format")
def test_2959_a_record_with_neither_file_nor_before_exits_2_naming_the_record_and_not_a_key_error(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "touch guard.txt")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-2959-mutations.md", keep="pin.txt", command="touch ran.witness")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, ran.stdout, "issue-2959-mutations.md" in ran.stderr, "KeyError" in ran.stderr,
            (tmp_path / "ran.witness").exists()) == (2, "", True, False, False), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a before/keep record whose command is red and a file is absent at the before sha")
def test_2959_a_red_before_keep_replay_leaves_every_restored_file_a_file_absent_at_before_and_the_keep_path_byte_identical(
        tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "src.txt").write_text("old behaviour\n")
    (tmp_path / "pin.txt").write_text("pin v0\n")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "src.txt").write_text("fixed behaviour\n")
    (tmp_path / "pin.txt").write_text("pin v1\n")
    (tmp_path / "z_new.txt").write_bytes(b"added \x00 later\n")
    git("add", "-A")
    git("commit", "-q", "-m", "fix, pin and add")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-2959-mutations.md", before=base, keep="pin.txt",
           command="grep -q fixed src.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, (tmp_path / "src.txt").read_bytes(), (tmp_path / "pin.txt").read_bytes(),
            (tmp_path / "z_new.txt").read_bytes() if (tmp_path / "z_new.txt").exists() else None) == (
        0, b"fixed behaviour\n", b"pin v1\n", b"added \x00 later\n"), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a before/keep record whose command fails only while a file absent at the before sha exists")
def test_2959_a_before_keep_replay_removes_a_file_absent_at_the_before_sha_while_the_command_runs(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "src.txt").write_text("old behaviour\n")
    (tmp_path / "pin.txt").write_text("pin v0\n")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "src.txt").write_text("fixed behaviour\n")
    (tmp_path / "pin.txt").write_text("pin v1\n")
    (tmp_path / "z_new.txt").write_text("added later\n")
    git("add", "-A")
    git("commit", "-q", "-m", "fix, pin and add")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-2959-mutations.md", before=base, keep="pin.txt",
           command="test ! -e z_new.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, "pin.txt" in ran.stderr, (tmp_path / "z_new.txt").read_bytes()) == (
        1, True, b"added later\n"), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a before/keep record whose command is green on the restored files and a file is absent at the before sha")
def test_2959_a_green_before_keep_replay_leaves_every_restored_file_a_file_absent_at_before_and_the_keep_path_byte_identical(
        tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "src.txt").write_text("old behaviour\n")
    (tmp_path / "pin.txt").write_text("pin v0\n")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "src.txt").write_text("fixed behaviour\n")
    (tmp_path / "pin.txt").write_text("pin v1\n")
    (tmp_path / "z_new.txt").write_bytes(b"added \x00 later\n")
    git("add", "-A")
    git("commit", "-q", "-m", "fix, pin and add")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-2959-mutations.md", before=base, keep="pin.txt",
           command="grep -q old src.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, (tmp_path / "src.txt").read_bytes(), (tmp_path / "pin.txt").read_bytes(),
            (tmp_path / "z_new.txt").read_bytes() if (tmp_path / "z_new.txt").exists() else None) == (
        1, b"fixed behaviour\n", b"pin v1\n", b"added \x00 later\n"), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a before/keep record on a branch that deleted a tracked file")
def test_2974_a_before_keep_replay_restores_a_file_the_branch_deleted_and_exits_with_the_replay_verdict(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "gone.txt").write_text("needed by the old behaviour\n")
    (tmp_path / "pin.txt").write_text("pin v0\n")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    git("rm", "-q", "gone.txt")
    (tmp_path / "pin.txt").write_text("pin v1\n")
    git("add", "-A")
    git("commit", "-q", "-m", "delete gone.txt and pin")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-2974-mutations.md", before=base, keep="pin.txt", command="test -e gone.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, (tmp_path / "gone.txt").exists()) == (1, False), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a before/keep record in a repo whose branch deleted a tracked file")
def test_2974_a_before_keep_record_on_a_branch_that_deleted_a_tracked_file_replays_and_leaves_the_tree_as_found(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "src.txt").write_text("old behaviour\n")
    (tmp_path / "pin.txt").write_text("pin v0\n")
    (tmp_path / "gone.txt").write_text("doomed\n")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "src.txt").write_text("fixed behaviour\n")
    (tmp_path / "pin.txt").write_text("pin v1\n")
    (tmp_path / "gone.txt").unlink()
    git("commit", "-q", "-am", "fix, pin and delete")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-2974-mutations.md", before=base, keep="pin.txt",
           command="test -f gone.txt && ! grep -q fixed src.txt && false || ! { test -f gone.txt && grep -q old src.txt; }")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, (tmp_path / "gone.txt").exists(), (tmp_path / "src.txt").read_bytes(),
            (tmp_path / "pin.txt").read_bytes()) == (0, False, b"fixed behaviour\n", b"pin v1\n"), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a before/keep record with a green commit, after main moved an unrelated file")
def test_2974_a_before_keep_record_with_a_green_commit_replays_without_touching_a_file_a_rebase_brought_in(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "src.txt").write_text("old behaviour\n")
    (tmp_path / "pin.txt").write_text("pin v0\n")
    (tmp_path / "other.txt").write_text("other v0\n")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "src.txt").write_text("fixed behaviour\n")
    (tmp_path / "pin.txt").write_text("pin v1\n")
    git("commit", "-q", "-am", "fix and pin")
    green = git("rev-parse", "HEAD")
    (tmp_path / "other.txt").write_text("other v1\n")
    git("commit", "-q", "-am", "main moved on")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-2974-mutations.md", before=base, keep="pin.txt", green=green,
           command="cp other.txt seen.out; ! grep -q old src.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, (tmp_path / "seen.out").read_bytes(), (tmp_path / "other.txt").read_bytes()) == (
        0, b"other v1\n", b"other v1\n"), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a before/keep record whose green is the plan commit, earlier than the ledger's tick")
def test_3016_a_before_keep_record_whose_green_precedes_the_tick_commit_replays_against_the_tick_commit(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "src.txt").write_text("old behaviour\n")
    (tmp_path / "pin.txt").write_text("pin v0\n")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-3016.md").write_text("- [ ] step\n")
    git("add", "-A")
    git("commit", "-q", "-m", "plan")
    plan = git("rev-parse", "HEAD")
    (tmp_path / "src.txt").write_text("fixed behaviour\n")
    (tmp_path / "pin.txt").write_text("pin v1\n")
    (tmp_path / ".tdd" / "issue-3016.md").write_text("- [x] step\n")
    git("add", "-A")
    git("commit", "-q", "-m", "green and tick")
    record(tmp_path / ".tdd" / "issue-3016-mutations.md", before=base, keep="pin.txt", green=plan,
           command="! grep -q old src.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, (tmp_path / "src.txt").read_bytes()) == (0, b"fixed behaviour\n"), ran.stderr


@pytest.mark.process("git, pin-recheck.sh replaying a directory-dependent record from a clone")
def test_2919_pin_recheck_replays_the_record_from_the_directory_it_is_run_in_not_the_one_that_recorded_it(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    def git(*words, cwd=repo):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=cwd,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (repo / "guard.txt").write_text("if guard\n")
    (repo / "runner.sh").write_text('echo result\ngrep -q "if guard" guard.txt && grep -qx other where.txt\n')
    (repo / ".tdd").mkdir()
    (repo / ".tdd" / "issue-2919-mutations.md").write_text(
        "file 9\nguard.txt\nold 8\nif guard\nnew 9\nif (true)\ncommand 12\nsh runner.sh\n\n")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (repo / "guard.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "touch guard.txt")
    other = tmp_path / "other"
    git("clone", "-q", str(repo), str(other), cwd=tmp_path)
    (repo / "where.txt").write_text("repo\n")
    (other / "where.txt").write_text("other\n")

    ran = subprocess.run(["sh", RECHECK, base], cwd=other, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, ran.stdout) == (0, ""), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a before/keep record whose before..green range replays no file")
def test_3016_a_before_keep_record_whose_range_replays_no_file_exits_2_naming_before_and_green_not_a_stay_green(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "src.txt").write_text("behaviour\n")
    (tmp_path / "pin.txt").write_text("pin v0\n")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-3016.md").write_text("- [ ] step\n")
    git("add", "-A")
    git("commit", "-q", "-m", "plan")
    plan = git("rev-parse", "HEAD")
    (tmp_path / "pin.txt").write_text("pin v1\n")
    git("commit", "-q", "-am", "touch the keep file after the green")
    record(tmp_path / ".tdd" / "issue-3016-mutations.md", before=base, keep="pin.txt", green=plan, command="true")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, base in ran.stderr, plan in ran.stderr, "stayed green" in ran.stderr) == (
        2, True, True, False), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a before/keep record whose keep file the range does not touch")
def test_3017_a_before_keep_record_whose_keep_file_the_range_does_not_touch_is_not_replayed_and_exits_3(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "pin.txt").write_text("pin v0\n")
    (tmp_path / "other.txt").write_text("one\n")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    first = git("rev-parse", "HEAD")
    (tmp_path / "pin.txt").write_text("pin v1\n")
    git("commit", "-q", "-am", "pin from another issue")
    base = git("rev-parse", "HEAD")
    (tmp_path / "other.txt").write_text("two\n")
    git("commit", "-q", "-am", "touch only other.txt")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-2959-mutations.md", before=first, keep="pin.txt", command="touch ran.witness")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, (tmp_path / "ran.witness").exists()) == (3, False), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a before/keep record whose keep file the range touches and whose command stays green")
def test_3017_a_before_keep_record_whose_keep_file_the_range_touches_is_replayed_and_a_green_command_exits_1_naming_it(
        tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "src.txt").write_text("old behaviour\n")
    (tmp_path / "pin.txt").write_text("pin v0\n")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "pin.txt").write_text("pin v1\n")
    git("commit", "-q", "-am", "touch the keep file")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-3017-mutations.md", before=base, keep="pin.txt",
           command="grep -q old src.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, "pin.txt" in ran.stderr) == (1, True), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a before/keep record whose touched files are absent at the before sha")
def test_3046_a_before_replay_leaves_an_executable_file_100755_and_a_plain_one_100644_with_the_same_bytes(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()

    def state():
        return (git("ls-files", "-s", "scripts/x.sh", "scripts/y.txt"),
                {n: ((tmp_path / n).stat().st_mode & 0o111 != 0, (tmp_path / n).read_bytes())
                 for n in ("scripts/x.sh", "scripts/y.txt")})
    git("init", "-q")
    (tmp_path / "pin.txt").write_text("pin v0\n")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "x.sh").write_text("#!/bin/sh\necho x\n")
    (tmp_path / "scripts" / "x.sh").chmod(0o755)
    (tmp_path / "scripts" / "y.txt").write_text("plain\n")
    (tmp_path / "pin.txt").write_text("pin v1\n")
    git("add", "-A")
    git("commit", "-q", "-m", "add scripts and pin")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-3046-mutations.md", before=base, keep="pin.txt", command="true")
    before = state()

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, state()) == (1, before), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a range that leaves the recorded file alone")
def test_2972_an_exit_0_or_3_leaves_a_receipt_holding_the_head_sha(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / "other.txt").write_text("one\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-835-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="touch ran.witness")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "other.txt").write_text("two\n")
    git("commit", "-q", "-am", "touch only other.txt")
    receipt = tmp_path / ".tdd" / "pin-recheck-ok"

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, receipt.read_text() if receipt.exists() else None) == (3, git("rev-parse", "HEAD") + "\n"), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over an unparseable record with an earlier run's receipt in place")
def test_2972_an_exit_2_removes_a_receipt_an_earlier_run_left(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "other.txt").write_text("one\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-835-mutations.md", old="if guard", new="if (true)", command="true")
    receipt = tmp_path / ".tdd" / "pin-recheck-ok"
    receipt.write_text("stale\n")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "other.txt").write_text("two\n")
    git("commit", "-q", "-am", "touch only other.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, receipt.read_text() if receipt.exists() else None) == (2, None), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a record whose pin stays green, with an earlier run's receipt in place")
def test_2972_an_exit_1_removes_a_receipt_an_earlier_run_left_and_writes_none(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\nthrows\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-835-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="grep -q throws guard.txt")
    receipt = tmp_path / ".tdd" / "pin-recheck-ok"
    receipt.write_text("stale\n")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nthrows\nsafe\n")
    git("commit", "-q", "-am", "later commit makes the test pass with the guard reverted")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, receipt.exists()) == (1, False), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a before/keep record whose before-state replay raises after files were swapped")
def test_2967_a_before_replay_that_raises_mid_run_exits_2_and_leaves_every_file_byte_identical(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()

    def tree():
        return {n: (tmp_path / n).read_bytes() for n in ("a_mod.txt", "b_recreated.txt", "c_added.txt", "z_gone.txt", "pin.txt")
                if (tmp_path / n).exists()}
    git("init", "-q")
    for n, text in (("a_mod.txt", "a v0\n"), ("b_recreated.txt", "b v0\n"), ("pin.txt", "pin v0\n")):
        (tmp_path / n).write_text(text)
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "a_mod.txt").write_text("a v1\n")
    (tmp_path / "b_recreated.txt").unlink()
    (tmp_path / "c_added.txt").write_text("c v1\n")
    (tmp_path / "z_gone.txt").write_text("z v1\n")
    (tmp_path / "pin.txt").write_text("pin v1\n")
    git("add", "-A")
    git("commit", "-q", "-m", "fix and pin")
    green = git("rev-parse", "HEAD")
    (tmp_path / "a_mod.txt").write_text("a v2\n")
    (tmp_path / "b_recreated.txt").write_text("b v2\n")
    (tmp_path / "c_added.txt").write_text("c v2\n")
    (tmp_path / "z_gone.txt").unlink()
    git("add", "-A")
    git("commit", "-q", "-m", "later")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-2967-mutations.md", before=base, keep="pin.txt", green=green, command="true")
    before = tree()

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, tree()) == (2, before), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a record whose command is not found")
def test_3124_a_record_whose_command_is_not_found_exits_2_naming_the_pin_file_and_the_command_instead_of_needs_a_look(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-3124-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="no-such-runner-3124 ./...")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "touch guard.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, ran.stdout, "issue-3124-mutations.md" in ran.stderr, "no-such-runner-3124 ./..." in ran.stderr,
            (tmp_path / "guard.txt").read_bytes()) == (2, "", True, True, b"if guard\nmore\n"), ran.stdout + ran.stderr


@pytest.mark.process("git, make, and pin-recheck.sh run over a record whose make command finds no makefile")
def test_3124_a_record_whose_make_command_finds_no_makefile_exits_2_naming_the_pin_file_and_the_command_instead_of_needs_a_look(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-3124-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="make")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "touch guard.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, ran.stdout, "issue-3124-mutations.md" in ran.stderr, "make" in ran.stderr,
            (tmp_path / "guard.txt").read_bytes()) == (2, "", True, True, b"if guard\nmore\n"), ran.stdout + ran.stderr


@pytest.mark.process("git, make, and pin-recheck.sh run over a record whose make command has a makefile and a failing target")
def test_3124_a_record_whose_make_command_has_a_makefile_but_a_failing_target_prints_needs_a_look_and_exits_0(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / "Makefile").write_text("test:\n\t@false\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-3124-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="make test")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "touch guard.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, "needs a look" in ran.stdout and "guard.txt" in ran.stdout,
            (tmp_path / "guard.txt").read_bytes()) == (0, True, b"if guard\nmore\n"), ran.stdout + ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a range that edits a recorded file and deletes the test its command names")
def test_3151_a_pin_whose_named_test_the_range_deletes_is_retired_exits_3_and_runs_nothing(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_guard.py").write_text("def test_g(): pass\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-835-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="touch ran.witness TESTS=tests/test_guard.py")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    git("rm", "-q", "tests/test_guard.py")
    git("commit", "-q", "-am", "edit guard.txt and delete its test")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    retired = [line for line in ran.stdout.splitlines() if line.startswith("retired:")]
    assert (ran.returncode, len(retired) == 1 and all(
        word in retired[0] for word in ("issue-835-mutations.md", "guard.txt", "tests/test_guard.py")),
        (tmp_path / ".tdd" / "pin-recheck-ok").exists(), (tmp_path / "ran.witness").exists()) == (
        3, True, True, False), ran.stderr
