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
