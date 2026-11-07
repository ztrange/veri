"""The event roster: every event name emitted under skills/ is documented in skills/tdd/JOURNAL.md."""
import pathlib
import re

import pytest

SKILLS = pathlib.Path(__file__).resolve().parents[5]
JOURNAL = SKILLS / "tdd" / "JOURNAL.md"
SH_CALL = re.compile(r"event\.sh +([a-z][a-z0-9-]*)")
MARK_CALL = re.compile(r"""event\.mark\((?:[^"']|"[^"]*:"|"[A-Za-z_]+"(?=\s*:))*?,\s*"([a-z][a-z0-9-]*)"\s*[,)]""")


def emitted_events():
    names = {}
    for path in sorted(SKILLS.rglob("*")):
        if not path.is_file() or "tests" in path.parts or path.suffix not in (".sh", ".py", ".md"):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern in (SH_CALL, MARK_CALL):
            for found in pattern.finditer(text):
                names.setdefault(found.group(1), path.relative_to(SKILLS))
    return names


@pytest.mark.tree_audit("reads every file under skills/ for event.sh call sites and event.mark calls")
def test_every_event_emitted_under_skills_is_documented_in_journal_md():
    journal = JOURNAL.read_text(encoding="utf-8") if JOURNAL.is_file() else ""
    emitted = emitted_events()
    assert emitted, "no event call site found under skills/"
    undocumented = sorted(name for name in emitted if not re.search(r"(?<![a-z0-9-])" + re.escape(name) + r"(?![a-z0-9-])", journal))
    assert not undocumented, "skills/tdd/JOURNAL.md does not document: " + ", ".join(
        "%s (emitted in %s)" % (name, emitted[name]) for name in undocumented)
