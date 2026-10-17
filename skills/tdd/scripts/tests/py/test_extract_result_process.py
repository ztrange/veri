"""Cases for veri/extract_result.py that start a real process: a symlinked entry point."""
import subprocess
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2]
STREAM = b'{"type":"system","subtype":"init"}\n{"type":"result","result":"VERDICT: PASS\\nREASON: linked."}'


@pytest.mark.process("extract-result.sh run through a symlink to the skill directory from another working directory")
def test_a_run_through_a_symlink_to_the_skill_directory_from_another_directory_answers_as_in_place(tmp_path):
    (tmp_path / "linked-skill").symlink_to(SCRIPTS.parent, target_is_directory=True)
    (tmp_path / "elsewhere").mkdir()

    in_place = subprocess.run([str(SCRIPTS / "extract-result.sh")], input=STREAM, capture_output=True)
    linked = subprocess.run([str(tmp_path / "linked-skill" / "scripts" / "extract-result.sh")], input=STREAM,
                            cwd=tmp_path / "elsewhere", capture_output=True)

    assert (linked.returncode, linked.stdout, linked.stderr) == (in_place.returncode, in_place.stdout, in_place.stderr)
    assert (in_place.returncode, in_place.stdout) == (0, b"VERDICT: PASS\nREASON: linked.\n")
