"""The event roster: every event name emitted under skills/ is documented in skills/tdd/JOURNAL.md."""
import pytest

from event_roster import SKILLS, documented_events, emitted_events

JOURNAL = SKILLS / "tdd" / "JOURNAL.md"


@pytest.mark.tree_audit("reads every file under skills/ for event.sh call sites and event.mark calls")
def test_every_event_emitted_under_skills_is_documented_in_journal_md():
    journal = JOURNAL.read_text(encoding="utf-8") if JOURNAL.is_file() else ""
    emitted = emitted_events()
    assert emitted, "no event call site found under skills/"
    documented = documented_events(journal)
    undocumented = sorted(name for name in emitted if name not in documented)
    assert not undocumented, "skills/tdd/JOURNAL.md does not document: " + ", ".join(
        "%s (emitted in %s)" % (name, emitted[name]) for name in undocumented)


def test_the_guard_fails_on_an_event_named_only_in_prose_or_another_row():
    from event_roster import documented_events

    text = (
        "# Journal\n\nThe `prose-only` event is mentioned here but has no row.\n\n"
        "| Event | Keys | Meaning |\n|---|---|---|\n| `listed` | `n` | See also prose-only. |\n")
    assert documented_events(text) == {"listed"}


def test_journal_md_has_a_table_row_for_the_conductor_restart_event():
    from event_roster import documented_events

    assert "conductor-restart" in documented_events(JOURNAL.read_text(encoding="utf-8"))


def test_journal_md_has_a_table_row_for_the_lint_event_and_the_event_table_declares_its_exit_key_4122():
    from veri import event_table

    from event_roster import documented_events

    assert ("lint" in documented_events(JOURNAL.read_text(encoding="utf-8")),
            "lint" in event_table.EVENTS and list(event_table.keys("lint"))) == (True, ["exit"])


def test_journal_md_has_a_table_row_for_the_tidy_first_event_and_the_event_table_declares_its_keys_4118():
    from veri import event_table

    from event_roster import documented_events

    assert ("tidy-first" in documented_events(JOURNAL.read_text(encoding="utf-8")),
            "tidy-first" in event_table.EVENTS and sorted(event_table.keys("tidy-first"))) == (True, ["anchor", "refactoring"])
