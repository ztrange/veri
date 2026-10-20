"""Cases for next-unchecked.sh that start the real entry point."""
import importlib
import subprocess

import pytest

from conftest import SCRIPTS, ViaStdin

LEDGER = (
    "# Plan for #42\n"
    "\n"
    "- [x] add the slugify lowercasing\n"
    "- [ ] collapse non-alphanumerics to a single hyphen\n"
    "- [ ] strip leading and trailing hyphens"
)


@pytest.mark.process("next-unchecked.sh run through a symlink to the skill directory from another working directory")
def test_cli_run_through_a_symlink_to_the_skill_directory_from_another_cwd_answers_as_it_does_in_place(
        tmp_path, run_cli):
    next_unchecked = importlib.import_module("veri.next_unchecked")
    (tmp_path / "linked-skill").symlink_to(SCRIPTS.parent, target_is_directory=True)
    (tmp_path / "elsewhere").mkdir()
    linked = str(tmp_path / "linked-skill" / "scripts" / "next-unchecked.sh")

    in_place = run_cli(ViaStdin(next_unchecked, LEDGER), [], cwd=SCRIPTS)
    ran = subprocess.run([linked], cwd=tmp_path / "elsewhere", input=LEDGER,
                         capture_output=True, text=True)

    assert (ran.returncode, ran.stdout, ran.stderr) == in_place
    assert in_place == (0, "collapse non-alphanumerics to a single hyphen\n", "")
