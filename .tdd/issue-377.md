# Plan for #377 — preflight sizes VERI_TIMEOUT from the fast tier, so a leaf running the full tier is killed at the 900 s floor

- [x] leaf-timeout.sh derives the run's hard timeout from the full-tier measurement rather than the fast-tier one: given a recorded pair whose fast tier is quick and whose full tier is slow, the value returned is the one the slow measurement implies ⟦criterion 1⟧
- [x] SKILL.md's preflight measures the full tier and hands that measurement to leaf-timeout.sh, exporting the result as VERI_TIMEOUT for every leaf, and the plan comment states which tier the number came from ⟦criterion 1⟧
- [x] An explicit VERI_TIMEOUT still wins over the sizing and is still printed back verbatim, whatever pair of tier measurements is handed in ⟦criterion 2⟧
- [x] leaf-timeout.sh still exits 2 with a diagnostic on stderr and nothing on stdout for a measurement it cannot read — the full-tier one included — and SKILL.md's preflight still refuses to start on that exit ⟦criterion 3⟧
