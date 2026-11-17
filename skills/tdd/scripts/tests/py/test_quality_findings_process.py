"""test-quality.sh started as a script: the shim's entry-point contract (#4119)."""
import os
import subprocess

import pytest

from conftest import SCRIPTS

SCRIPT = SCRIPTS / "test-quality.sh"


@pytest.mark.process("test-quality.sh run as a script")
def test_the_shim_records_a_finding_with_0_and_refuses_an_undefined_case_with_2(tmp_path):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / "test_alpha.py").write_text("def test_adds():\n    assert 1 + 1 == 2\n")

    def record(report):
        ran = subprocess.run([str(SCRIPT), "record", "9"], cwd=tmp_path, input=report, capture_output=True,
                             text=True, env=os.environ)
        return ran.returncode, (tmp_path / ".tdd" / "issue-9-test-quality").read_text()

    recorded = record("FINDING: weak-assertion | test_alpha.py::test_adds | asserts arithmetic only\n")
    refused = record("FINDING: redundant | test_alpha.py::test_gone | gone\n")

    assert (recorded, refused) == (
        (0, "weak-assertion | test_alpha.py::test_adds | asserts arithmetic only\n"),
        (2, "weak-assertion | test_alpha.py::test_adds | asserts arithmetic only\n"))
