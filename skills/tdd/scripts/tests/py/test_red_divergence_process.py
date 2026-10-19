"""Cases for red-divergence.sh that start the real entry point."""
import importlib
import io
import subprocess
import sys

import pytest

from conftest import SCRIPTS

REPORTS = (
    "FAIL_OUTPUT: f\nPREDICTED_FAILURE: p\nPREDICTION: DIVERGED\nPREDICTION_NOTE: n",
    "FAIL_OUTPUT: f\nPREDICTION: MATCHED",
    "FAIL_OUTPUT: f\n",
)


@pytest.mark.process("red-divergence.sh run through a symlink to the skill directory from another working directory")
def test_cli_run_through_a_symlink_to_the_skill_directory_from_another_cwd_answers_as_it_does_in_place(tmp_path, run_cli, monkeypatch):
    red_divergence = importlib.import_module("veri.red_divergence")
    report = None

    class Module:
        @staticmethod
        def main(argv):
            monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(report.encode()), newline="\n"))
            return red_divergence.main(argv)

    (tmp_path / "linked-skill").symlink_to(SCRIPTS.parent, target_is_directory=True)
    (tmp_path / "elsewhere").mkdir()
    linked = str(tmp_path / "linked-skill" / "scripts" / "red-divergence.sh")

    results = []
    for report in REPORTS:
        in_place = run_cli(Module, [], cwd=SCRIPTS)
        ran = subprocess.run([linked], cwd=tmp_path / "elsewhere", input=report, capture_output=True, text=True)
        results.append(((ran.returncode, ran.stdout, ran.stderr), in_place))

    assert all(linked_answer == in_place for linked_answer, in_place in results)
    assert [in_place[0] for _, in_place in results] == [0, 3, 2]
