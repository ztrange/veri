# Plan for #3263 — PRD 014.6a: every event veri emits is documented in `skills/tdd/JOURNAL.md`, and an undocumented one fails the suite

- [x] A `tree_audit` case in a new `skills/tdd/scripts/tests/py/test_journal_event_roster.py` collects every event name emitted under `skills/` (`event.sh` call sites and `event.mark` calls) and fails, naming the event, on one `skills/tdd/JOURNAL.md` does not document; its green adds `skills/tdd/JOURNAL.md` naming every such event ⟦criterion 2⟧
- [x] `skills/tdd/JOURNAL.md` names, for every event veri emits, the keys it carries and what each key means, judged against the diff ⟦diff-checked⟧ ⟦criterion 1⟧
