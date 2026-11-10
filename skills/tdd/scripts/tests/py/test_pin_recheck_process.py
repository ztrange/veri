"""Cases for pin-recheck.sh against a real git repository."""
import os
import subprocess

import pytest

from conftest import SCRIPTS

RECHECK = str(SCRIPTS / "pin-recheck.sh")


def record(path, **fields):
    path.write_text("".join(f"{name} {len(value)}\n{value}\n" for name, value in fields.items()) + "\n")


def main_disarmed_on_base(git, repo):
    (repo / "marker.txt").write_text("main\n")
    git("add", "marker.txt")
    git("commit", "-q", "-m", "main marker")
    git("update-ref", "refs/remotes/origin/main", "HEAD")
    (repo / "marker.txt").unlink()


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


@pytest.mark.process("git, and pin-recheck.sh run over a range with an origin/main base, for a pin that goes red under its mutation")
def test_3290_a_mutation_pin_red_under_its_mutation_at_head_with_an_origin_main_exits_0_and_prints_no_stale_line(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    git("add", "-A")
    git("commit", "-q", "-m", "main")
    git("update-ref", "refs/remotes/origin/main", "HEAD")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-835-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="sh -c \"echo result; grep -q 'if guard' guard.txt\"")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "touch guard.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, "stale" in ran.stdout + ran.stderr) == (0, False), ran.stdout + ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a range whose later commit disarms the recorded pin")
def test_2506_a_record_whose_command_stays_green_under_its_mutation_exits_1_naming_the_pin_and_restores_the_file(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    git("add", "-A")
    git("commit", "-q", "-m", "main")
    git("update-ref", "refs/remotes/origin/main", "HEAD")
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


@pytest.mark.process("git, and pin-recheck.sh run over a range with an origin/main base where the pin goes red under its mutation")
def test_3290_a_mutation_pin_green_under_its_mutation_at_head_but_red_at_the_base_names_the_pin_on_stderr_and_exits_1(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    git("add", "-A")
    git("commit", "-q", "-m", "main")
    git("update-ref", "refs/remotes/origin/main", "HEAD")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-835-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="sh -c \"grep -q 'if guard' guard.txt || grep -q safe guard.txt\"")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nsafe\n")
    git("commit", "-q", "-am", "later commit makes the test pass with the guard reverted")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, "pin stayed green under its mutation: guard.txt\n" in ran.stderr, "stale:" in ran.stdout) == (
        1, True, False), ran.stdout + ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a range with an origin/main base where the pin is green under its mutation")
def test_3290_a_mutation_pin_green_under_its_mutation_at_head_and_at_the_base_prints_the_stale_line_and_does_not_exit_1(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\nthrows\n")
    git("add", "-A")
    git("commit", "-q", "-m", "main")
    git("update-ref", "refs/remotes/origin/main", "HEAD")
    main = git("rev-parse", "HEAD")
    witness = tmp_path.parent / f"{tmp_path.name}.witness"
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-835-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command=f"sh -c \"grep -q 'if (true)' guard.txt && git rev-parse HEAD >> '{witness}'; grep -q throws guard.txt\"")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nthrows\nmore\n")
    git("commit", "-q", "-am", "touch guard.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    mutated_at = witness.read_text().split() if witness.exists() else []
    assert (ran.returncode != 1, "stale: .tdd/issue-835-mutations.md guard.txt\n" in ran.stdout, main in mutated_at) == (
        True, True, True), (ran.returncode, ran.stdout, ran.stderr, mutated_at)


@pytest.mark.process("git, and pin-recheck.sh run over a range with an origin/main base where the base-run mutation's command fails")
def test_3290_a_failing_base_run_of_the_mutation_leaves_the_files_byte_identical_and_removes_the_base_worktree(tmp_path):
    repo = tmp_path / "repo"
    scratch = tmp_path / "scratch"
    repo.mkdir()
    scratch.mkdir()

    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=repo,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (repo / "guard.txt").write_text("if guard\n")
    git("add", "-A")
    git("commit", "-q", "-m", "main")
    git("update-ref", "refs/remotes/origin/main", "HEAD")
    (repo / ".tdd").mkdir()
    record(repo / ".tdd" / "issue-835-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="sh -c \"grep -q 'if guard' guard.txt || grep -q safe guard.txt\"")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (repo / "guard.txt").write_text("if guard\nsafe\n")
    git("commit", "-q", "-am", "later commit")
    before = {p.name: p.read_bytes() for p in (repo / "guard.txt", repo / ".tdd" / "issue-835-mutations.md")}

    ran = subprocess.run(["sh", RECHECK, base], cwd=repo, capture_output=True, text=True, timeout=20,
                         env={**os.environ, "TMPDIR": str(scratch)})

    after = {p.name: p.read_bytes() for p in (repo / "guard.txt", repo / ".tdd" / "issue-835-mutations.md")}
    worktrees = [l for l in git("worktree", "list").splitlines() if l]
    assert (before == after, len(worktrees), sorted(p.name for p in scratch.iterdir()), git("status", "--porcelain")) == (
        True, 1, [], ""), (ran.returncode, ran.stdout, ran.stderr, worktrees)


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

    assert (ran.returncode, ran.stdout.startswith("needs a look: guard.txt"), len(ran.stdout.splitlines()),
            (tmp_path / "guard.txt").read_bytes()) == (0, True, 1, b"if guard\nmore\n"), ran.stderr


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

    assert (ran.returncode, ran.stdout.startswith("needs a look: guard.txt"), len(ran.stdout.splitlines()),
            (tmp_path / "guard.txt").read_bytes()) == (0, True, 1, b"if guard\nmore\n"), ran.stdout + ran.stderr


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
    (tmp_path / "guard.txt").write_text("if guard\n")
    git("add", "-A")
    git("commit", "-q", "-m", "main")
    git("update-ref", "refs/remotes/origin/main", "HEAD")
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

    assert (ran.returncode, ran.stdout.startswith("needs a look: guard.txt"), len(ran.stdout.splitlines()),
            (tmp_path / "guard.txt").read_bytes()) == (0, True, 1, b"if guard\nmore\n"), ran.stdout + ran.stderr


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
    main_disarmed_on_base(git, tmp_path)
    (tmp_path / "src.txt").write_text("fixed behaviour\n")
    (tmp_path / "pin.txt").write_text("pin v1\n")
    (tmp_path / ".tdd" / "notes.md").write_text("ledger v1\n")
    git("commit", "-q", "-am", "fix, pin and ledger")
    record(tmp_path / ".tdd" / "issue-2959-mutations.md", before=base, keep="pin.txt",
           command="grep -q 'pin v1' pin.txt && grep -q 'ledger v1' .tdd/notes.md && test ! -e marker.txt")

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
    main_disarmed_on_base(git, tmp_path)
    (tmp_path / "src.txt").write_text("fixed behaviour\n")
    (tmp_path / "pin.txt").write_text("pin v1\n")
    git("commit", "-q", "-am", "fix and pin")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-2959-mutations.md", before=base, keep="pin.txt",
           command="grep -q old src.txt && test ! -e marker.txt")

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
    main_disarmed_on_base(git, tmp_path)
    (tmp_path / "src.txt").write_text("fixed behaviour\n")
    (tmp_path / "pin.txt").write_text("pin v1\n")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "fix, pin and touch guard")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-2959-mutations.md", before=base, keep="pin.txt",
           command="grep -q old src.txt && test ! -e marker.txt")
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
    main_disarmed_on_base(git, tmp_path)
    (tmp_path / "src.txt").write_text("fixed behaviour\n")
    (tmp_path / "pin.txt").write_text("pin v1\n")
    (tmp_path / "z_new.txt").write_text("added later\n")
    git("add", "-A")
    git("commit", "-q", "-m", "fix, pin and add")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-2959-mutations.md", before=base, keep="pin.txt",
           command="test ! -e z_new.txt && test ! -e marker.txt")

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
    main_disarmed_on_base(git, tmp_path)
    (tmp_path / "src.txt").write_text("fixed behaviour\n")
    (tmp_path / "pin.txt").write_text("pin v1\n")
    (tmp_path / "z_new.txt").write_bytes(b"added \x00 later\n")
    git("add", "-A")
    git("commit", "-q", "-m", "fix, pin and add")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-2959-mutations.md", before=base, keep="pin.txt",
           command="grep -q old src.txt && test ! -e marker.txt")

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
    main_disarmed_on_base(git, tmp_path)
    git("rm", "-q", "gone.txt")
    (tmp_path / "pin.txt").write_text("pin v1\n")
    git("add", "-A")
    git("commit", "-q", "-m", "delete gone.txt and pin")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-2974-mutations.md", before=base, keep="pin.txt", command="test -e gone.txt && test ! -e marker.txt")

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
    main_disarmed_on_base(git, tmp_path)
    (tmp_path / "pin.txt").write_text("pin v1\n")
    git("commit", "-q", "-am", "touch the keep file")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-3017-mutations.md", before=base, keep="pin.txt",
           command="grep -q old src.txt && test ! -e marker.txt")

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
    main_disarmed_on_base(git, tmp_path)
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "x.sh").write_text("#!/bin/sh\necho x\n")
    (tmp_path / "scripts" / "x.sh").chmod(0o755)
    (tmp_path / "scripts" / "y.txt").write_text("plain\n")
    (tmp_path / "pin.txt").write_text("pin v1\n")
    git("add", "-A")
    git("commit", "-q", "-m", "add scripts and pin")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-3046-mutations.md", before=base, keep="pin.txt", command="true && test ! -e marker.txt")
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
    (tmp_path / "guard.txt").write_text("if guard\n")
    git("add", "-A")
    git("commit", "-q", "-m", "main")
    git("update-ref", "refs/remotes/origin/main", "HEAD")
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


@pytest.mark.process("git, and pin-recheck.sh run over a before/keep record whose before-state replay swaps files, one added after before and deleted by HEAD")
def test_2967_a_before_replay_that_swaps_files_leaves_every_file_byte_identical_and_answers_exit_1(tmp_path):
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
    main_disarmed_on_base(git, tmp_path)
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
    record(tmp_path / ".tdd" / "issue-2967-mutations.md", before=base, keep="pin.txt", green=green, command="true && test ! -e marker.txt")
    before = tree()

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, tree()) == (1, before), ran.stderr


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


@pytest.mark.process("git, and pin-recheck.sh run over a range that deletes one pin's test and leaves another pin green under its mutation")
def test_3151_a_retired_pin_beside_a_live_pin_that_stays_green_exits_1_the_live_pin_deciding(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "live.txt").write_text("if guard\n")
    git("add", "-A")
    git("commit", "-q", "-m", "main")
    git("update-ref", "refs/remotes/origin/main", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / "live.txt").write_text("if guard\nthrows\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_guard.py").write_text("def test_g(): pass\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-835-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="touch ran.witness TESTS=tests/test_guard.py")
    record(tmp_path / ".tdd" / "issue-836-mutations.md", file="live.txt", old="if guard", new="if (true)",
           command="grep -q throws live.txt")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    (tmp_path / "live.txt").write_text("if guard\nthrows\nmore\n")
    git("rm", "-q", "tests/test_guard.py")
    git("commit", "-q", "-am", "edit both files and delete one pin's test")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    retired = [line for line in ran.stdout.splitlines() if line.startswith("retired:")]
    assert (ran.returncode, len(retired) == 1 and "tests/test_guard.py" in retired[0],
            "live.txt" in ran.stdout + ran.stderr, (tmp_path / "ran.witness").exists()) == (
        1, True, True, False), ran.stdout + ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a range that deletes one pin's test and leaves another pin red under its mutation")
def test_3151_a_retired_pin_beside_a_live_pin_that_goes_red_exits_0_the_live_pin_deciding(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / "live.txt").write_text("if guard\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_guard.py").write_text("def test_g(): pass\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-835-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="touch ran.witness TESTS=tests/test_guard.py")
    record(tmp_path / ".tdd" / "issue-836-mutations.md", file="live.txt", old="if guard", new="if (true)",
           command="sh -c \"echo result; grep -q 'if guard' live.txt\"")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    (tmp_path / "live.txt").write_text("if guard\nmore\n")
    git("rm", "-q", "tests/test_guard.py")
    git("commit", "-q", "-am", "edit both files and delete one pin's test")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    retired = [line for line in ran.stdout.splitlines() if line.startswith("retired:")]
    assert (ran.returncode, len(retired) == 1 and "tests/test_guard.py" in retired[0],
            (tmp_path / "ran.witness").exists()) == (0, True, False), ran.stdout + ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a range that edits a pin's file while its named test is missing but not deleted by the range")
def test_3151_a_pin_whose_named_test_is_missing_at_head_but_not_deleted_by_the_range_exits_2_naming_the_path(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_guard.py").write_text("def test_g(): pass\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-835-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="sh -c \"echo result; touch ran.witness; grep -q 'if guard' guard.txt\" TESTS=tests/test_guard.py")
    git("add", "-A")
    git("commit", "-q", "-m", "add the test")
    git("rm", "-q", "tests/test_guard.py")
    git("commit", "-q", "-m", "remove the named test before the base")
    (tmp_path / "other.txt").write_text("x\n")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    git("checkout", "-q", "-b", "trunk")
    (tmp_path / "tests").mkdir(exist_ok=True)
    (tmp_path / "tests" / "test_guard.py").write_text("def test_g(): pass\n")
    git("add", "-A")
    git("commit", "-q", "-m", "origin/main brings the named test back")
    git("update-ref", "refs/remotes/origin/main", "HEAD")
    git("checkout", "-q", "-")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "edit the pinned file; the named test is missing here")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, "tests/test_guard.py" in ran.stderr, "retired:" in ran.stdout,
            (tmp_path / "ran.witness").exists()) == (2, True, False, False), ran.stdout + ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a range that deletes only some of the test files one pin names")
def test_3151_a_pin_naming_several_test_files_some_deleted_by_the_range_is_replayed_on_the_rest_without_a_retired_line(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_gone.py").write_text("def test_g(): pass\n")
    (tmp_path / "tests" / "test_kept.py").write_text("def test_k(): pass\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-835-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="sh -c 'echo result; echo \"$@\" > ran.args; grep -q \"if guard\" guard.txt' x "
                   "TESTS=tests/test_gone.py TESTS=tests/test_kept.py")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    git("rm", "-q", "tests/test_gone.py")
    git("commit", "-q", "-am", "edit the pinned file and delete one of its two tests")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    args = (tmp_path / "ran.args").read_text().strip() if (tmp_path / "ran.args").exists() else None
    assert (ran.returncode, "retired:" in ran.stdout, args) == (0, False, "TESTS=tests/test_kept.py"), \
        ran.stdout + ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a range that deletes a test file whose path prefixes another named test file")
def test_3151_a_deleted_test_path_that_prefixes_a_kept_one_leaves_the_kept_argument_intact_on_replay(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_a.py").write_text("def test_a(): pass\n")
    (tmp_path / "tests" / "test_a.py2").write_text("def test_a2(): pass\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-835-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="sh -c 'echo result; echo \"$@\" > ran.args; grep -q \"if guard\" guard.txt' x "
                   "TESTS=tests/test_a.py TESTS=tests/test_a.py2")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    git("rm", "-q", "tests/test_a.py")
    git("commit", "-q", "-am", "edit the pinned file and delete the shorter-named test")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    args = (tmp_path / "ran.args").read_text().strip() if (tmp_path / "ran.args").exists() else None
    assert (ran.returncode, args) == (0, "TESTS=tests/test_a.py2"), ran.stdout + ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a before record whose replay range names a file the checked range later deletes")
def test_3151_a_before_replay_over_a_file_added_after_before_and_deleted_by_head_answers_and_does_not_exit_2(tmp_path):
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
    green = git("rev-parse", "HEAD")
    git("rm", "-q", "z_new.txt")
    git("commit", "-q", "-m", "delete the added file")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-3128-mutations.md", before=base, keep="pin.txt", green=green,
           command="grep -q fixed src.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, (tmp_path / "z_new.txt").exists()) == (0, False), ran.stdout + ran.stderr


@pytest.mark.process("git, and pin-recheck run in-process over a before/keep record whose replayed command raises")
def test_3151_a_before_replay_whose_command_raises_mid_run_restores_every_file_byte_identical(tmp_path, monkeypatch, run_cli):
    import importlib
    pin_recheck = importlib.import_module("veri.pin_recheck")

    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()

    def tree():
        return {n: (tmp_path / n).read_bytes() for n in ("a_mod.txt", "c_added.txt", "z_gone.txt", "pin.txt")
                if (tmp_path / n).exists()}
    git("init", "-q")
    for n, text in (("a_mod.txt", "a v0\n"), ("z_gone.txt", "z v0\n"), ("pin.txt", "pin v0\n")):
        (tmp_path / n).write_text(text)
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "a_mod.txt").write_text("a v1\n")
    (tmp_path / "c_added.txt").write_text("c v1\n")
    (tmp_path / "z_gone.txt").unlink()
    (tmp_path / "pin.txt").write_text("pin v1\n")
    git("add", "-A")
    git("commit", "-q", "-m", "fix and pin")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-3151-mutations.md", before=base, keep="pin.txt", command="true")
    before = tree()

    def interrupted(command):
        assert tree() != before, "the replay had not swapped the files when the command ran"
        raise KeyboardInterrupt

    monkeypatch.setattr(pin_recheck, "run_captured", interrupted)
    with pytest.raises(KeyboardInterrupt):
        run_cli(pin_recheck, [base], cwd=tmp_path)

    assert tree() == before


@pytest.mark.process("git, and pin-recheck.sh run over a before/keep record whose named test the range deletes")
def test_3151_a_before_record_whose_named_test_the_range_deletes_is_retired_and_replays_nothing(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "pin.txt").write_text("pin v0\n")
    (tmp_path / "t_gone.txt").write_text("test v0\n")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "pin.txt").write_text("pin v1\n")
    git("rm", "-q", "t_gone.txt")
    git("commit", "-q", "-am", "pin and delete the test")
    (tmp_path / ".tdd").mkdir()
    ledger = tmp_path / ".tdd" / "issue-3151-mutations.md"
    record(ledger, before=base, keep="pin.txt", command="touch ran.witness; echo TESTS=t_gone.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, ran.stdout, (tmp_path / "ran.witness").exists()) == (
        3, "retired: .tdd/issue-3151-mutations.md pin.txt t_gone.txt\n", False), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a range that touches the file part of a pytest node id a pin names")
def test_3168_a_pin_naming_a_pytest_node_id_whose_file_exists_is_rechecked_by_its_file_and_does_not_exit_2(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_guard.py").write_text("# v0\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-3168-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="sh -c \"echo result; touch ran.witness; grep -q 'if guard' guard.txt\" TESTS=tests/test_guard.py::test_a_case")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    (tmp_path / "tests" / "test_guard.py").write_text("# v1\n")
    git("commit", "-q", "-am", "touch the pinned file and the test file")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode != 2, "named test missing" in ran.stderr) == (True, False), ran.stdout + ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a pin whose command quotes the TESTS= node id")
def test_3181_a_pin_whose_command_quotes_its_tests_node_id_is_rechecked_by_its_file_and_does_not_exit_2(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_guard.py").write_text("# v0\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-3181-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="bash -c 'echo result; touch ran.witness; grep -q \"if guard\" guard.txt; "
                   "echo make test TESTS=\"tests/test_guard.py::test_a_case\"'")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    (tmp_path / "tests" / "test_guard.py").write_text("# v1\n")
    git("commit", "-q", "-am", "touch the pinned file and the test file")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode != 2, "named test missing" in ran.stderr) == (True, False), ran.stdout + ran.stderr


def _repo_with_deleted_test(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "pin.txt").write_text("pin v0\n")
    (tmp_path / "t_gone.py").write_text("test v0\n")
    (tmp_path / "t_keep.py").write_text("test v0\n")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "pin.txt").write_text("pin v1\n")
    git("rm", "-q", "t_gone.py")
    git("commit", "-q", "-am", "pin and delete the test")
    (tmp_path / ".tdd").mkdir()
    return base


@pytest.mark.process("git, and pin-recheck.sh run over a before/keep record whose quoted named test the range deletes")
def test_3181_a_record_quoting_a_deleted_tests_node_id_is_retired_and_not_exit_2(tmp_path):
    base = _repo_with_deleted_test(tmp_path)
    record(tmp_path / ".tdd" / "issue-3181-mutations.md", before=base, keep="pin.txt",
           command="touch ran.witness; bash -c 'make test TESTS=\"t_gone.py::test_a_case\"'")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, ran.stdout, (tmp_path / "ran.witness").exists()) == (
        3, "retired: .tdd/issue-3181-mutations.md pin.txt t_gone.py::test_a_case\n", False), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a before/keep record naming a quoted deleted test beside a kept one")
def test_3181_a_quoted_deleted_test_beside_a_kept_one_is_dropped_from_the_replayed_command(tmp_path):
    base = _repo_with_deleted_test(tmp_path)
    record(tmp_path / ".tdd" / "issue-3181-mutations.md", before=base, keep="pin.txt",
           command="echo X TESTS=\"t_gone.py::test_a_case\" TESTS=\"t_keep.py::test_b_case\" > args.witness; false")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    witness = (tmp_path / "args.witness").read_text() if (tmp_path / "args.witness").exists() else None
    assert (ran.returncode != 2, witness is not None and "t_gone" not in witness and "t_keep" in witness) == (
        True, True), (ran.stdout, ran.stderr, witness)


@pytest.mark.process("git, and pin-recheck.sh run over a before-state pin that is green on its before-state at HEAD and on the base")
def test_3160_a_before_state_pin_green_on_its_before_state_at_head_and_on_the_base_is_stale_exits_0_and_leaves_the_tree_as_found(
        tmp_path):
    repo, scratch = tmp_path / "repo", tmp_path / "scratch"
    repo.mkdir()
    scratch.mkdir()

    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=repo,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (repo / "src.txt").write_text("old behaviour\n")
    (repo / "pin.txt").write_text("pin v0\n")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    git("update-ref", "refs/remotes/origin/main", "HEAD")
    (repo / "pin.txt").write_text("pin v1\n")
    git("commit", "-q", "-am", "touch the pin file, leaving the pin as it was")
    (repo / ".tdd").mkdir()
    record(repo / ".tdd" / "issue-3160-mutations.md", before=base, keep="pin.txt", command="sh -c \"grep -q old src.txt\" TESTS=src.txt")
    before = (git("worktree", "list"), git("status", "--porcelain"))

    ran = subprocess.run(["sh", RECHECK, base], cwd=repo, capture_output=True, text=True, timeout=20,
                         env={**os.environ, "TMPDIR": str(scratch)})

    assert (ran.returncode, ran.stdout, "pin stayed green" in ran.stderr, (repo / ".tdd" / "pin-recheck-ok").exists(),
            (git("worktree", "list"), git("status", "--porcelain")) == before, list(scratch.iterdir())) == (
        0, "stale: .tdd/issue-3160-mutations.md src.txt\n", False, True, True, []), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a pin this range disarmed beside a stale pin")
def test_3160_a_before_state_pin_red_on_the_base_and_green_at_head_beside_a_stale_pin_is_named_and_exits_1(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "src.txt").write_text("old behaviour\n")
    (tmp_path / "pin.txt").write_text("pin v0\n")
    (tmp_path / "stale.txt").write_text("stale v0\n")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    main_disarmed_on_base(git, tmp_path)
    (tmp_path / "pin.txt").write_text("pin v1\n")
    (tmp_path / "stale.txt").write_text("stale v1\n")
    git("commit", "-q", "-am", "touch both pin files")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-3160-a-mutations.md", before=base, keep="stale.txt", command="sh -c \"grep -q old src.txt\" TESTS=src.txt")
    record(tmp_path / ".tdd" / "issue-3160-b-mutations.md", before=base, keep="pin.txt",
           command="grep -q old src.txt && test ! -e marker.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, "pin stayed green on the before-state: pin.txt" in ran.stderr,
            "stayed green on the before-state: stale.txt" in ran.stderr, ran.stdout,
            (tmp_path / ".tdd" / "pin-recheck-ok").exists()) == (
        1, True, False, "stale: .tdd/issue-3160-a-mutations.md src.txt\n", False), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a stale before-state pin beside an old-format pin that goes red under its mutation")
def test_3160_a_stale_before_state_pin_beside_an_old_format_pin_that_goes_red_under_its_mutation_exits_0(tmp_path):
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
    git("update-ref", "refs/remotes/origin/main", "HEAD")
    (tmp_path / "pin.txt").write_text("pin v1\n")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "touch the pin file and guard")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-3160-mutations.md", before=base, keep="pin.txt", command="sh -c \"grep -q old src.txt\" TESTS=src.txt")
    record(tmp_path / ".tdd" / "issue-835-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="sh -c \"echo result; grep -q 'if guard' guard.txt\"")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, ran.stdout, "pin stayed green" in ran.stderr,
            (tmp_path / ".tdd" / "pin-recheck-ok").exists()) == (
        0, "stale: .tdd/issue-3160-mutations.md src.txt\n", False, True), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a stale before-state pin beside an old-format pin that stays green under its mutation")
def test_3160_a_stale_before_state_pin_beside_an_old_format_pin_that_stays_green_under_its_mutation_exits_1(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "src.txt").write_text("old behaviour\n")
    (tmp_path / "pin.txt").write_text("pin v0\n")
    (tmp_path / "guard.txt").write_text("if guard\n")
    git("add", "-A")
    git("commit", "-q", "-m", "main")
    git("update-ref", "refs/remotes/origin/main", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nthrows\n")
    git("commit", "-q", "-am", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "pin.txt").write_text("pin v1\n")
    (tmp_path / "guard.txt").write_text("if guard\nthrows\nsafe\n")
    git("commit", "-q", "-am", "touch the pin file and disarm guard")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-3160-mutations.md", before=base, keep="pin.txt", command="sh -c \"grep -q old src.txt\" TESTS=src.txt")
    record(tmp_path / ".tdd" / "issue-835-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="grep -q throws guard.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, "stale: .tdd/issue-3160-mutations.md src.txt\n" in ran.stdout,
            "pin stayed green" in ran.stderr and "pin.txt" in ran.stderr, "guard.txt" in ran.stdout + ran.stderr,
            (tmp_path / ".tdd" / "pin-recheck-ok").exists()) == (1, True, False, True, False), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a green before-state pin in a repository with no origin/main")
def test_3160_a_green_before_state_pin_in_a_repository_with_no_origin_main_exits_2_naming_the_unresolvable_base(tmp_path):
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
    git("commit", "-q", "-am", "touch the pin file")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-3160-mutations.md", before=base, keep="pin.txt", command="grep -q old src.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, "origin/main" in ran.stderr, "Traceback" in ran.stderr, "stale:" in ran.stdout,
            "pin stayed green" in ran.stderr) == (2, True, False, False, False), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a green before-state pin whose base worktree cannot be created")
def test_3160_a_green_before_state_pin_whose_base_worktree_cannot_be_created_exits_2_naming_the_worktree_creation(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "src.txt").write_text("old behaviour\n")
    (tmp_path / "pin.txt").write_text("pin v0\n")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    git("update-ref", "refs/remotes/origin/main", "HEAD")
    (tmp_path / "pin.txt").write_text("pin v1\n")
    git("commit", "-q", "-am", "touch the pin file")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-3160-mutations.md", before=base, keep="pin.txt", command="grep -q old src.txt")
    (tmp_path / ".git" / "worktrees").write_text("not a directory\n")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, "worktree" in ran.stderr, "CalledProcessError" in ran.stderr, "stale:" in ran.stdout,
            "pin stayed green" in ran.stderr, (tmp_path / ".tdd" / "pin-recheck-ok").exists()) == (
        2, True, False, False, False, False), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a stale before-state pin whose command names no TESTS= value")
def test_3160_a_stale_before_state_pin_whose_command_names_no_tests_value_names_its_keep_path(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "src.txt").write_text("old behaviour\n")
    (tmp_path / "pin.txt").write_text("pin v0\n")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    git("update-ref", "refs/remotes/origin/main", "HEAD")
    (tmp_path / "pin.txt").write_text("pin v1\n")
    git("commit", "-q", "-am", "touch the pin file, leaving the pin as it was")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-3160-mutations.md", before=base, keep="pin.txt", command="grep -q old src.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, ran.stdout) == (0, "stale: .tdd/issue-3160-mutations.md pin.txt\n"), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a range that edits a pin's file while its named test is missing at HEAD and on the base")
def test_3160_a_pin_whose_named_test_is_missing_at_head_and_on_the_base_and_not_deleted_is_stale_not_exit_2(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-835-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="sh -c \"echo result; touch ran.witness; grep -q 'if guard' guard.txt\" TESTS=tests/test_guard.py")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    git("update-ref", "refs/remotes/origin/main", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "edit the pinned file; the named test is missing everywhere")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, ran.stdout.startswith("stale: .tdd/issue-835-mutations.md"),
            "named test missing" in ran.stderr, (tmp_path / "ran.witness").exists()) == (
        0, True, False, False), ran.stdout + ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a green before-state pin whose replay on the base fails")
def test_3160_a_base_replay_that_fails_exits_2_and_still_removes_the_base_worktree(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "src.txt").write_text("old behaviour\n")
    (tmp_path / "pin.txt").write_text("pin v0\n")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "f.txt").write_text("a\n")
    git("add", "-A")
    git("commit", "-q", "-m", "before")
    before = git("rev-parse", "HEAD")
    git("rm", "-q", "-r", "sub")
    git("commit", "-q", "-m", "main drops sub")
    git("update-ref", "refs/remotes/origin/main", "HEAD")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "f.txt").write_text("c\n")
    (tmp_path / "pin.txt").write_text("pin v1\n")
    git("add", "-A")
    git("commit", "-q", "-m", "range restores sub and touches the pin file")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-3160-mutations.md", before=before, keep="pin.txt", command="grep -q old src.txt")
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    listed = git("worktree", "list")

    ran = subprocess.run(["sh", RECHECK, git("merge-base", "origin/main", "HEAD")], cwd=tmp_path,
                         capture_output=True, text=True, timeout=20, env={**os.environ, "TMPDIR": str(scratch)})

    assert (ran.returncode, git("worktree", "list"), list(scratch.iterdir())) == (2, listed, []), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a range whose later commit removes the recorded old text")
def test_3204_a_pin_whose_old_text_is_gone_prints_old_text_gone_as_its_reason_and_still_exits_0_with_the_receipt(tmp_path):
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
    (tmp_path / "guard.txt").write_text("if checked\nthrows\n")
    git("commit", "-q", "-am", "later commit rewrites the guard line")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, ran.stdout.splitlines(), (tmp_path / ".tdd" / "pin-recheck-ok").exists()) == (
        0, ["needs a look: guard.txt (old text gone)"], True), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a range where the recorded command fails before any mutation")
def test_3204_a_base_run_that_fails_prints_needs_a_look_with_its_reason_and_still_exits_0_with_the_receipt(tmp_path):
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

    assert (ran.returncode, "needs a look: guard.txt (base run failed)" in ran.stdout.splitlines(),
            (tmp_path / ".tdd" / "pin-recheck-ok").exists()) == (0, True, True), ran.stdout + ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a record whose mutated run and control run are both green")
def test_3204_a_pin_whose_mutated_and_control_runs_both_pass_names_that_reason_and_still_exits_0_with_the_receipt(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-3204-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="true")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "touch guard.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, ran.stdout, (tmp_path / ".tdd" / "pin-recheck-ok").exists()) == (
        0, "needs a look: guard.txt (mutation and control green)\n", True), ran.stdout + ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over three pins on one file, two sharing a reason and one holding another")
def test_3204_pins_sharing_a_file_and_a_reason_print_one_line_with_a_count_and_a_lone_reason_prints_none(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-3204-mutations.md", file="guard.txt", old="if gone", new="if (true)",
           command="true")
    record(tmp_path / ".tdd" / "issue-3204-more-mutations.md", file="guard.txt", old="if vanished", new="if (true)",
           command="true")
    record(tmp_path / ".tdd" / "issue-3204-third-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="false")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "touch guard.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, sorted(ran.stdout.splitlines()), (tmp_path / ".tdd" / "pin-recheck-ok").exists()) == (
        0, ["needs a look: guard.txt (base run failed)", "needs a look: guard.txt (old text gone) ×2"], True), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a record whose make command make rejects as a usage error")
def test_3204_a_pin_whose_make_command_make_rejects_as_a_usage_error_exits_2_naming_the_pin_file_and_command_with_no_usage_or_receipt(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / "x").mkdir()
    (tmp_path / ".tdd").mkdir()
    command = "make test TESTS=./x -run TestFoo"
    record(tmp_path / ".tdd" / "issue-3204-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command=command)
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "touch guard.txt")
    bindir = tmp_path.parent / (tmp_path.name + "-bin")
    bindir.mkdir()
    (bindir / "make").write_text("#!/bin/sh\n"
                                 "echo 'make: invalid option -- u' >&2\n"
                                 "echo 'Usage: make [options] [target] ...' >&2\n"
                                 "echo 'Options:' >&2\n"
                                 "exit 2\n")
    (bindir / "make").chmod(0o755)

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20,
                         env={**os.environ, "PATH": f"{bindir}:{os.environ['PATH']}"})

    assert (ran.returncode, "issue-3204-mutations.md" in ran.stderr, command in ran.stderr,
            "Usage:" in ran.stderr, (tmp_path / ".tdd" / "pin-recheck-ok").exists()) == (
        2, True, True, False, False), ran.stdout + ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a record whose make command exits 1 printing make's usage words")
def test_3204_a_make_command_that_exits_1_printing_invalid_option_stays_a_base_run_failed_needs_a_look_and_exits_0(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-3204-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="make test")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "touch guard.txt")
    bindir = tmp_path.parent / (tmp_path.name + "-bin")
    bindir.mkdir()
    (bindir / "make").write_text("#!/bin/sh\n"
                                 "echo 'invalid option -- u' >&2\n"
                                 "echo 'Usage: make [options] [target] ...' >&2\n"
                                 "exit 1\n")
    (bindir / "make").chmod(0o755)

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20,
                         env={**os.environ, "PATH": f"{bindir}:{os.environ['PATH']}"})

    assert (ran.returncode, ran.stdout.splitlines(), (tmp_path / ".tdd" / "pin-recheck-ok").exists()) == (
        0, ["needs a look: guard.txt (base run failed)"], True), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a record whose make command exits 2 printing only one of make's usage-error signs")
def test_3204_a_make_exit_2_printing_only_invalid_option_or_only_its_usage_still_exits_2_naming_the_pin_file_and_command(tmp_path):
    outcomes = {}
    for name, stderr_line in (("invalid", "make: invalid option -- u"), ("usage", "Usage: make [options] [target] ...")):
        repo = tmp_path / name
        repo.mkdir()

        def git(*words):
            return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=repo,
                                  capture_output=True, text=True, timeout=20, check=True).stdout.strip()
        git("init", "-q")
        (repo / "guard.txt").write_text("if guard\n")
        (repo / "x").mkdir()
        (repo / ".tdd").mkdir()
        record(repo / ".tdd" / "issue-3204-mutations.md", file="guard.txt", old="if guard", new="if (true)",
               command="make test TESTS=./x -run TestFoo")
        git("add", "-A")
        git("commit", "-q", "-m", "base")
        base = git("rev-parse", "HEAD")
        (repo / "guard.txt").write_text("if guard\nmore\n")
        git("commit", "-q", "-am", "touch guard.txt")
        bindir = tmp_path / (name + "-bin")
        bindir.mkdir()
        (bindir / "make").write_text(f"#!/bin/sh\necho '{stderr_line}' >&2\nexit 2\n")
        (bindir / "make").chmod(0o755)

        ran = subprocess.run(["sh", RECHECK, base], cwd=repo, capture_output=True, text=True, timeout=20,
                             env={**os.environ, "PATH": f"{bindir}:{os.environ['PATH']}"})
        outcomes[name] = (ran.returncode, "issue-3204-mutations.md" in ran.stderr,
                          "make test TESTS=./x -run TestFoo" in ran.stderr)

    assert outcomes == {"invalid": (2, True, True), "usage": (2, True, True)}


@pytest.mark.process("git, and pin-recheck.sh run over a mutation pin whose file the range adds, so the base lacks it")
def test_3290_a_mutation_pin_green_under_its_mutation_whose_file_is_absent_on_the_base_is_not_stale_and_exits_1_without_a_traceback(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "other.txt").write_text("one\n")
    git("add", "-A")
    git("commit", "-q", "-m", "main")
    git("update-ref", "refs/remotes/origin/main", "HEAD")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-835-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="sh -c \"grep -q throws guard.txt\"")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nthrows\n")
    git("add", "-A")
    git("commit", "-q", "-m", "range adds guard.txt")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, "pin stayed green under its mutation: guard.txt\n" in ran.stderr, "Traceback" in ran.stderr,
            "stale:" in ran.stdout) == (1, True, False, False), ran.stdout + ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a green mutation pin whose base worktree cannot be created")
def test_3290_a_mutation_pin_green_under_its_mutation_whose_base_worktree_cannot_be_created_exits_2_and_is_not_read_as_a_disarm(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\nthrows\n")
    (tmp_path / "other.txt").write_text("one\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-835-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="sh -c \"grep -q throws guard.txt\"")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    git("update-ref", "refs/remotes/origin/main", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nthrows\nmore\n")
    git("commit", "-q", "-am", "range touches guard.txt")
    (tmp_path / ".git" / "worktrees").write_text("not a directory\n")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, "worktree" in ran.stderr, "pin stayed green" in ran.stderr, "stale:" in ran.stdout,
            "Traceback" in ran.stderr) == (2, True, False, False, False), ran.stdout + ran.stderr


@pytest.mark.process("git, tick-ledger.sh --unpinnable, then pin-recheck.sh over a range touching the pinned file")
def test_3289_a_pin_dropped_by_an_unpinnable_retire_is_not_reported_as_base_run_failed(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_thing.py").write_text("def test_other():\n    pass\n")
    (tmp_path / "Makefile").write_text("test:\n\t@true\n")
    (tmp_path / ".tdd").mkdir()
    ledger = tmp_path / ".tdd" / "issue-42.md"
    ledger.write_text("# Plan for #42\n\n- [ ] a one ⟦criterion 1⟧\n")
    record(tmp_path / ".tdd" / "issue-42-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="false TESTS=tests/test_thing.py::test_never_written")
    reason = tmp_path / "reason.txt"
    reason.write_text("VERDICT: REJECT\nREASON: the hand mutation stays green\n")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "touch guard.txt")
    retired = subprocess.run(["sh", str(SCRIPTS / "tick-ledger.sh"), "--unpinnable", str(reason), "--case",
                              "tests/test_thing.py::test_other", str(ledger), "a one"],
                             cwd=tmp_path, capture_output=True, text=True, timeout=20, env={**os.environ, "VERI_ISSUE": "42"})

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (retired.returncode, "base run failed" in ran.stdout + ran.stderr) == (0, False), retired.stderr + ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a range whose ledger step declares a pin retired while its test file survives")
def test_3323_a_pin_whose_test_survives_and_a_ledger_step_declares_retired_is_not_replayed_and_exits_3(tmp_path):
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
    (tmp_path / ".tdd" / "issue-900.md").write_text(
        "- [x] add the method\n  retire-pin: .tdd/issue-835-mutations.md guard.txt -- a later design adds it on purpose\n")
    git("add", "-A")
    git("commit", "-q", "-m", "edit guard.txt and declare its pin retired")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    retired = [line for line in ran.stdout.splitlines() if line.startswith("retired:")]
    assert (ran.returncode, retired, (tmp_path / ".tdd" / "pin-recheck-ok").exists(),
            (tmp_path / "ran.witness").exists()) == (
        3, ["retired: .tdd/issue-835-mutations.md guard.txt a later design adds it on purpose"], True, False), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a range whose ledger step declares a pin retired while its test file survives")
def test_3323_a_retired_pin_gains_a_retired_line_with_the_reason_that_the_record_readers_still_parse(tmp_path):
    from veri.pin_recheck import records

    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_guard.py").write_text("def test_g(): pass\n")
    (tmp_path / ".tdd").mkdir()
    fields = dict(file="guard.txt", old="if guard", new="if (true)", command="touch ran.witness TESTS=tests/test_guard.py")
    mutations = tmp_path / ".tdd" / "issue-835-mutations.md"
    record(mutations, **fields)
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    (tmp_path / ".tdd" / "issue-900.md").write_text(
        "- [x] add the method\n  retire-pin: .tdd/issue-835-mutations.md guard.txt -- a later design adds it on purpose\n")
    git("add", "-A")
    git("commit", "-q", "-m", "edit guard.txt and declare its pin retired")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, records(mutations.read_text())) == (
        3, [{**fields, "retired": "a later design adds it on purpose"}]), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a range whose ledger step declares a pin retired in one of two record files")
def test_3323_retiring_a_pin_in_one_record_file_leaves_the_other_record_file_untouched(tmp_path):
    from veri.pin_recheck import records

    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / "other.txt").write_text("if other\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_guard.py").write_text("def test_g(): pass\n")
    (tmp_path / ".tdd").mkdir()
    mine = dict(file="guard.txt", old="if guard", new="if (true)", command="touch ran.witness TESTS=tests/test_guard.py")
    theirs = dict(file="other.txt", old="if other", new="if (true)", command="touch ran.witness TESTS=tests/test_guard.py")
    first = tmp_path / ".tdd" / "issue-835-mutations.md"
    second = tmp_path / ".tdd" / "issue-836-mutations.md"
    record(first, **mine)
    record(second, **theirs)
    untouched = second.read_text()
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    (tmp_path / ".tdd" / "issue-900.md").write_text(
        "- [x] add the method\n  retire-pin: .tdd/issue-835-mutations.md guard.txt -- a later design adds it on purpose\n")
    git("add", "-A")
    git("commit", "-q", "-m", "edit guard.txt and declare its pin retired")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, records(first.read_text()), second.read_text()) == (
        3, [{**mine, "retired": "a later design adds it on purpose"}], untouched), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a range whose ledger step declares a pin retired while its test file survives")
def test_3323_retiring_a_declared_pin_writes_exactly_one_pin_retired_event_carrying_the_reason(tmp_path):
    import json

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
    (tmp_path / ".tdd" / "issue-900.md").write_text(
        "- [x] add the method\n  retire-pin: .tdd/issue-835-mutations.md guard.txt -- a later design adds it on purpose\n")
    git("add", "-A")
    git("commit", "-q", "-m", "edit guard.txt and declare its pin retired")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    log = tmp_path / ".tdd" / "events.jsonl"
    events = [json.loads(line) for line in log.read_text().splitlines()] if log.is_file() else []
    retired = [e.get("reason") for e in events if e.get("event") == "pin-retired"]
    assert (ran.returncode, retired) == (3, ["a later design adds it on purpose"]), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run twice over a range whose ledger step declares a pin retired while its test file survives")
def test_3323_a_second_run_after_a_pin_was_retired_neither_replays_it_nor_writes_a_second_pin_retired_event(tmp_path):
    import json

    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_guard.py").write_text("def test_g(): pass\n")
    (tmp_path / ".tdd").mkdir()
    mutations = tmp_path / ".tdd" / "issue-835-mutations.md"
    record(mutations, file="guard.txt", old="if guard", new="if (true)",
           command="touch ran.witness TESTS=tests/test_guard.py")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    (tmp_path / ".tdd" / "issue-900.md").write_text(
        "- [x] add the method\n  retire-pin: .tdd/issue-835-mutations.md guard.txt -- a later design adds it on purpose\n")
    git("add", "-A")
    git("commit", "-q", "-m", "edit guard.txt and declare its pin retired")

    first = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)
    after_first = mutations.read_text()
    second = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    log = tmp_path / ".tdd" / "events.jsonl"
    events = [json.loads(line) for line in log.read_text().splitlines()] if log.is_file() else []
    retired = [e.get("reason") for e in events if e.get("event") == "pin-retired"]
    assert (first.returncode, second.returncode, retired, mutations.read_text() == after_first,
            (tmp_path / "ran.witness").exists()) == (
        3, 3, ["a later design adds it on purpose"], True, False), first.stderr + second.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a range that declares one pin retired and leaves another pin whose mutant stays green")
def test_3323_a_pin_not_declared_retired_beside_a_retired_one_is_still_replayed_and_exits_1(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    git("commit", "-q", "--allow-empty", "-m", "main")
    git("update-ref", "refs/remotes/origin/main", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / "other.txt").write_text("if other\nthrows\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_guard.py").write_text("def test_g(): pass\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-835-mutations.md", file="guard.txt", old="if guard", new="if (true)",
           command="touch ran.witness TESTS=tests/test_guard.py")
    record(tmp_path / ".tdd" / "issue-836-mutations.md", file="other.txt", old="if other", new="if (true)",
           command="grep -q throws other.txt")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    (tmp_path / "other.txt").write_text("if other\nthrows\nsafe\n")
    (tmp_path / ".tdd" / "issue-900.md").write_text(
        "- [x] add the method\n  retire-pin: .tdd/issue-835-mutations.md guard.txt -- a later design adds it on purpose\n")
    git("add", "-A")
    git("commit", "-q", "-m", "edit both files and declare the guard pin retired")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, "pin stayed green under its mutation: other.txt" in ran.stderr, (tmp_path / "ran.witness").exists(),
            (tmp_path / "other.txt").read_bytes()) == (
        1, True, False, b"if other\nthrows\nsafe\n"), ran.stdout + ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a range whose ledger step declares a pin retired with an empty reason")
def test_3323_a_retire_pin_declaration_with_an_empty_reason_exits_2_and_retires_nothing(tmp_path):
    import json

    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / ".tdd").mkdir()
    mutations = tmp_path / ".tdd" / "issue-835-mutations.md"
    record(mutations, file="guard.txt", old="if guard", new="if (true)",
           command="sh -c \"echo result; grep -q 'if guard' guard.txt\"")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    before = mutations.read_text()
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    (tmp_path / ".tdd" / "issue-900.md").write_text(
        "- [x] add the method\n  retire-pin: .tdd/issue-835-mutations.md guard.txt -- \n")
    git("add", "-A")
    git("commit", "-q", "-m", "edit guard.txt and declare its pin retired with no reason")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    log = tmp_path / ".tdd" / "events.jsonl"
    events = [json.loads(line) for line in log.read_text().splitlines()] if log.is_file() else []
    assert (ran.returncode, "retired:" in ran.stdout, mutations.read_text() == before,
            [e for e in events if e.get("event") == "pin-retired"], (tmp_path / ".tdd" / "pin-recheck-ok").exists()) == (
        2, False, True, [], False), ran.stdout + ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run over a range whose ledger step declares retired a file that holds no pin")
def test_3323_a_retire_pin_declaration_naming_a_file_that_holds_no_pin_exits_2_and_retires_nothing(tmp_path):
    import json

    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard.txt").write_text("if guard\n")
    (tmp_path / ".tdd").mkdir()
    mutations = tmp_path / ".tdd" / "issue-835-mutations.md"
    record(mutations, file="guard.txt", old="if guard", new="if (true)",
           command="sh -c \"echo result; grep -q 'if guard' guard.txt\"")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    before = mutations.read_text()
    (tmp_path / "guard.txt").write_text("if guard\nmore\n")
    (tmp_path / ".tdd" / "issue-900.md").write_text(
        "- [x] add the method\n  retire-pin: .tdd/issue-835-mutations.md other.txt -- a later design adds it on purpose\n")
    git("add", "-A")
    git("commit", "-q", "-m", "edit guard.txt and declare a pin retired that does not exist")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    log = tmp_path / ".tdd" / "events.jsonl"
    events = [json.loads(line) for line in log.read_text().splitlines()] if log.is_file() else []
    assert (ran.returncode, "retired:" in ran.stdout, mutations.read_text() == before,
            [e for e in events if e.get("event") == "pin-retired"], (tmp_path / ".tdd" / "pin-recheck-ok").exists()) == (
        2, False, True, [], False), ran.stdout + ran.stderr


@pytest.mark.process("git, and pin-recheck.sh replaying an event.py mutant through a copied timed-test-run.sh")
@pytest.mark.tree_audit("copies the veri scripts and lib trees into a temporary repo")
def test_3383_a_replayed_mutant_dropping_o_append_from_event_py_leaves_the_live_journal_append_only(tmp_path):
    import json
    import shutil

    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    scripts = tmp_path / "skills" / "tdd" / "scripts"
    scripts.mkdir(parents=True)
    shutil.copy(SCRIPTS / "timed-test-run.sh", scripts)
    shutil.copytree(SCRIPTS / "lib", scripts / "lib")
    shutil.copytree(SCRIPTS / "veri", scripts / "veri", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    git("init", "-q")
    (tmp_path / ".gitignore").write_text(".tdd/events.jsonl\n")
    (tmp_path / ".tdd").mkdir()
    wrapper = scripts / "timed-test-run.sh"
    record(tmp_path / ".tdd" / "issue-2749-mutations.md", file="skills/tdd/scripts/veri/event.py",
           old="os.O_WRONLY | os.O_APPEND | os.O_CREAT", new="os.O_WRONLY | os.O_CREAT",
           command=f"{wrapper} affected suite true")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    event_py = scripts / "veri" / "event.py"
    event_py.write_text(event_py.read_text() + "\n")
    git("commit", "-q", "-am", "touch event.py")
    journal = tmp_path / ".tdd" / "events.jsonl"
    before = "".join(json.dumps({"ts": 1794156370 + n, "event": "step", "note": "x" * 200}) + "\n" for n in range(3))
    journal.write_text(before)

    subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=60)

    after = journal.read_text()
    assert (after.startswith(before), after[len(before):] == "" or after.endswith("\n")) == (True, True), after


@pytest.mark.process("git, and pin-recheck.sh run over a range that touches the files two ledgers record")
def test_3363_without_a_ledger_flag_every_touched_record_of_every_ledger_is_replayed(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard-a.txt").write_text("if guard\n")
    (tmp_path / "guard-b.txt").write_text("if guard\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-835-mutations.md", file="guard-a.txt", old="if guard", new="if (true)",
           command="sh -c \"echo result; grep -q 'if guard' guard-a.txt && touch ran-a.witness\"")
    record(tmp_path / ".tdd" / "issue-836-mutations.md", file="guard-b.txt", old="if guard", new="if (true)",
           command="sh -c \"echo result; grep -q 'if guard' guard-b.txt && touch ran-b.witness\"")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard-a.txt").write_text("if guard\nmore\n")
    (tmp_path / "guard-b.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "touch both")

    ran = subprocess.run(["sh", RECHECK, base], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, (tmp_path / "ran-a.witness").exists(), (tmp_path / "ran-b.witness").exists()) == (0, True, True), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run with --ledger over a range that touches the files two ledgers record")
def test_3363_with_a_ledger_flag_only_that_ledgers_touched_records_are_replayed(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard-a.txt").write_text("if guard\n")
    (tmp_path / "guard-b.txt").write_text("if guard\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-835-mutations.md", file="guard-a.txt", old="if guard", new="if (true)",
           command="sh -c \"echo result; grep -q 'if guard' guard-a.txt && touch ran-a.witness\"")
    record(tmp_path / ".tdd" / "issue-836-mutations.md", file="guard-b.txt", old="if guard", new="if (true)",
           command="sh -c \"echo result; grep -q 'if guard' guard-b.txt && touch ran-b.witness\"")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard-a.txt").write_text("if guard\nmore\n")
    (tmp_path / "guard-b.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "touch both")

    ran = subprocess.run(["sh", RECHECK, base, "--ledger", ".tdd/issue-835-mutations.md"], cwd=tmp_path,
                         capture_output=True, text=True, timeout=20)

    assert (ran.returncode, (tmp_path / "ran-a.witness").exists(), (tmp_path / "ran-b.witness").exists()) == (0, True, False), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run with --ledger and no file over a range that touches a recorded file")
def test_3363_a_ledger_flag_with_no_file_after_it_exits_2_and_replays_nothing(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard-a.txt").write_text("if guard\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-835-mutations.md", file="guard-a.txt", old="if guard", new="if (true)",
           command="sh -c \"echo result; grep -q 'if guard' guard-a.txt && touch ran-a.witness\"")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard-a.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "touch guard-a")

    ran = subprocess.run(["sh", RECHECK, base, "--ledger"], cwd=tmp_path, capture_output=True, text=True, timeout=20)

    assert (ran.returncode, (tmp_path / "ran-a.witness").exists()) == (2, False), ran.stderr


@pytest.mark.process("git, and pin-recheck.sh run with --ledger naming a ledger whose recorded file the range leaves alone")
def test_3363_a_ledger_flag_whose_ledger_has_no_touched_record_exits_3_and_replays_nothing(tmp_path):
    def git(*words):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *words], cwd=tmp_path,
                              capture_output=True, text=True, timeout=20, check=True).stdout.strip()
    git("init", "-q")
    (tmp_path / "guard-a.txt").write_text("if guard\n")
    (tmp_path / "guard-b.txt").write_text("if guard\n")
    (tmp_path / ".tdd").mkdir()
    record(tmp_path / ".tdd" / "issue-835-mutations.md", file="guard-a.txt", old="if guard", new="if (true)",
           command="sh -c \"echo result; grep -q 'if guard' guard-a.txt && touch ran-a.witness\"")
    record(tmp_path / ".tdd" / "issue-836-mutations.md", file="guard-b.txt", old="if guard", new="if (true)",
           command="sh -c \"echo result; grep -q 'if guard' guard-b.txt && touch ran-b.witness\"")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "guard-b.txt").write_text("if guard\nmore\n")
    git("commit", "-q", "-am", "touch guard-b only")

    ran = subprocess.run(["sh", RECHECK, base, "--ledger", ".tdd/issue-835-mutations.md"], cwd=tmp_path,
                         capture_output=True, text=True, timeout=20)

    assert (ran.returncode, (tmp_path / "ran-a.witness").exists(), (tmp_path / "ran-b.witness").exists()) == (3, False, False), ran.stderr
