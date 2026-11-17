# Plan for #4238 — PRD 035.7c: metrics.md shows the conductor's spend per phase

- [x] `metrics.sh <n>` prints a `#### Conductor by phase` table, `estimated` in its heading, one row per `conductor.by_phase` entry with its turns and cost, `unknown` for a null cost; none when `by_phase` is null ⟦criterion 1⟧
- [x] `SCRIPTS.md`'s `metrics.sh` entry names the table, graded by row SC480 ⟦criterion 2⟧
