"""No key veri's events carry is a schema version key: keys and events are append-only."""
import json
import pathlib
import re

import pytest

from veri import event

ROOT = pathlib.Path(__file__).resolve().parents[6]
JOURNAL_MD = ROOT / "skills" / "tdd" / "JOURNAL.md"
FIXTURES = ROOT / "fixtures" / "journal"
VERSION_KEYS = {"version", "schema", "schema_version", "v"}


def _is_version_key(key):
    return key.lower() in VERSION_KEYS or "version" in key.lower()


@pytest.mark.tree_audit("lists fixtures/journal/ for its captured journals")
def test_no_key_an_event_carries_is_a_schema_version_key():
    keys = {}
    for context_key, _ in event.CONTEXT:
        keys.setdefault(context_key.decode(), "veri/event.py run context")
    keys.setdefault("ts", "veri/event.py run context")
    keys.setdefault("awake", "veri/event.py run context")
    for line in JOURNAL_MD.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("|") and len(cells) >= 2 and cells[0].startswith("`"):
            for key in re.findall(r"`([^`]+)`", cells[1]):
                keys.setdefault(key, "skills/tdd/JOURNAL.md row %s" % cells[0])
        if "Every line carries" in line:
            sentence = line.split("Every line carries")[1].split("then the keys")[0]
            for key in re.findall(r"`([^`]+)`", sentence):
                keys.setdefault(key, "skills/tdd/JOURNAL.md common keys")
    files = sorted(FIXTURES.glob("*.jsonl"))
    assert files, "no fixture journal under fixtures/journal/"
    for path in files:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                for key in json.loads(line):
                    keys.setdefault(key, "fixtures/journal/%s" % path.name)
    offenders = sorted("%s (%s)" % (k, where) for k, where in keys.items() if _is_version_key(k))
    assert not offenders, "schema version keys on events: " + ", ".join(offenders)
