# Plan for #3836 — PRD 030.1a: an event's keys are declared in one table, and the page, the writers and the fixture are checked against it

- [ ] `veri/event_table.py` exists and imports no other veri module ⟦criterion 1⟧
- [ ] the table declares every event veri emits with its keys and per key whether it is required, `grading`, `unpinnable-missing`, `prose-owed-waived`, `suite-flake` and `skill-edit-no-author` with the keys their writers pass ⟦criterion 4⟧
- [ ] a case fails, naming the event and key, when the table and `JOURNAL.md`'s table differ in either direction, read through `journal_schema.kinds`/`fields`; `JOURNAL.md` gains the rows the table holds ⟦criterion 2⟧
- [ ] that guard goes red with a key removed from the table, and with a key removed from a `JOURNAL.md` row ⟦criterion 3⟧
- [ ] `test_journal_fields_audit.py` checks literal writer kinds and keys against the table, with no ratchet lists ⟦criterion 5⟧
- [ ] `test_journal_fixture_keys.py` checks the fixture against the table and no longer parses `JOURNAL.md` ⟦criterion 6⟧
- [ ] a `tree_audit` case fails, naming file and line, on an `event.sh` call site under `skills/` whose literal event or key the table does not declare ⟦criterion 7⟧
- [ ] that guard goes red with an undeclared key added to an `event.sh` call under `skills/` ⟦criterion 8⟧
- [ ] `veri/README.md`'s module index has an entry for the table module ⟦criterion 9⟧
