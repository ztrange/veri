"""The event roster: every event name emitted under skills/ is documented in skills/tdd/JOURNAL.md."""
import re

import pytest

from veri.event_roster import SKILLS, emitted_events

JOURNAL = SKILLS / "tdd" / "JOURNAL.md"


@pytest.mark.tree_audit("reads every file under skills/ for event.sh call sites and event.mark calls")
def test_every_event_emitted_under_skills_is_documented_in_journal_md():
    journal = JOURNAL.read_text(encoding="utf-8") if JOURNAL.is_file() else ""
    emitted = emitted_events()
    assert emitted, "no event call site found under skills/"
    undocumented = sorted(name for name in emitted if not re.search(r"(?<![a-z0-9-])" + re.escape(name) + r"(?![a-z0-9-])", journal))
    assert not undocumented, "skills/tdd/JOURNAL.md does not document: " + ", ".join(
        "%s (emitted in %s)" % (name, emitted[name]) for name in undocumented)
