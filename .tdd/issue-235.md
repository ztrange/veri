# Plan for #235 — metrics.sh's progress count misses steps that ended via pin, undercounting a finished run

- [x] A log carrying a `pin` mark for a step, and no `step-done` mark for that step, counts that step as done in the "Steps done: X of Y planned" line
- [x] A log with two `pin` marks and one `step-done` mark for three different ledger steps reports "3 of 3 planned"
- [x] A log whose steps end only in `step-done` (no `pin`) is unaffected
