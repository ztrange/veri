"""Cases for supervise.sh that start a real process."""
import os
import subprocess
import sys

import pytest

from conftest import SCRIPTS


@pytest.mark.process("supervise.sh run for real, supervising a real leaf that echoes its arguments and exits 1")
def test_supervise_sh_forwards_its_arguments_to_the_leaf_and_the_leafs_exit_code_as_its_own(tmp_path):
    ran = subprocess.run([str(SCRIPTS / "supervise.sh"), "develop-red", "sh", "-c", 'echo "$1"; exit 1', "sh", "forwarded"],
                         cwd=tmp_path, capture_output=True, text=True,
                         env={"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "VERI_STUCK_RETRIES": "0",
                              "VERI_POLL": "0.05", "PYTHONDONTWRITEBYTECODE": "1"})

    assert (ran.returncode, ran.stdout) == (1, "forwarded\n"), ran.stderr


@pytest.mark.process("supervise.sh and git run for real, from a subdirectory of a throwaway repo")
def test_supervise_sh_run_from_a_subdirectory_writes_its_run_state_under_the_repo_root_1895(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    sub = tmp_path / "skills"
    sub.mkdir()

    ran = subprocess.run([str(SCRIPTS / "supervise.sh"), "develop-red", "sh", "-c", "exit 0"],
                         cwd=sub, capture_output=True, text=True,
                         env={"PATH": os.path.dirname(sys.executable) + ":/usr/bin:/bin", "VERI_STUCK_RETRIES": "0",
                              "VERI_POLL": "0.05", "PYTHONDONTWRITEBYTECODE": "1"})

    assert ran.returncode == 0, ran.stderr
    assert (sorted(p.name for p in (tmp_path / ".tdd").glob("develop-red.*")), (sub / ".tdd").exists()) == (
        ["develop-red.exit", "develop-red.log", "develop-red.pid", "develop-red.rc"], False)
