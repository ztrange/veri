# Plan for #679 — Cover accepts a non-test proof for a refactor step no test can observe: dead-code deletion and type-only changes

- [x] cover-outcome.sh reads a report ending `COVERED: unreachable` or `COVERED: type-only` with a `PROOF: <proof>` line as exit 3, printing `<kind>: <proof>` on stdout ⟦criterion 1⟧
- [x] cover-outcome.sh exits 2 on `COVERED: unreachable` or `COVERED: type-only` when the report has no `PROOF:` line or says `PROOF: NONE` ⟦criterion 2⟧
- [x] cover-outcome.sh still exits 1 on `COVERED: no` when the report also carries a `PROOF:` line ⟦criterion 2⟧
- [x] cover-outcome.sh still exits 0 printing CAUGHT_BY on `COVERED: yes`, 1 on `COVERED: no` and 2 on a report with no `COVERED:` line ⟦criterion 3⟧
- [ ] the develop-cover prompt allows `COVERED: unreachable` only for a step that only deletes code no caller reaches, with a `PROOF:` naming every caller and why none reaches the code (none exists, every caller passes a no-op, the value is never read) ⟦criterion 4⟧
- [ ] the develop-cover prompt allows `COVERED: type-only` only for a step that changes only types, with a `PROOF:` that is the type-check command the leaf ran green ⟦criterion 5⟧
- [ ] the develop-cover prompt says a step moving or reshaping runtime code is never `unreachable` or `type-only`, that reachable code no test watches is `COVERED: no`, and its report block carries a `PROOF:` line ⟦criterion 6⟧
- [ ] SKILL.md's Cover step reads the cover report through cover-outcome.sh: exit 3 goes on to Transform posting the proof in the Cover comment without bailing or running coverage-blocker.sh, exit 2 bails as `no-verdict` ⟦criterion 7⟧
- [ ] SKILL.md reruns a type-only step's proof command after its transform commits, a non-zero exit rejecting the transform as transform-touches-tests.sh exit 1 does ⟦criterion 8⟧
- [ ] SKILL.md's Scope & plan tells a refactor-kind planner to fold a deletion into the step that makes the code dead, never leaving a no-op for a later step to delete ⟦criterion 9⟧
- [ ] the refactor plan verifier `_verify-plan-refactor.md` REJECTs a step that leaves a no-op in place for a later step to delete ⟦criterion 10⟧
