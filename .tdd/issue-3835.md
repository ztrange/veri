# Plan for #3835 — PRD 030.2: one page says what a reader of veri's files may rely on

- [x] a case fails when the journal path `PUBLISHED.md` states, or its `VERI_HOME` default, differs from what `event.journal_path` builds, taking both from `event.py` ⟦criterion 2⟧
- [x] that guard goes red with the path in `PUBLISHED.md` one directory shallower ⟦criterion 3⟧
- [x] a case fails when `JOURNAL.md`'s text above its event table does not hold that journal path and a link to `PUBLISHED.md`; `JOURNAL.md` still names `.tdd/events.jsonl` as the run's own copy ⟦criterion 4⟧ ⟦criterion 5⟧
- [ ] `skills/tdd/PUBLISHED.md` states what a reader may rely on, graded by the issue's `## Requirements` rows ⟦criterion 1⟧
