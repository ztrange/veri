### `report.sh --report` prints one block per open issue whose title starts `PRD <nnn>`, ordered by PRD number, each headed `PRD <nnn> (#<n>) — <title>`; closed PRDs and non-PRD issues get no block ⟦criterion 1⟧
- split `main` into load-snapshot, age-line and PRD-selection helpers (not duplication removal, so not applied here)
### Each PRD block's left line counts as waiting the open children with an open blocker in their cached `blockedBy`, naming each blocker ⟦criterion 1⟧
- split `main` in prd_report.py into helpers (snapshot loading, children and solved counting, left-line rendering) — a larger restructuring than this leaf's duplication-only rule allows
### Each PRD block's left line counts as held by no lane the open children with no opt-in label (`ready-for-agent` or `ready-for-agent:<lane>`) and no `tdd/<n>-*` branch on origin ⟦criterion 1⟧
- split `main` into per-PRD helper functions (solved, left); this is not duplication removal, so it is not applied here
### A PRD block whose holding lanes have fewer than three issues closed in the last 7 days prints `no rate yet` for its ETA ⟦criterion 1⟧
- split the `main` function in prd_report.py into per-section helpers (head selection, solved, left, ETA), which is a restructuring beyond this cycle's duplication-only remit
