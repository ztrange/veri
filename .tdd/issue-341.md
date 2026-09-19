# Plan for #341 — SKILL.md and its prompts run the fast tier, affected suites, and one full run per PR

- [x] SKILL.md's preflight baseline step names `--tier fast`'s command as what it runs and times, in wording a text-reading guard suite can pin ⟦criterion 1⟧
- [x] develop-red.md and verify-red.md name the affected-suites command, not a single hand-named suite, as what the red leaf and its verifier run ⟦criterion 2⟧
- [x] verify-refactor.md's checklist item 1 no longer says "the project's full test suite" and names the affected-suites command ⟦criterion 3⟧
- [x] develop-refactor.md names the affected-suites command fed refactor-touched.sh's output as what the refactor leaf runs after each transform
- [x] develop-green.md and verify-green.md name the fast command plus the affected suites as what they run, not "the full suite" ⟦criterion 4⟧
- [ ] SKILL.md's Draft PR section and its closing invariant both name `--tier all`'s command, run exactly once, as the only full-suite gate left in the cycle ⟦criterion 5⟧
- [ ] A red result on the final full run adds a repair step to the ledger rather than bailing, with a unit-tier test added when the failure exposes a gap and the verifier judging the fix against the full command ⟦criterion 6⟧
- [ ] A second red result on the full run after a repair step bails, naming every suite still red, not only the first ⟦criterion 7⟧
- [ ] build-develop-prompt.sh accepts the new parameters the tiered templates require and exits 2 on a missing one, its existing cases still passing ⟦criterion 8⟧
- [ ] build-verify-prompt.sh accepts the new parameters the tiered templates require and exits 2 on a missing one, its existing cases still passing ⟦criterion 8⟧
- [ ] run-conductor.test.sh asserts, per phase with a stub claude, which command (fast, affected, fast+affected, or all) that phase's launch was built with ⟦criterion 9⟧
