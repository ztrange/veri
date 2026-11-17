# Plan for #4051 — PRD 025.16: the pytest leg lives under tests/

- [ ] run-conductor's free-space check and the leg read `PINNED_TMPDIR` from one `veri/` module, and `run_conductor.py` imports no leg module ⟦criterion 3⟧
- [ ] the five leg modules live in `skills/tdd/scripts/tests/leg/`, the Makefile starts the leg there, and no site names them under `veri/` ⟦criterion 1⟧ ⟦criterion 2⟧ ⟦criterion 6⟧
- [ ] `CLAUDE.md` names the leg at its new path (CM51 reworded), graded ⟦criterion 4⟧ ⟦criterion 5⟧
