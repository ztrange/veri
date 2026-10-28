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
