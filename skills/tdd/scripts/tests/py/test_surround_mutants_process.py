"""Cases for surround-mutants.sh that start the real entry point over the real mutation-probe.sh."""
import os
import subprocess

import pytest

from conftest import SCRIPTS


@pytest.mark.process("surround-mutants.sh over the real mutation-probe.sh, mutating a scratch file and restoring it")
def test_cli_runs_each_row_through_the_real_probe_restoring_the_file_and_answers_red_survived_and_short_4108(tmp_path):
    program = tmp_path / "prog.txt"
    program.write_text("x = 1\ny = 2\n")
    report = tmp_path / "develop-surround.out"
    report.write_text("MUTANT: prog.txt | x = 1 | x = 9\nMUTANT: prog.txt | y = 2 | y = 3\n")
    caught = tmp_path / "caught.out"
    caught.write_text("MUTANT: prog.txt | x = 1 | x = 9\n")
    command = ["sh", "-c", "grep -q 'x = 1' prog.txt"]

    def run(*reports):
        env = {k: v for k, v in os.environ.items() if k != "VERI_MUTATION_RECORD"}
        ran = subprocess.run([str(SCRIPTS / "surround-mutants.sh"), *map(str, reports), "--", *command], cwd=tmp_path,
                             capture_output=True, text=True, stdin=subprocess.DEVNULL,
                             env=dict(env, VERI_SURROUND_MUTANTS="2"))
        return ran.returncode, ran.stdout

    assert run(report) == (1, "prog.txt | x = 1 | x = 9 red\nprog.txt | y = 2 | y = 3 survived\n")
    assert run(caught) == (1, "prog.txt | x = 1 | x = 9 red\nshort 1 of 2\n")
    assert program.read_text() == "x = 1\ny = 2\n"
