### `report.sh --report` prints one block per open issue whose title starts `PRD <nnn>`, ordered by PRD number, each headed `PRD <nnn> (#<n>) — <title>`; closed PRDs and non-PRD issues get no block ⟦criterion 1⟧
- split `main` into load-snapshot, age-line and PRD-selection helpers (not duplication removal, so not applied here)
