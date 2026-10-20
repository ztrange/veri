"""Cases for ledger-steps.sh that start the real entry point."""
import importlib
import subprocess

import pytest

from conftest import SCRIPTS, ViaStdin

KINDS = (
    "# Plan for #42\n\nprose\n\n"
    "- [x] add lowercasing ⟦criterion 1⟧ ⟂ refactor pending\n"
    "- [ ] strip edge hyphens ⟦criterion 2⟧\n"
)
NONE = "# Plan for #42\n\n- [x] add lowercasing ⟦criterion 1⟧\n- [ ] a person reads the page ⟦human-owed⟧ ⟦criterion 2⟧\n"


@pytest.mark.process("ledger-steps.sh run through a symlink to the skill directory from another working directory")
def test_cli_run_through_a_symlink_to_the_skill_directory_from_another_cwd_answers_as_it_does_in_place(
        tmp_path, run_cli):
    ledger_steps = importlib.import_module("veri.ledger_steps")
    (tmp_path / "linked-skill").symlink_to(SCRIPTS.parent, target_is_directory=True)
    (tmp_path / "elsewhere").mkdir()
    linked = str(tmp_path / "linked-skill" / "scripts" / "ledger-steps.sh")

    answers = {}
    for ledger, argv in ((KINDS, []), (NONE, ["current"])):
        ran = subprocess.run([linked, *argv], cwd=tmp_path / "elsewhere", input=ledger,
                             capture_output=True, text=True)
        answers[ledger] = (run_cli(ViaStdin(ledger_steps, ledger), argv, cwd=SCRIPTS),
                           (ran.returncode, ran.stdout, ran.stderr))

    assert all(in_place == linked_run for in_place, linked_run in answers.values())
    assert answers[KINDS][0][0] == 0 and answers[KINDS][0][1].startswith("1\tdone\t")
    assert answers[NONE][0] == (3, "", "")
