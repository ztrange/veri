"""`python3 skills/tdd/scripts/veri/journal_sample.py` prints the sample journal: one line per declared event (PRD 030.4, SJ1, SJ2)."""
import json
import subprocess
import sys

import pytest
from veri import event_table

from conftest import SCRIPTS


@pytest.mark.process("python3 running veri/journal_sample.py as a script")
def test_run_as_a_script_it_prints_one_line_per_declared_event_in_table_order_carrying_every_key_and_exits_0():
    done = subprocess.run([sys.executable, str(SCRIPTS / "veri" / "journal_sample.py")], capture_output=True,
                          stdin=subprocess.DEVNULL)

    assert (done.returncode, done.stderr) == (0, b"")
    lines = [json.loads(line) for line in done.stdout.decode().splitlines()]
    assert [line["event"] for line in lines] == list(event_table.EVENTS)
    # an event key named like a run-context one (`step`) repeats it in the line; a JSON object keeps it once
    assert [list(line) for line in lines] == [list(dict.fromkeys(event_table.COMMON + event_table.keys(name)))
                                              for name in event_table.EVENTS]
