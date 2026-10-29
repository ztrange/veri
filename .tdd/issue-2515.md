# Plan for #2515 — A leaf killed from outside bails as killed-external, not killed-stuck

- [x] skills/tdd/BAIL.md lists the `killed-external` cause (row BL44): a developer leaf's supervise.sh exited 2 with the `supervise[<name>]: killed-external` status line, never retried, a system failure distinct from killed-stuck, graded PASS and re-signed in skills/tdd/GRADED ⟦skill-edit⟧ ⟦criterion 1⟧
- [x] skills/tdd/SKILL.md's *Launching a leaf* bails with cause `killed-external` on a developer leaf's exit 2 whose `.tdd/<name>.err` carries the `supervise[<name>]: killed-external` status line, after the stop check and without relaunching, every other exit 2 read as today (row LL38), graded PASS and re-signed in skills/tdd/GRADED ⟦skill-edit⟧ ⟦criterion 1⟧
