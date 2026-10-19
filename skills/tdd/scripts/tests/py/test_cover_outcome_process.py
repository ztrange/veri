"""Cases for cover-outcome.sh that start the real entry point."""
import subprocess

import pytest

from conftest import SCRIPTS

REPORTS = (
    "some narration\nCOVERED: yes\nCAUGHT_BY: widget.test.sh: a stubbed widget stays blue\nMUTATION: widget.sh: painted the widget red",
    "some narration with no report lines at all",
)


@pytest.mark.process("cover-outcome.sh run through a symlink to the skill directory from another working directory")
def test_cli_run_through_a_symlink_to_the_skill_directory_from_another_cwd_answers_as_it_does_in_place(tmp_path):
    (tmp_path / "linked-skill").symlink_to(SCRIPTS.parent, target_is_directory=True)
    (tmp_path / "elsewhere").mkdir()
    linked = str(tmp_path / "linked-skill" / "scripts" / "cover-outcome.sh")

    def answer(script, cwd, report):
        ran = subprocess.run([script], cwd=cwd, input=report, capture_output=True, text=True)
        return ran.returncode, ran.stdout, ran.stderr

    for report in REPORTS:
        assert answer(linked, tmp_path / "elsewhere", report) == answer(str(SCRIPTS / "cover-outcome.sh"), SCRIPTS, report)
    assert answer(linked, tmp_path / "elsewhere", REPORTS[0])[0] == 0
    assert answer(linked, tmp_path / "elsewhere", REPORTS[1])[0] == 2
