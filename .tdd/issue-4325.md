# Plan for #4325 — Operator docs define a live conductor by its pid alone, so a hand check of the two-line conductor.pid reads live runs as dead

- [x] `skills/vdev/SKILL.md`'s *Live conductors and the slot decision* says `conductor.pid` holds two lines, the pid and then its start time, that a conductor is live only when that pid answers `kill -0` and its start time matches the second line, and points at `$S/status.sh --json` as the reader that applies the rule (row D141) ⟦skill-edit⟧ ⟦criterion 1⟧
- [x] `operator/PRINCIPLES.md`'s P1 and P9 paragraphs define a live conductor as `conductor.pid`'s first-line pid answering `kill -0` with its start time matching the second line (row P9 reworded) ⟦skill-edit⟧ ⟦criterion 1⟧
