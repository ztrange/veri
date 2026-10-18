"""Cases for next-pending-refactor.sh that start the real entry point."""
import importlib
import io
import subprocess
import sys

import pytest

from conftest import SCRIPTS

LEDGER = (
    "# Plan for #42\n"
    "\n"
    "- [x] add the slugify lowercasing\n"
    "- [x] collapse non-alphanumerics to a single hyphen ⟂ refactor pending\n"
    "- [x] strip leading and trailing hyphens ⟂ refactor pending\n"
    "- [ ] percent-encode the remainder"
)


class ViaStdin:
    def __init__(self, module, ledger):
        self.module, self.ledger = module, ledger

    def main(self, argv):
        sys.stdin = io.TextIOWrapper(io.BytesIO(self.ledger.encode()))
        return self.module.main(argv)


@pytest.mark.process("next-pending-refactor.sh run through a symlink to the skill directory from another working directory")
def test_cli_run_through_a_symlink_to_the_skill_directory_from_another_cwd_answers_as_it_does_in_place(
        tmp_path, run_cli):
    next_pending_refactor = importlib.import_module("veri.next_pending_refactor")
    (tmp_path / "skill").symlink_to(SCRIPTS.parent, target_is_directory=True)
    (tmp_path / "elsewhere").mkdir()
    linked = str(tmp_path / "skill" / "scripts" / "next-pending-refactor.sh")

    in_place = run_cli(ViaStdin(next_pending_refactor, LEDGER), [], cwd=SCRIPTS)
    ran = subprocess.run([linked], cwd=tmp_path / "elsewhere", input=LEDGER,
                         capture_output=True, text=True)

    assert (ran.returncode, ran.stdout, ran.stderr) == in_place
    assert in_place == (0, "collapse non-alphanumerics to a single hyphen\n", "")
