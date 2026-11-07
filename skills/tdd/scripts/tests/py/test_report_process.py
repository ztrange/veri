"""Cases for report.sh that start the real entry point."""
import subprocess

import pytest

from conftest import SCRIPTS


@pytest.mark.process("report.sh run as a real /bin/sh shim with no argument")
def test_no_argument_prints_the_usage_line_on_stderr_and_exits_2():
    ran = subprocess.run([str(SCRIPTS / "report.sh")], capture_output=True, text=True, stdin=subprocess.DEVNULL)

    assert ran.returncode == 2
    assert ran.stdout == ""
    assert "report.sh" in ran.stderr
    assert "--report" in ran.stderr
