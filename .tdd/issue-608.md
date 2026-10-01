# Plan for #608 — hermetic-suites and skill-leaf-env stop re-running work they already did

- [x] hermetic-suites.test.sh's conductor-lock cases each run a slice of solvable-issues.test.sh, the way the label-band case does, and none runs a whole copy of it ⟦criterion 2⟧
- [x] hermetic-suites.test.sh pins that a live conductor lock on every fixture issue number in the surrounding repository changes neither the exit code nor the stdout of solvable-issues.sh, and goes red when solvable-issues.sh starts reading that lock ⟦criterion 1⟧
- [x] skill-leaf-env.test.sh launches each launch line in SKILL.md at most once per ledger shape it plants ⟦criterion 4⟧
- [x] skill-leaf-env.test.sh pins, for every launch line in SKILL.md, the environment each leaf launch receives, VERI_STEP included, and goes red when one launch line drops a variable it pins ⟦criterion 3⟧
- [x] repair the red full suite: no-job-spec-kills.test.sh fails — "no file under skills/ ends a background process by a job spec" names skill-leaf-env.test.sh:37 and :442, whose step-title text spells `kill %1`, and "every exemption names a line … that ends a background process by a job spec" says the [skill-leaf-env.test.sh:395] exemption excuses nothing — no-job-spec-kills.test.sh is green again with every assertion it makes kept ⟦added⟧ ⟦criterion 3⟧ ⟂ refactor pending
