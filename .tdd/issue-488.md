# Plan for #488 — the By-step table's revise cell is phase-blind, so a step reads as an overrun it never had

- [x] A step whose revise marks name more than one phase renders its `#### By step` revise cell as one `<phase> <used>/<budget>` entry per revised phase, rather than one step-wide total ⟦criterion 1⟧
- [x] A step that revised two phases once each under `REVISE_BUDGET` 2 renders each phase as `1/2`, with no count above the budget anywhere in its revise cell ⟦criterion 2⟧
- [x] A step that revised one phase `REVISE_BUDGET` times renders that phase as `<budget>/<budget>` in its revise cell ⟦criterion 3⟧
- [ ] A step with no revise marks renders its revise cell exactly as today, the unknown placeholder ⟦criterion 4⟧
