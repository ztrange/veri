"""Cases for rerun-alone.sh that start the real entry point."""
import subprocess

import pytest

from conftest import SCRIPTS

RERUN = str(SCRIPTS / "rerun-alone.sh")


@pytest.mark.process("rerun-alone.sh run on red output that names no test file")
def test_red_output_naming_no_test_file_exits_1_and_runs_no_alone_command_2905(tmp_path):
    ran_log = tmp_path / "alone-ran"
    alone = tmp_path / "alone"
    alone.write_text(f"#!/bin/sh\necho \"$@\" >> {ran_log}\nexit 0\n")
    alone.chmod(0o755)
    red = tmp_path / "red-output.txt"
    red.write_text("Error: connection refused\n2 failed\n")

    ran = subprocess.run([RERUN, str(alone), str(red)], cwd=tmp_path, capture_output=True, text=True)

    assert ran.returncode == 1
    assert not ran_log.exists()
