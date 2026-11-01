"""PRD 016: no tracked file still names a skill by its long name."""
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[5]
NAMES = ["bail", "coord", "dev", "file", "groom", "handoff", "judge", "merge", "plan", "report", "status", "stop"]


@pytest.mark.process("git grep over the repository this suite runs in")
def test_no_tracked_file_outside_specs_and_tdd_contains_veri_dash_a_renamed_skill_name():
    pattern = "veri" + "-(" + "|".join(NAMES) + ")([^[:alnum:]_]|$)"
    run = subprocess.run(
        ["git", "-C", str(ROOT), "grep", "-lIE", pattern, "--", ".", ":(exclude)specs", ":(exclude).tdd"],
        capture_output=True,
        text=True,
    )

    assert run.returncode in (0, 1), run.stderr
    assert run.stdout.split() == [], run.stdout


def _sweep(root):
    pattern = "veri" + "-(" + "|".join(NAMES) + ")([^[:alnum:]_]|$)"
    run = subprocess.run(
        ["git", "-C", str(root), "grep", "-lIE", pattern, "--", ".", ":(exclude)specs", ":(exclude).tdd"],
        capture_output=True,
        text=True,
    )
    assert run.returncode in (0, 1), run.stderr
    return run.stdout.split()


@pytest.mark.process("git init, add and grep on a throwaway repository")
def test_the_sweep_reports_a_tracked_file_holding_a_long_name_and_not_one_under_specs(tmp_path):
    (tmp_path / "specs").mkdir()
    (tmp_path / "README.md").write_text("run veri" + "-status now\n")
    (tmp_path / "specs" / "prd.md").write_text("history: veri" + "-bail\n")
    (tmp_path / "clean.md").write_text("run vstatus\n")
    for argv in (["init", "-q"], ["add", "."]):
        subprocess.run(["git", "-C", str(tmp_path), *argv], check=True, capture_output=True)

    assert _sweep(tmp_path) == ["README.md"]
