"""In-process cases for veri/refactor_owed.py, the module refactor-owed.sh is a shim over."""
import pathlib
import subprocess

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]


@pytest.mark.process("refactor-owed.sh run through a symlink to the skill directory")
def test_cli_run_through_a_symlink_to_the_skill_directory_from_another_working_directory_answers_append_render_and_list_as_in_place_reading_the_owed_file_there(
        tmp_path):
    (tmp_path / "linked-skill").symlink_to(SCRIPTS.parent, target_is_directory=True)
    report = ("CANDIDATES: structural | extract the parser\n"
              "CANDIDATES: cosmetic | rename a local\n"
              "CANDIDATES: test-only | fold the fixtures\n")
    answers = {}
    for where, script in (("in-place", SCRIPTS / "refactor-owed.sh"),
                          ("elsewhere", tmp_path / "linked-skill" / "scripts" / "refactor-owed.sh")):
        cwd = tmp_path / where
        cwd.mkdir()
        answers[where] = [
            (ran.returncode, ran.stdout, ran.stderr)
            for ran in (subprocess.run([str(script), *argv], cwd=cwd, input=stdin, capture_output=True, text=True)
                        for argv, stdin in ((["append", "owed.md", "the step"], report),
                                            (["render", "owed.md"], ""), (["list", "owed.md"], "")))]

    elsewhere = tmp_path / "elsewhere" / "owed.md"
    assert elsewhere.read_text() == (tmp_path / "in-place" / "owed.md").read_text() != ""
    assert answers["elsewhere"] == answers["in-place"]
    assert [code for code, _, _ in answers["in-place"]] == [0, 0, 0]
    assert answers["in-place"][2][1] == "extract the parser\n"
