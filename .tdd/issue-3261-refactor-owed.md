### `report.sh --report` prints one block per open issue whose title starts `PRD <nnn>`, ordered by PRD number, each headed `PRD <nnn> (#<n>) — <title>`; closed PRDs and non-PRD issues get no block ⟦criterion 1⟧
- split `main` into load-snapshot, age-line and PRD-selection helpers (not duplication removal, so not applied here)
### Each PRD block's left line counts as waiting the open children with an open blocker in their cached `blockedBy`, naming each blocker ⟦criterion 1⟧
- split `main` in prd_report.py into helpers (snapshot loading, children and solved counting, left-line rendering) — a larger restructuring than this leaf's duplication-only rule allows
### Each PRD block's left line counts as held by no lane the open children with no opt-in label (`ready-for-agent` or `ready-for-agent:<lane>`) and no `tdd/<n>-*` branch on origin ⟦criterion 1⟧
- split `main` into per-PRD helper functions (solved, left); this is not duplication removal, so it is not applied here
### A PRD block whose holding lanes have fewer than three issues closed in the last 7 days prints `no rate yet` for its ETA ⟦criterion 1⟧
- split the `main` function in prd_report.py into per-section helpers (head selection, solved, left, ETA), which is a restructuring beyond this cycle's duplication-only remit
### A PRD block whose holding lanes have three or more issues closed in the last 7 days prints its ETA's lower bound as its left count ÷ the fastest rate, the rate per lane taken from the cache's `lane` field over those closed issues (issues per day at the fastest quartile of `wallSeconds`), an issue with a null `lane` counting toward no lane; the red case's fixture holds two or more open children, so the bound changes when the left count does ⟦added⟧ ⟦criterion 1⟧
- extract the fastest-lane-rate loop in `main` of `prd_report.py` into a named helper (moves logic, removes no duplication)
### A PRD block whose holding lanes have three or more issues closed in the last 7 days prints its ETA's upper bound as its left count ÷ the slowest rate (issues per day at the slowest quartile of `wallSeconds`), after the lower bound as a range; the red case's fixture holds two or more open children, so the bound changes when the left count does ⟦added⟧ ⟦criterion 1⟧
- in `main`, the ETA loop in `prd_report.py` computes fastest and slowest rates inline. Collecting the per-lane `86400 / wall` rates and taking `max` and `min` would drop the `slowest = None` sentinel. It removes no duplication against code this cycle wrote, so I did not apply it.
### A PRD block whose open children no lane holds prints `ETA: no lane: no ETA` ⟦criterion 1⟧
- extract the per-PRD ETA computation (lanes, rate, range) from `main` in prd_report.py into a helper function
### A PRD block whose open children are chained by `blockedBy` bounds its ETA by the slowest chain ⟦criterion 1⟧
- `chain` is redefined on every PRD loop iteration. Lift it to a module-level function that takes `by_number`. This isn't duplication removal, so I didn't apply it.
- Split the long `main` report branch into per-block helpers. This isn't duplication removal, so I didn't apply it.
### A PRD whose cached `updatedAt` has no stored entry in `.tdd/report-owed.json`, or a stored `updatedAt` that differs, prints `owed: stale` ⟦criterion 3⟧
- split `main` in prd_report.py into per-block helpers (children, left, owed, ETA). It is a move of behaviour, not duplication removal.
### `report.sh --stale` prints the numbers of the PRDs whose owed answer is stale, one per line ⟦criterion 3⟧
- `--stale` loads the cache with `_load`, but `--report` reopens it inline with `open`/`json.load`, and it also loads the owed file inline. Using `_load` in both places would remove the duplication.
- Both modes repeat the sort of `heads.items()` by integer PRD number. A shared helper could do that sort.
### `report.sh --store-owed <prd> <file>` stores the JSON answer read from `<file>` in `.tdd/report-owed.json` under that PRD with the PRD's current cached `updatedAt` ⟦criterion 4⟧
- out-of-scope | replace the inline `open`/`json.load` of the cache and owed files in `--report` with `_load`, which an earlier cycle wrote
### `report.sh --store-owed <prd> <file>` preserves every other PRD's entry already in `.tdd/report-owed.json` ⟦criterion 4⟧
- `--report` reads the cache with an inline `open`/`json.load` and an existence check where `--stale` and `--store-owed` use `_load`; reuse `_load` there
- `main` dispatches `--stale`, `--store-owed` and `--report` in one long function; split it into one function per option
