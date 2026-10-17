"""Process cases for veri/stop_requested.py, the module stop-requested.sh is a shim over."""
import subprocess

import pytest

from conftest import SCRIPTS


@pytest.mark.process("stop-requested.sh run through a symlink to the scripts directory from another working directory")
def test_cli_run_through_a_symlink_to_the_scripts_directory_reads_and_clears_the_working_directorys_stop_never_one_beside_the_skill(
        tmp_path):
    home, run = tmp_path / "home", tmp_path / "run"
    (home / ".tdd").mkdir(parents=True)
    (run / ".tdd").mkdir(parents=True)
    (home / "scripts").symlink_to(SCRIPTS)
    (home / ".tdd" / "stop").write_text("at-leaf\n")
    (run / ".tdd" / "stop").write_text("now\n")
    shim = str(home / "scripts" / "stop-requested.sh")

    read = subprocess.run([shim], capture_output=True, text=True, cwd=str(run))
    assert (read.returncode, read.stdout, read.stderr) == (0, "now\n", "")

    clear = subprocess.run([shim, "--clear"], capture_output=True, text=True, cwd=str(run))
    assert (clear.returncode, clear.stdout, clear.stderr) == (0, "", "")
    assert not (run / ".tdd" / "stop").exists()
    assert (home / ".tdd" / "stop").read_text() == "at-leaf\n"
