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
