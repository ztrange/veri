# Plan for #3605 — dispatch.sh reports a relaunched run as stalled from the previous run's file mtimes

- [x] dispatch.sh does not report `stalled <n>` for a run whose `.tdd/` activity files (events.jsonl, *.out, *.log) carry mtimes older than the stall window when its conductor started (`.tdd/conductor.pid` mtime) less than the stall window ago ⟦criterion 1⟧
- [x] dispatch.sh still reports `stalled <n>` for a run whose conductor started (`.tdd/conductor.pid` mtime) longer than the stall window ago and whose `.tdd/` activity files have not been written for longer than the stall window ⟦criterion 2⟧ ⟂ retired unpinnable
