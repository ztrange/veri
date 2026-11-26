"""Process cases for veri/wait_leaf.py: the ones that start a real process; the small cases are in unit/test_wait_leaf.py.
"""
import subprocess

import pytest

from conftest import INTERPRETER_VENV, SCRIPTS


@pytest.mark.process("wait-leaf.sh run through a symlink to the skills directory")
def test_a_run_through_a_symlink_to_the_skills_directory_reads_the_working_directorys_exit_file_and_answers_a_recorded_1(
        tmp_path):
    (tmp_path / "linked").symlink_to(SCRIPTS.parents[1], target_is_directory=True)
    (tmp_path / "caller" / ".tdd").mkdir(parents=True)
    (tmp_path / "caller" / ".tdd" / "via-link.exit").write_text("1\n")

    ran = subprocess.run([str(tmp_path / "linked" / "tdd" / "scripts" / "wait-leaf.sh"), "via-link", "0"],
                         cwd=tmp_path / "caller", stdin=subprocess.DEVNULL, capture_output=True, text=True,
                         env={"PATH": "/usr/bin:/bin", "VERI_VENV": INTERPRETER_VENV, "VERI_POLL": "0"})

    assert (ran.returncode, ran.stdout, ran.stderr) == (1, "", "")
    assert not (SCRIPTS / ".tdd" / "via-link.exit").exists()
