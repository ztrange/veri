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
           command="grep -q 'if guard' guard.txt")
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
