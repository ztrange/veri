"""Cases for veri/leaf_role.py that start a real process: a symlinked entry point."""
import subprocess
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parents[3]
IN_PLACE = SKILL_DIR / "scripts" / "leaf-role.sh"


@pytest.mark.process("leaf-role.sh run through a symlink to the skill directory from another working directory")
def test_a_shim_run_through_a_symlink_and_from_another_cwd_answers_as_in_place_for_develop_red_and_plan_red(
        tmp_path):
    (tmp_path / "skill").symlink_to(SKILL_DIR, target_is_directory=True)
    (tmp_path / "elsewhere").mkdir()
    problems = []
    for leaf, want in (("develop-red", 0), ("plan-red", 2)):
        in_place = subprocess.run([str(IN_PLACE), leaf], stdin=subprocess.DEVNULL, capture_output=True)
        linked = subprocess.run([str(tmp_path / "skill" / "scripts" / "leaf-role.sh"), leaf],
                                cwd=tmp_path / "elsewhere", stdin=subprocess.DEVNULL, capture_output=True)
        if in_place.returncode != want:
            problems.append("%s: want exit %s in place, got %s" % (leaf, want, in_place.returncode))
        if linked.returncode != in_place.returncode:
            problems.append("%s: want exit %s through the symlink, got %s"
                            % (leaf, in_place.returncode, linked.returncode))
        for stream in ("stdout", "stderr"):
            if getattr(linked, stream) != getattr(in_place, stream):
                problems.append("%s: std%s differs through the symlink" % (leaf, stream[3:]))
    assert problems == []
