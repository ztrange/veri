# Plan for #4574 — Conductor spend is 82% of veri-dashboard run cost: diagnose the 122 hot conductor turns

- [x] `specs/conductor-cost-audit.md` holds a measured breakdown of the 122 conductor turns at or above $0.50 in veri-dashboard runs #13, #26 and #27 (read from `~/.veri/runs/ztrange-veri-dashboard/{13,26,27}.*`): per turn what it read or ran, its context size and its cost, grouped by cause, naming the dominant cause with its share of the $97; no production or test file changes ⟦diff-checked⟧ ⟦criterion 1⟧
- [x] `specs/conductor-cost-audit.md` ends with a proposed fix per named cause, each given as an issue title, and no fix is made in this branch (only `specs/conductor-cost-audit.md` changes) ⟦diff-checked⟧ ⟦criterion 2⟧
