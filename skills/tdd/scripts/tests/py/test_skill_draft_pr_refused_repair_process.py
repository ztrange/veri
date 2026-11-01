"""The Draft PR repair block of skills/tdd/SKILL.md, run through real bash against stub scripts."""
import re
import subprocess
from pathlib import Path

import pytest

SKILL = Path(__file__).resolve().parents[3] / "SKILL.md"
ANCHOR = re.compile(r"^\$S/add-ledger-step\.sh .*⟦suite-repair⟧")


def _repair_block():
    out, on = [], False
    for line in SKILL.read_text(encoding="utf-8").split("\n"):
        if ANCHOR.match(line):
            on = True
        elif on and line.startswith("```"):
            break
        if on:
            out.append(line)
    return "\n".join(out).replace("<n>", "2730")


@pytest.mark.process("SKILL.md's Draft PR repair block runs under bash -c against stub scripts")
def test_issue_2730_a_refused_repair_step_bails_step_add_refused_and_writes_no_step_added_or_step_start(tmp_path):
    block = _repair_block()
    assert block.strip(), "no add-ledger-step.sh ⟦suite-repair⟧ block in SKILL.md — nothing could be run"
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    stubs = {"add-ledger-step.sh": "#!/bin/sh\nexit 2\n",
             "ledger-steps.sh": "#!/bin/sh\necho step-one\n",
             "classify-bail.sh": '#!/bin/sh\necho "$1"\n',
             "event.sh": '#!/bin/sh\necho "$*" >> "$PWD/events.log"\n'}
    for name, body in stubs.items():
        (bin_dir / name).write_text(body)
        (bin_dir / name).chmod(0o755)
    work = tmp_path / "work"
    work.mkdir()
    env = {"PATH": "/usr/bin:/bin", "HOME": str(tmp_path), "S": str(bin_dir)}
    subprocess.run(["bash", "-c", block], cwd=work, env=env, stdin=subprocess.DEVNULL,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log = work / "events.log"
    events = log.read_text().splitlines() if log.exists() else []
    assert events == ["bail cause=step-add-refused classification=step-add-refused"], (
        f"a refused repair step left events {events} instead of only the step-add-refused bail")
