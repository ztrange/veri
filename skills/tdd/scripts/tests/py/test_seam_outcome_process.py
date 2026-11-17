"""Cases for seam-outcome.sh that start the real entry point."""
import subprocess

import pytest

from conftest import SCRIPTS


@pytest.mark.process("seam-outcome.sh run as the conductor runs it, a report on stdin")
def test_cli_answers_0_with_the_seam_1_with_the_reason_and_2_for_an_unreadable_report_4106():
    def answer(report):
        ran = subprocess.run([str(SCRIPTS / "seam-outcome.sh")], input=report, capture_output=True, text=True)
        return ran.returncode, ran.stdout

    assert [answer(r) for r in ("SEAM: bin/parse\nREACHES: yes\nPROOF: bin/parse calls parse()\n",
                                "SEAM: bin/parse\nREACHES: no\nPROOF: nothing reaches parse()\n",
                                "narration only\n")] == [
        (0, "bin/parse\n"), (1, "nothing reaches parse()\n"), (2, "")]
