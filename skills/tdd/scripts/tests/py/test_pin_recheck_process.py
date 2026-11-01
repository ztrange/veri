"""Cases for pin-recheck.sh against a real git repository."""
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
