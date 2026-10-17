"""Case for refactor-triage.sh that starts a real process: a symlinked entry point."""
import subprocess
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parents[3]
IN_PLACE = SKILL_DIR / "scripts" / "refactor-triage.sh"


@pytest.mark.process("refactor-triage.sh run through a symlink to the skill directory from another working directory")
def test_a_shim_run_through_a_symlink_and_from_another_cwd_answers_a_structural_a_cosmetic_only_and_an_empty_report_as_in_place(
        tmp_path):
    (tmp_path / "linked-skill").symlink_to(SKILL_DIR, target_is_directory=True)
    (tmp_path / "elsewhere").mkdir()
    reports = (
        (b"CANDIDATES: structural | extract the parser\nCANDIDATES: cosmetic | rename a local\n", 0),
        (b"CANDIDATES: cosmetic | rename a local\n", 3),
        (b"", 2),
    )
    problems = []
    for report, want in reports:
        in_place = subprocess.run([str(IN_PLACE)], input=report, capture_output=True)
        linked = subprocess.run([str(tmp_path / "linked-skill" / "scripts" / "refactor-triage.sh")],
                                input=report, cwd=tmp_path / "elsewhere", capture_output=True)
        if linked.returncode != want:
            problems.append("%r: want exit %s through the symlink, got %s" % (report, want, linked.returncode))
        if linked.returncode != in_place.returncode:
            problems.append("%r: linked exit %s, in place exit %s" % (report, linked.returncode, in_place.returncode))
        if linked.stdout != in_place.stdout:
            problems.append("%r: stdout differs through the symlink" % (report,))
        if linked.stderr != in_place.stderr:
            problems.append("%r: stderr differs through the symlink" % (report,))
    assert problems == []
