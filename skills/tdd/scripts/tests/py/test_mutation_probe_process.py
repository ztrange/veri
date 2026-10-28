"""Medium cases for mutation-probe.sh: the shim and the command it runs, started for real."""
import subprocess
from pathlib import Path

import pytest

PROBE = Path(__file__).resolve().parents[2] / "mutation-probe.sh"


@pytest.mark.process("mutation-probe.sh and the sh command it runs against the edited fixture")
def test_command_sees_the_edited_content_and_a_failing_command_exits_0(tmp_path):
    target = tmp_path / "target.txt"
    target.write_text("keep alpha keep\n")
    witness = tmp_path / "witness.txt"
    result = subprocess.run(
        [str(PROBE), str(target), "alpha", "beta", "--", "sh", "-c", 'cp "$1" "$2"; exit 1', "sh", str(target), str(witness)],
        capture_output=True, text=True, timeout=20)
    assert (result.returncode, witness.read_text() if witness.exists() else None) == (0, "keep beta keep\n"), result.stderr
