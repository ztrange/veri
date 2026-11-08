"""The captured journal under fixtures/journal/ uses only events and keys skills/tdd/JOURNAL.md documents."""
import json
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[6]
JOURNAL_MD = ROOT / "skills" / "tdd" / "JOURNAL.md"
FIXTURES = ROOT / "fixtures" / "journal"


def _documented(text):
    common = set()
    for line in text.splitlines():
        if "Every line carries" in line:
            sentence = line.split("Every line carries")[1].split("then the keys")[0]
            common = set(re.findall(r"`([^`]+)`", sentence))
    rows = {}
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("|") and len(cells) >= 2 and cells[0].startswith("`"):
            rows[cells[0].strip("`")] = set(re.findall(r"`([^`]+)`", cells[1]))
    return common, rows


@pytest.mark.tree_audit("lists fixtures/journal/ for its captured journals")
def test_every_event_and_key_in_the_fixture_journal_is_documented_in_journal_md():
    common, rows = _documented(JOURNAL_MD.read_text(encoding="utf-8"))
    files = sorted(FIXTURES.glob("*.jsonl"))
    assert files, "no fixture journal under fixtures/journal/"
    problems = []
    for path in files:
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            record = json.loads(line)
            event = record.get("event")
            if event not in rows:
                problems.append("%s:%d event %r is not documented" % (path.name, n, event))
                continue
            for key in record:
                if key not in common and key not in rows[event]:
                    problems.append("%s:%d key %r of event %r is not documented" % (path.name, n, key, event))
    assert not problems, "skills/tdd/JOURNAL.md does not document:\n" + "\n".join(problems)
