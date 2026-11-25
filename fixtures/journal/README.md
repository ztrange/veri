# Journal fixture

`3277.jsonl` is the journal of the real, merged run of issue #3277 (PR #3281),
copied byte for byte from `~/.veri/runs/ztrange-veri/3277.jsonl`, save its `mutation-record-restored`
lines, an event #4741 retired.

- Run: issue #3277
- Skill commit its events carry: `afc8d4bfdbc688100dda3be40e40a0ba88e63b14`
- Captured: 2026-11-07

`sample.jsonl` is not captured: it is generated from `skills/tdd/scripts/veri/event_table.py`, one
line per event the table declares, in its order, each carrying every key declared for that event.
Its values are invented (fixed per key format), so it shows the shape of every line, not a run.
Regenerate it whenever the table changes:

    python3 skills/tdd/scripts/veri/journal_sample.py > fixtures/journal/sample.jsonl
