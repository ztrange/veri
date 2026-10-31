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
