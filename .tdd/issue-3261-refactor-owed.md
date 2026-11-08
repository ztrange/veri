### `report.sh --report` prints one block per open issue whose title starts `PRD <nnn>`, ordered by PRD number, each headed `PRD <nnn> (#<n>) — <title>`; closed PRDs and non-PRD issues get no block ⟦criterion 1⟧
- split `main` into load-snapshot, age-line and PRD-selection helpers (not duplication removal, so not applied here)
### Each PRD block's left line counts as waiting the open children with an open blocker in their cached `blockedBy`, naming each blocker ⟦criterion 1⟧
- split `main` in prd_report.py into helpers (snapshot loading, children and solved counting, left-line rendering) — a larger restructuring than this leaf's duplication-only rule allows
