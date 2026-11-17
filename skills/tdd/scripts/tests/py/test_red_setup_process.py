"""red-setup.sh's entry point: the shim runs veri/red_setup.py, a real Red report's SETUP: line is recorded through the
real event journal, and worst reads that journal back into the owed file. The module's logic is tested in-process, in
tests/py/unit/test_red_setup.py."""
import subprocess

import pytest

from conftest import SCRIPTS

SETUP = str(SCRIPTS / "red-setup.sh")
LEDGER = ("# Plan for #7 — frob\n\n"
          "- [ ] zorblat frobs a nitz ⟦criterion 1⟧\n"
          "- [ ] zorblat refuses an empty nitz ⟦criterion 2⟧\n")


def run(*argv, cwd, stdin=""):
    ran = subprocess.run([SETUP, *argv], cwd=cwd, input=stdin, capture_output=True, text=True)
    return ran.returncode, ran.stdout, ran.stderr


@pytest.mark.process("red-setup.sh run as a script: record twice through the real event journal, then worst")
def test_record_then_worst_files_the_worst_verified_red_as_one_testability_row(tmp_path):
    (tmp_path / ".tdd").mkdir()
    ledger = tmp_path / ".tdd" / "issue-7.md"
    ledger.write_text(LEDGER)
    owed = tmp_path / ".tdd" / "issue-7-refactor-owed.md"

    first = run("record", "7", cwd=tmp_path, stdin="PREDICTION: MATCHED\nSETUP: 5 | five fakes\n")
    ledger.write_text(LEDGER.replace("- [ ] zorblat frobs", "- [x] zorblat frobs"))
    second = run("record", "7", cwd=tmp_path, stdin="PREDICTION: MATCHED\nSETUP: 1 | a spy\n")
    worst = run("worst", "7", str(owed), cwd=tmp_path)

    assert (first, second, worst, owed.read_text()) == (
        (0, "", ""), (0, "", ""), (0, "", ""),
        "not-done | testability | zorblat frobs a nitz ⟦criterion 1⟧: 5 stubs and setup (five fakes)\n")


@pytest.mark.process("red-setup.sh run as a script with no argument")
def test_the_shim_exits_2_with_its_usage_when_given_no_argument(tmp_path):
    code, out, err = run(cwd=tmp_path)

    assert (code, out, err.startswith("usage: red-setup.sh record")) == (2, "", True)
