# Plan for #3261 — PRD 014.5b: `report.sh --report` prints every active PRD's report from local files, with no model

The logic lives in a new module `skills/tdd/scripts/veri/prd_report.py` (the name `veri/report.py` is already taken by the leaf-report reader four modules import), behind a new `/bin/sh` shim `skills/tdd/scripts/report.sh` per the `status.sh` convention; unit cases in `skills/tdd/scripts/tests/py/unit/test_prd_report.py`, entry-point cases in `skills/tdd/scripts/tests/py/test_prd_report_process.py`. Every case builds its own `.tdd/report-cache.json` and `.tdd/report-owed.json` under `tmp_path` and fakes `solvable-issues.sh` and `gh` at the process boundary.

- [x] `report.sh` run with no argument prints its usage line on stderr and exits 2; the step adds `report.sh` (a `/bin/sh` shim over `veri/prd_report.py`) and its declared caller (a `report` recipe in the `Makefile` running `report.sh --report`, so `unreachable.sh` reaches it; `SCRIPTS.md` is a graded unit and is not edited)
- [x] `report.sh --report` with a snapshot `.tdd/report-cache.json` present states the snapshot's age on its first line ⟦criterion 2⟧
- [x] `report.sh --report` with no `.tdd/report-cache.json` says there is no snapshot and exits 2 ⟦criterion 2⟧
- [x] `report.sh --report` prints one block per open issue whose title starts `PRD <nnn>`, ordered by PRD number, each headed `PRD <nnn> (#<n>) — <title>`; closed PRDs and non-PRD issues get no block ⟦criterion 1⟧
- [x] Each PRD block's solved line counts the PRD's closed children (cached issues whose title starts with its `PRD <nnn>`, plus the issues in its `links`, minus the PRD itself and links to other PRDs) and how many of them closed in the last 7 days ⟦criterion 1⟧
- [x] Each PRD block's left line counts as solvable now the open children that `VERI_LABEL=<their opt-in label> solvable-issues.sh` lists; the red case's fixture keeps a second open PRD (#99 "PRD 015: other prd child") so blocks are shown not to bleed into each other, and it asserts the `left` line inside the PRD 014 block only, never the count of `left` lines in the whole report ⟦criterion 1⟧
- [x] Each PRD block's left line counts as waiting the open children with an open blocker in their cached `blockedBy`, naming each blocker ⟦criterion 1⟧
- [x] Each PRD block's left line counts as held by no lane the open children with no opt-in label (`ready-for-agent` or `ready-for-agent:<lane>`) and no `tdd/<n>-*` branch on origin ⟦criterion 1⟧
- [x] Each PRD block's ETA is a range: its left count ÷ the rate of the lanes holding its open children, the rate per lane taken from the cache's `lane` field over the issues closed in the last 7 days (issues per day, fastest and slowest quartile of `wallSeconds`), an issue with a null `lane` counting toward no lane ⟦criterion 1⟧ ⟂ retired unpinnable
- [x] A PRD block whose holding lanes have fewer than three issues closed in the last 7 days prints `no rate yet` for its ETA ⟦criterion 1⟧ ⟂ refactor pending
- [ ] A PRD block whose open children no lane holds prints `ETA: no lane: no ETA` ⟦criterion 1⟧
- [ ] A PRD block whose open children are chained by `blockedBy` bounds its ETA by the slowest chain ⟦criterion 1⟧
- [ ] A PRD whose cached `updatedAt` has no stored entry in `.tdd/report-owed.json`, or a stored `updatedAt` that differs, prints `owed: stale` ⟦criterion 3⟧
- [ ] A PRD whose cached `updatedAt` equals the one stored for it in `.tdd/report-owed.json` prints the stored owed answer (how many issues, with the sections they come from, or `none`) on its owed line ⟦criterion 1⟧
- [ ] `report.sh --stale` prints the numbers of the PRDs whose owed answer is stale, one per line ⟦criterion 3⟧
- [ ] `report.sh --store-owed <prd> <file>` stores the JSON answer read from `<file>` in `.tdd/report-owed.json` under that PRD with the PRD's current cached `updatedAt` ⟦criterion 4⟧
- [ ] `report.sh --store-owed <prd> <file>` preserves every other PRD's entry already in `.tdd/report-owed.json` ⟦criterion 4⟧
- [ ] With `gh` refusing and a snapshot present, `report.sh --report` exits 0 and prints the same report as with `gh` answering (a medium case at the process boundary, `gh` and `solvable-issues.sh`'s GitHub reads refused) ⟦criterion 2⟧
