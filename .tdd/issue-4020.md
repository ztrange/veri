# Plan for #4020 — PRD 030.4: a sample journal with one line per declared event

- [x] `python3 skills/tdd/scripts/veri/journal_sample.py` prints one line per event `veri/event_table.py` declares, in the table's order, each carrying every key declared for it, built through `event.line` with values fixed per format, and exits 0 ⟦criterion 2⟧
- [x] two runs of `journal_sample.py` with a different clock, environment and current directory print the same bytes ⟦criterion 2⟧
- [x] a case fails, naming the first differing line, when the committed `fixtures/journal/sample.jsonl` differs from what `journal_sample.py` builds; the sample is committed ⟦criterion 1⟧ ⟦criterion 3⟧
- [x] a case fails, naming the event, when a declared event has no line in `sample.jsonl` or it holds a line for an undeclared event ⟦criterion 4⟧
- [x] the fixture-format case reads `sample.jsonl` through its glob and fails naming the line, event, key and value for a sample value breaking its format ⟦criterion 5⟧
- [x] `fixtures/journal/README.md` names `sample.jsonl`, says it is generated from the table, not captured, with invented values, and gives the command that regenerates it ⟦criterion 6⟧
- [x] `veri/README.md`'s module index has an entry for `journal_sample` ⟦criterion 7⟧
