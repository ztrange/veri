"""Cases for grade-prose.sh that start a real process: the launcher and a stub claude."""
import subprocess
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2]
STUB = """#!/bin/sh
{ printf '%s\\n' "$@"; cat; } > "$STUB_RECORD"
printf '%s\\n' '{"type":"result","subtype":"success","is_error":false,"result":"BEGIN GRADES\\nA1: PASS - ok\\nA2: PASS - ok\\nEND GRADES\\nVERDICT: PASS"}'
"""
REQUIREMENTS = """## guide/unit.md

| ID | Requirement | Why |
|---|---|---|
| A1 | The widget is blue. | because |
| A2 | The widget never hums. | because |
"""
PROSE = "The widget is painted a deep blue.\nIt stays silent.\n"


@pytest.mark.process("grade-prose.sh launching a stub claude through supervise.sh")
def test_a_whole_file_unit_sends_the_stub_claude_the_unit_text_and_every_requirement_id_and_text(tmp_path):
    (tmp_path / "guide").mkdir()
    (tmp_path / "guide" / "unit.md").write_text(PROSE)
    (tmp_path / "REQUIREMENTS.md").write_text(REQUIREMENTS)
    claude = tmp_path / "claude"
    claude.write_text(STUB)
    claude.chmod(0o755)
    record = tmp_path / "record.txt"

    subprocess.run([str(SCRIPTS / "grade-prose.sh"), "REQUIREMENTS.md", "guide/unit.md"], cwd=tmp_path,
                   capture_output=True, env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path),
                                             "CLAUDE_BIN": str(claude), "STUB_RECORD": str(record)})

    received = record.read_text() if record.exists() else ""
    assert [PROSE in received, "A1" in received, "The widget is blue." in received,
            "A2" in received, "The widget never hums." in received] == [True] * 5, received
