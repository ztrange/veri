# Plan for #4443 — A go-red guard step is run as a mutation probe on its named case, not handed to the Red leaf

- [x] `tick-ledger.sh` refuses (exit 2, ledger untouched) a `⟦go-red⟧` step whose mutation record holds no entry for the file the step's probe names ⟦criterion 2⟧
- [x] `go-red-step.sh <n>` runs `mutation-probe.sh <file> <old> <new>` with the `veri: one test file:` command on the case the open `⟦go-red⟧` step names, into `.tdd/issue-<n>-mutations.md`, then `step-tick.sh <n>`; a step naming no probe, bad arguments or a missing input are exit 2 ⟦criterion 1⟧
- [x] `go-red-step.sh` stops with exit 1 and ticks nothing when the probe sees no red (its exit 1), and with exit 2 when the probe exits 2 or the named file is not restored ⟦criterion 2⟧
- [ ] `step-tick.sh` closes a `⟦go-red⟧` step without a pin-recheck receipt, under `test: go-red — <summary> (#<n>)` ⟦criterion 1⟧
- [ ] `run-step.sh` runs `go-red-step.sh` as a `⟦go-red⟧` step's one stage, and `red-half.sh` refuses a `⟦go-red⟧` step ⟦criterion 1⟧
- [ ] SKILL.md's go-red paragraph routes the step to `go-red-step.sh` through `run-step.sh`, never the Red leaf, netting <= 80 B; the PL row added and the unit regraded ⟦skill-edit⟧ ⟦criterion 1⟧
- [ ] SCRIPTS.md, veri/README.md and GO-RED.md list `go-red-step.sh`, its probe wording and its exits
