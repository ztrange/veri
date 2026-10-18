"""Cases for criterion-finished.sh that start the real entry point."""
import importlib
import io
import subprocess
import sys

import pytest

from conftest import SCRIPTS


class ViaStdin:
    def __init__(self, module, ledger):
        self.module, self.ledger = module, ledger

    def main(self, argv):
        sys.stdin = io.TextIOWrapper(io.BytesIO(self.ledger.encode()))
        return self.module.main(argv)


@pytest.mark.process("criterion-finished.sh run through a symlink to the skill directory from another working directory")
def test_cli_run_through_a_symlink_to_the_skill_directory_from_another_cwd_answers_as_it_does_in_place(
        tmp_path, run_cli):
    criterion_finished = importlib.import_module("veri.criterion_finished")
    (tmp_path / "skill").symlink_to(SCRIPTS.parent, target_is_directory=True)
    (tmp_path / "elsewhere").mkdir()
    linked = str(tmp_path / "skill" / "scripts" / "criterion-finished.sh")

    for ledger, argv, want in (
        ("- [x] a ⟦criterion 1⟧\n", ["1"], 0),
        ("- [ ] a ⟦criterion 1⟧\n", ["1"], 3),
        ("- [x] a ⟦criterion 1⟧\n", [], 2),
    ):
        in_place = run_cli(ViaStdin(criterion_finished, ledger), argv, cwd=SCRIPTS)
        ran = subprocess.run([linked, *argv], cwd=tmp_path / "elsewhere", input=ledger,
                             capture_output=True, text=True)
        assert (ran.returncode, ran.stdout, ran.stderr) == in_place
        assert in_place[0] == want
