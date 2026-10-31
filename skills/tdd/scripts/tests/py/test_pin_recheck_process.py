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
