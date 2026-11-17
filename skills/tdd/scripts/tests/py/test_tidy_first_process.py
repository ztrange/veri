"""Cases for veri/tidy_first.py that start a real process: the shim's entry-point contract (#4118)."""
import subprocess
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2]


@pytest.mark.process("tidy-first.sh run through its shim on a green report")
def test_4118_tidy_first_sh_answers_0_3_and_2_through_its_shim(tmp_path):
    (tmp_path / "route.py").write_text("def answer():\n    pass\n")

    def run(report):
        done = subprocess.run([str(SCRIPTS / "tidy-first.sh")], input=report.encode(), cwd=tmp_path, capture_output=True)
        return done.returncode, done.stdout.decode(), done.stderr.decode()

    assert run("TIDY_FIRST: Extract Function | route.py::answer | tangled\n") == (
        0, "apply Extract Function to `route.py::answer`, so the step after it is one small change;"
           " the step changes no behaviour and no test file ⟦diff-checked⟧\n", "")
    assert run("IMPL_PATH: route.py\n") == (3, "", "")
    assert run("TIDY_FIRST: Tidy | route.py::answer | x\n") == (
        2, "", "tidy-first.sh: names a refactoring SMELLS.md does not list: TIDY_FIRST: Tidy | route.py::answer | x\n")
