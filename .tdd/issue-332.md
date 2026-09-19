# Plan for #332 — no-size-assertion.test.sh forks sed and grep twice per test file instead of once for the whole tree

- [x] no-size-assertion.test.sh's probe makes exactly one grep invocation across the whole scanned directory before any per-file work, counted by a PATH-first counting shim in front of grep and sed, never a wall-clock measurement ⟦criterion 1⟧
- [x] against a fixture directory of N suites where only M (M < N) contain a size-verb line, the counting shim shows the probe's per-file subjects()/classification forks bounded by M, not N ⟦criterion 2⟧
- [x] a suite whose only size-verb line is inside a comment (`# wc -c the old way`) is still not reported by no-size-assertion.test.sh ⟦criterion 3⟧
- [ ] a suite binding a variable to CLAUDE.md or SKILL.md three lines above the line that measures it (`doc="$ROOT/CLAUDE.md"` then `wc -c < "$doc"`) is still reported by no-size-assertion.test.sh, naming the suite and line ⟦criterion 4⟧
- [ ] a suite that measures something else entirely with wc/stat/du is still not reported by no-size-assertion.test.sh ⟦criterion 5⟧
- [ ] no-size-assertion.test.sh run against the current tree still ends in the same `<n> passed, <m> failed` outcome as before the restructure ⟦criterion 6⟧
- [ ] every no-size-assertion.test.sh assertion that passed before still passes, and make test is green ⟦criterion 7⟧
