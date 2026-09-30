# Plan for #588 — a scope-loop case in the suites fails intermittently on CI (run 36711106787)

- [x] a helper that registers a PR in a VERI_GH_JSON fixture never loses an entry when two registrations interleave between one's read of the PR lines and its write of prs.json — proven by a unit suite that forces that interleaving with no waiting ⟦criterion 2⟧
- [x] CLAUDE.md's unit-suite count matches the unit suites that exist, so claude-md-counts.test.sh passes with the new unit/gh-fixture.test.sh (it reports 21 where 22 exist) ⟦added⟧ ⟦criterion 2⟧
- [x] parallel-conductors.test.sh registers its PRs through that helper, so the 12/13 ready-PR race in its bail case cannot drop a PR ⟦criterion 2⟧
- [x] no-nested-suites.test.sh passes: claude-md-counts.test.sh:302 names gh-fixture.test.sh outside a comment in a shape that file treats as launching it, with no exemption recorded ⟦added⟧ ⟦criterion 2⟧ ⟂ refactor pending
- [ ] confirm the issue thread's Plan + cause comment names the failing case (parallel-conductors.test.sh:391, continue mode) and its cause (the open_pr fixture's lost update), read from run 36711106787 attempt 1's log ⟦human-owed⟧ ⟦criterion 1⟧
