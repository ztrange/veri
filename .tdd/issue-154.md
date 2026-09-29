# Plan for #154 — docs-test pays for build-guards twice since #137 — keep the lane-insulation pin, cut the whole-suite rerun

- [ ] lane-insulation.test.sh's third case asks build-guards.test.sh, over the tree owing commentary, for only the git-budget case (`ONLY='a build asks git once per script'`) instead of the whole suite, and still reports a suite that dies before its count line (the 18b stderr-as-numbers bug) ⟦criterion 2⟧
- [ ] The docs-test duration merge-gates.sh prints in its `docs-test` line is no longer the stale "~2 min": it states a figure measured by this run or none at all ⟦criterion 3⟧
- [ ] The stale "~2 min" for docs-test in CLAUDE.md's Commands table and any Makefile comment is measured-and-current or removed, and lane-insulation.test.sh's header stops quoting a ~215 s / ~200 s whole-suite cost ⟦criterion 3⟧
- [ ] make -C projects/docs test wall time at or below its pre-#137 figure, both numbers measured on this machine in one sitting and stated in the PR ⟦human-owed⟧ ⟦criterion 1⟧
