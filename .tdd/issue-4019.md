# Plan for #4019 — PRD 030.3: every journal key has a declared format

- [x] a case fails, naming the event and key, for a key of an event or a string common key whose format is missing or outside the closed set `veri/event_table.py` defines; the table declares one for every key ⟦criterion 1⟧
- [x] `event_table.valid` reads an empty value as invalid for a key not marked empty-allowed, whatever its format, and as valid for one so marked ⟦criterion 2⟧
- [x] a case fails, naming the file, line, event, key and value, for a value in `fixtures/journal/*.jsonl` its key's declared format rejects ⟦criterion 3⟧
- [x] `JOURNAL.md` states every key's format and a case fails, naming the event and key, when it differs from the table's, the page read by `journal_schema.formats` ⟦criterion 4⟧
- [x] a case fails, naming the event and key, for a `JOURNAL.md` row whose list ends with `…`; `bail`'s `cause` list is written out ⟦criterion 5⟧
- [x] a case fails naming each cause in one of `bail`'s `cause` values and `classify_bail.CATEGORIES` and not the other, and its `classification` values are exactly `process` and `system` ⟦criterion 6⟧
- [x] `PUBLISHED.md` states that each key has a format stated in `JOURNAL.md`, that a list may gain values, and that a reader treats an unknown value as an unknown key ⟦criterion 7⟧
