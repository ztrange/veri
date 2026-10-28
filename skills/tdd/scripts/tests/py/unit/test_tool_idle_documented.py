"""In-process case for CLAUDE.md's record of VERI_TOOL_IDLE as an injected liveness tunable."""
import re

from skill_sections import ROOT


def test_claude_md_lists_veri_tool_idle_beside_heartbeat_as_injected_window_2566():
    text = (ROOT / "CLAUDE.md").read_text()
    paragraph = next(
        p for p in re.split(r"\n\s*\n", text) if "`VERI_STUCK_RETRIES` shrink" in p
    )
    flat = " ".join(paragraph.split())
    assert re.search(r"`VERI_HEARTBEAT`.*`VERI_TOOL_IDLE`|`VERI_TOOL_IDLE`.*`VERI_HEARTBEAT`", flat), flat


def test_claude_md_six_budgets_bullet_still_counts_six_and_does_not_fold_veri_tool_idle_2566():
    text = (ROOT / "CLAUDE.md").read_text()
    bullet = next(b for b in re.split(r"\n(?=- )", text) if b.startswith("- **Six budgets"))
    flat = " ".join(bullet.split())
    names = set(re.findall(r"`([A-Z][A-Z_]*(?:BUDGET|RETRIES|GROWTH))`", flat))
    assert names == {
        "VERI_STUCK_RETRIES", "VERI_NO_VERDICT_RETRIES", "REVISE_BUDGET",
        "VERI_REFACTOR_BUDGET", "VERI_STEP_GROWTH", "VERI_SKILL_EDIT_BUDGET",
    }, flat
    assert "VERI_TOOL_IDLE" not in flat, flat
