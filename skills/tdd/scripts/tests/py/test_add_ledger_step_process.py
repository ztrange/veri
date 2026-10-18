"""Cases for add-ledger-step.sh that start the real entry point."""
import importlib

import pytest

from conftest import SCRIPTS

import subprocess

SEED = (
    "# Plan for #42\n\n"
    "- [x] lowercase the slug ⟦criterion 1⟧\n"
    "- [ ] collapse to single hyphen ⟦criterion 2⟧\n"
    "- [ ] strip edge hyphens ⟦criterion 3⟧\n"
)


@pytest.mark.process("add-ledger-step.sh run through a symlink to the skill directory from another working directory")
def test_cli_run_through_a_symlink_to_the_skill_directory_from_another_cwd_rewrites_the_relative_ledger_as_it_does_in_place(
        tmp_path, run_cli):
    add_ledger_step = importlib.import_module("veri.add_ledger_step")
    (tmp_path / "linked-skill").symlink_to(SCRIPTS.parent, target_is_directory=True)
    linked = str(tmp_path / "linked-skill" / "scripts" / "add-ledger-step.sh")
    for name in ("in-place", "elsewhere"):
        (tmp_path / name).mkdir()
        (tmp_path / name / "l.md").write_text(SEED)

    answers = {}
    for anchor in ("collapse to single hyphen", "no such step"):
        argv = ["l.md", "after", anchor, "t"]
        ran = subprocess.run([linked, *argv], cwd=tmp_path / "elsewhere", stdin=subprocess.DEVNULL,
                             capture_output=True, text=True)
        answers[anchor] = (run_cli(add_ledger_step, argv, cwd=tmp_path / "in-place"),
                           (ran.returncode, ran.stdout, ran.stderr))

    after, none = answers["collapse to single hyphen"], answers["no such step"]
    assert after[0] == after[1] == (0, "", "")
    assert none[0] == none[1] == (2, "", "add-ledger-step.sh: anchor matches no single step: no such step\n")
    assert (tmp_path / "elsewhere" / "l.md").read_bytes() == (tmp_path / "in-place" / "l.md").read_bytes()
    assert "- [ ] t ⟦added⟧ ⟦criterion 2⟧\n" in (tmp_path / "elsewhere" / "l.md").read_text()
