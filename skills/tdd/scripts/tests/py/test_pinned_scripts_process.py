"""Cases for pinned-scripts.sh that start a real process."""
import subprocess

import pytest

from conftest import SCRIPTS


@pytest.mark.process("pinned-scripts.sh run with no argument")
def test_pinned_scripts_with_no_argument_prints_usage_and_exits_2_2627(tmp_path):
    ran = subprocess.run(["/bin/sh", str(SCRIPTS / "pinned-scripts.sh")], cwd=tmp_path, capture_output=True,
                         text=True, stdin=subprocess.DEVNULL,
                         env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "PYTHONDONTWRITEBYTECODE": "1"})

    assert ran.returncode == 2, ran.stderr
    assert "usage: pinned-scripts.sh <n>" in ran.stderr
    assert ran.stdout == ""


@pytest.mark.process("pinned-scripts.sh run on a run whose pinned scripts copy exists")
def test_pinned_scripts_prints_the_directory_holding_the_runs_pinned_scripts_and_exits_0_2627(tmp_path):
    root = tmp_path.resolve() / "repo"
    (root / ".git").mkdir(parents=True)
    kept = root / ".tdd" / "pinned-scripts"
    kept.mkdir(parents=True)
    (kept / "status.sh").write_text("#!/bin/sh\n")

    ran = subprocess.run(["/bin/sh", str(SCRIPTS / "pinned-scripts.sh"), "2627"], cwd=root, capture_output=True,
                         text=True, stdin=subprocess.DEVNULL,
                         env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "PYTHONDONTWRITEBYTECODE": "1"})

    assert (ran.returncode, ran.stdout.strip()) == (0, str(kept)), ran.stderr


@pytest.mark.process("pinned-scripts.sh run from the main checkout for two different runs")
def test_pinned_scripts_from_the_main_checkout_prints_each_runs_own_worktree_directory_2627(tmp_path):
    root = tmp_path.resolve() / "repo"
    (root / ".git").mkdir(parents=True)

    def printed(n):
        ran = subprocess.run(["/bin/sh", str(SCRIPTS / "pinned-scripts.sh"), n], cwd=root, capture_output=True,
                             text=True, stdin=subprocess.DEVNULL,
                             env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "PYTHONDONTWRITEBYTECODE": "1"})
        return ran.returncode, ran.stdout.strip()

    assert (printed("41"), printed("42")) == (
        (0, str(root / ".tdd" / "wt" / "41" / ".tdd" / "pinned-scripts")),
        (0, str(root / ".tdd" / "wt" / "42" / ".tdd" / "pinned-scripts")),
    )


@pytest.mark.process("pinned-scripts.sh run on a run whose pinned scripts copy is gone")
def test_pinned_scripts_with_the_copy_absent_exits_2_naming_the_pin_and_the_git_archive_recovery_2627(tmp_path):
    root = tmp_path.resolve() / "repo"
    (root / ".git").mkdir(parents=True)
    state = root / ".tdd" / "wt" / "2627" / ".tdd"
    state.mkdir(parents=True)
    pin = "0123456789abcdef0123456789abcdef01234567"
    (state / "issue-2627-skill-commit").write_text(pin + "\n")

    ran = subprocess.run(["/bin/sh", str(SCRIPTS / "pinned-scripts.sh"), "2627"], cwd=root, capture_output=True,
                         text=True, stdin=subprocess.DEVNULL,
                         env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "PYTHONDONTWRITEBYTECODE": "1"})

    assert ran.returncode == 2, (ran.stdout, ran.stderr)
    assert pin in ran.stderr
    assert "git archive %s skills/tdd/scripts" % pin in ran.stderr
    assert ran.stdout == ""


@pytest.mark.process("pinned-scripts.sh run from the main checkout whose pin is recorded in its own .tdd")
def test_pinned_scripts_from_the_main_checkout_names_the_pin_recorded_there_when_the_copy_is_absent_2627(tmp_path):
    root = tmp_path.resolve() / "repo"
    (root / ".git").mkdir(parents=True)
    (root / ".tdd").mkdir()
    pin = "89abcdef0123456789abcdef0123456789abcdef"
    (root / ".tdd" / "issue-2627-skill-commit").write_text(pin + "\n")

    ran = subprocess.run(["/bin/sh", str(SCRIPTS / "pinned-scripts.sh"), "2627"], cwd=root, capture_output=True,
                         text=True, stdin=subprocess.DEVNULL,
                         env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "PYTHONDONTWRITEBYTECODE": "1"})

    assert ran.returncode == 2, (ran.stdout, ran.stderr)
    assert "git archive %s skills/tdd/scripts" % pin in ran.stderr
    assert ran.stdout == ""
