"""Process cases for detect-test-command.sh, the shim over veri/detect_test_command.py."""
import os
import subprocess

import pytest

SHIM = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "..", "detect-test-command.sh"))


@pytest.mark.process("detect-test-command.sh started through a symlink to the skill directory, from another working directory")
def test_shim_run_through_a_symlink_and_from_another_directory_prints_the_same_command_and_exit_code_as_in_place(tmp_path):
    repo = tmp_path / "linked-repo"
    repo.mkdir()
    (repo / "Makefile").write_text("test:\n\techo hi\n")
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    skill = os.path.dirname(os.path.dirname(SHIM))
    os.symlink(skill, str(tmp_path / "linked-skill"))
    linked_shim = str(tmp_path / "linked-skill" / "scripts" / "detect-test-command.sh")

    in_place = subprocess.run([SHIM], capture_output=True, text=True, cwd=str(repo))
    linked = subprocess.run([linked_shim, str(repo)], capture_output=True, text=True, cwd=str(elsewhere))

    assert (in_place.returncode, in_place.stdout, in_place.stderr) == (0, "make test\n", "")
    assert (linked.returncode, linked.stdout, linked.stderr) == (0, "make test\n", "")
