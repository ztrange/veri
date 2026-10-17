"""Cases for veri/exhausted_outcome.py that start a real process: a symlinked entry point."""
import subprocess
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2]


@pytest.mark.process("exhausted-outcome.sh run through a symlink to the skill directory from another working directory")
def test_a_run_through_a_symlink_to_the_skill_directory_from_another_directory_answers_as_in_place(tmp_path):
    (tmp_path / "linked-skill").symlink_to(SCRIPTS.parent, target_is_directory=True)
    (tmp_path / "elsewhere").mkdir()

    for report, want, want_code in ((b"SPLIT: a", b"a\n", 0), (b"NEEDS_USER: q", b"q\n", 1), (b"neither", b"", 3)):
        in_place = subprocess.run([str(SCRIPTS / "exhausted-outcome.sh")], input=report, capture_output=True)
        linked = subprocess.run([str(tmp_path / "linked-skill" / "scripts" / "exhausted-outcome.sh")], input=report,
                                cwd=tmp_path / "elsewhere", capture_output=True)
        assert (linked.returncode, linked.stdout, linked.stderr) == (in_place.returncode, in_place.stdout, in_place.stderr)
        assert (linked.returncode, linked.stdout) == (want_code, want)
