"""prose-owed.sh waives a unit a pending skill-edit step names, on the run's branch."""
import json
import subprocess
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2]


@pytest.mark.process("git")
def test_2081_on_a_run_branch_a_unit_a_pending_skill_edit_step_names_prints_nothing_and_exits_0(tmp_path):
    subprocess.run(["git", "init", "-q", "-b", "tdd/2081-a-run-whose-pending-skill-edit-step"], cwd=tmp_path, check=True)
    (tmp_path / "skills" / "demo").mkdir(parents=True)
    (tmp_path / "skills" / "demo" / "SKILL.md").write_text("The widget is blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## skills/demo/SKILL.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-2081.md").write_text(
        "- [ ] ⟦added⟧ ⟦skill-edit⟧ regrade `skills/demo/SKILL.md`\n")

    ran = subprocess.run([str(SCRIPTS / "prose-owed.sh"), str(tmp_path)], stdin=subprocess.DEVNULL,
                         capture_output=True, text=True)

    assert (ran.returncode, ran.stdout) == (0, ""), ran.stderr


@pytest.mark.process("git")
def test_2081_a_waived_unit_is_logged_as_a_prose_owed_waived_event_naming_the_step(tmp_path):
    subprocess.run(["git", "init", "-q", "-b", "tdd/2081-a-run-whose-pending-skill-edit-step"], cwd=tmp_path, check=True)
    (tmp_path / "skills" / "demo").mkdir(parents=True)
    (tmp_path / "skills" / "demo" / "SKILL.md").write_text("The widget is blue.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(
        "## skills/demo/SKILL.md\n\n| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-2081.md").write_text(
        "- [ ] ⟦added⟧ ⟦skill-edit⟧ regrade `skills/demo/SKILL.md`\n")

    subprocess.run([str(SCRIPTS / "prose-owed.sh"), str(tmp_path)], stdin=subprocess.DEVNULL,
                   capture_output=True, text=True)

    log = tmp_path / ".tdd" / "events.jsonl"
    events = [json.loads(l) for l in log.read_text().splitlines()] if log.exists() else []
    waived = [(e.get("unit"), "regrade `skills/demo/SKILL.md`" in e.get("step", "")) for e in events
              if e.get("event") == "prose-owed-waived"]
    assert waived == [("skills/demo/SKILL.md", True)]
