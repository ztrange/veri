# Plan for #539 — verify-refactor runs the full suite once per step; PRD 003 decided once per PR — restore it

- [x] SKILL.md's verify-refactor entry (Refactor loop, sub-step 5) says the verdict is on the fast tier plus the affected suites still green, in the same terms as verify-refactor.md, and no longer says the full suite runs in the refactor phase ⟦criterion 1⟧
- [x] SKILL.md's sentence explaining what catches a break in a suite outside the affected set points at the Draft PR step's single full-suite run and its repair step, not at verify-refactor ⟦criterion 2⟧
- [x] SKILL.md's Green section says develop-green keeps the fast tier plus the affected suites green before it reports, as develop-green.md does, and no longer says it keeps the full suite green ⟂ refactor pending
- [ ] CLAUDE.md's "Testing idiom" paragraph states what runs per step (red and refactor leaves: the affected suites; develop-green, verify-green and verify-refactor: the fast tier plus the affected suites) and per PR (the full suite once before the PR is readied, plus once per repair step) ⟦criterion 3⟧
- [ ] the suite that pins which phases run which tier (skill-suite-runs.test.sh) asserts SKILL.md names no full-suite run inside a step's cycle, so a run carries at most one tier-all run per PR plus one per repair step, and that case goes red against the pre-#539 SKILL.md text ⟦criterion 4⟧
