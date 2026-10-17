"""Cases for veri/tier_usual.py that start a real process: a symlinked entry point."""
import json
import subprocess
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parents[3]
IN_PLACE = SKILL_DIR / "scripts" / "tier-usual.sh"


def _event(event, tier, seconds):
    return json.dumps({"ts": 1700000000, "issue": "342", "actor": "developer", "phase": "green",
                       "step": "1", "event": event, "attempt": "1", "skill_commit": "abc1234",
                       "tier": tier, "suites": "one.test.sh", "seconds": seconds})


@pytest.mark.process("tier-usual.sh run through a symlink to the skill directory from another working directory")
def test_a_shim_run_through_a_symlink_and_from_another_cwd_answers_as_in_place_for_a_tier_and_for_no_argument(
        tmp_path):
    for place in ("here", "elsewhere"):
        (tmp_path / place / ".tdd").mkdir(parents=True)
        (tmp_path / place / ".tdd" / "events.jsonl").write_text("".join(_event(*e) + "\n" for e in [
            ("test-run", "fast", "3"),
            ("test-run", "all", "900"),
            ("test-run", "fast", "1"),
            ("test-run", "fast", "2"),
        ]))
    (tmp_path / "linked-skill").symlink_to(SKILL_DIR, target_is_directory=True)
    linked = tmp_path / "linked-skill" / "scripts" / "tier-usual.sh"

    def run(script, cwd, *argv):
        done = subprocess.run([str(script), *argv], cwd=cwd, stdin=subprocess.DEVNULL, capture_output=True)
        return done.returncode, done.stdout

    assert run(IN_PLACE, tmp_path / "here", "fast") == (0, b"2.0\n")
    assert run(linked, tmp_path / "elsewhere", "fast") == (0, b"2.0\n")
    assert run(IN_PLACE, tmp_path / "here") == (2, b"")
    assert run(linked, tmp_path / "elsewhere") == (2, b"")
