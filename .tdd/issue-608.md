# Plan for #608 — hermetic-suites and skill-leaf-env stop re-running work they already did

- [ ] hermetic-suites.test.sh's conductor-lock cases each run a slice of solvable-issues.test.sh, the way the label-band case does, and none runs a whole copy of it ⟦criterion 2⟧
- [ ] hermetic-suites.test.sh pins that a live conductor lock on every fixture issue number in the surrounding repository changes neither the exit code nor the stdout of solvable-issues.sh, and goes red when solvable-issues.sh starts reading that lock ⟦criterion 1⟧
- [ ] skill-leaf-env.test.sh launches each launch line in SKILL.md at most once per ledger shape it plants ⟦criterion 4⟧
- [ ] skill-leaf-env.test.sh pins, for every launch line in SKILL.md, the environment each leaf launch receives, VERI_STEP included, and goes red when one launch line drops a variable it pins ⟦criterion 3⟧
