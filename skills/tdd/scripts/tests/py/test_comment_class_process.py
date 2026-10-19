"""Cases for comment-class.sh that start the real entry point."""
import importlib
import subprocess

import pytest

from conftest import SCRIPTS


@pytest.mark.process("comment-class.sh run through a symlink to the skill directory from another working directory")
def test_cli_run_through_a_symlink_to_the_skill_directory_from_another_cwd_prints_the_same_lines_and_exit_code_as_in_place(tmp_path, run_cli):
    comment_class = importlib.import_module("veri.comment_class")
    linked_file = tmp_path / "linked.sh"
    linked_file.write_text("# a comment in code\ncat > out.txt <<EOF\n# written\nEOF\n")
    (tmp_path / "elsewhere").mkdir()
    (tmp_path / "linked-skill").symlink_to(SCRIPTS.parent, target_is_directory=True)

    in_place = run_cli(comment_class, [str(linked_file)])
    ran = subprocess.run(
        [str(tmp_path / "linked-skill" / "scripts" / "comment-class.sh"), str(linked_file)],
        cwd=tmp_path / "elsewhere", capture_output=True, text=True,
    )

    assert in_place == (0, f"{linked_file}:1:1\n{linked_file}:3:2\n", "")
    assert (ran.returncode, ran.stdout, ran.stderr) == in_place
