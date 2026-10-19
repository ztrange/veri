"""Cases for classify-bail.sh that start the real entry point."""
import importlib
import subprocess

import pytest

from conftest import SCRIPTS


@pytest.mark.process("classify-bail.sh run through a symlink to the skill directory from another working directory")
def test_cli_run_through_a_symlink_to_the_skill_directory_from_another_cwd_answers_as_it_does_in_place(
        tmp_path, run_cli):
    classify_bail = importlib.import_module("veri.classify_bail")
    (tmp_path / "linked-skill").symlink_to(SCRIPTS.parent, target_is_directory=True)
    (tmp_path / "elsewhere").mkdir()
    linked = str(tmp_path / "linked-skill" / "scripts" / "classify-bail.sh")

    results = {}
    for cause in ("killed-stuck", "bogus"):
        in_place = run_cli(classify_bail, [cause], cwd=SCRIPTS)
        ran = subprocess.run([linked, cause], cwd=tmp_path / "elsewhere", capture_output=True, text=True)
        results[cause] = ((ran.returncode, ran.stdout, ran.stderr), in_place)

    assert all(linked_answer == in_place for linked_answer, in_place in results.values())
    assert results["killed-stuck"][1] == (0, "system\n", "")
    assert results["bogus"][1][0] == 2
