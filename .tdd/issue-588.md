# Plan for #588 — a scope-loop case in the suites fails intermittently on CI (run 36711106787)

- [ ] a helper that registers a PR in a VERI_GH_JSON fixture never loses an entry when two registrations interleave between one's read of the PR lines and its write of prs.json — proven by a unit suite that forces that interleaving with no waiting ⟦criterion 2⟧
- [ ] parallel-conductors.test.sh registers its PRs through that helper, so the 12/13 ready-PR race in its bail case cannot drop a PR ⟦criterion 2⟧
- [ ] confirm the issue thread's Plan + cause comment names the failing case (parallel-conductors.test.sh:391, continue mode) and its cause (the open_pr fixture's lost update), read from run 36711106787 attempt 1's log ⟦human-owed⟧ ⟦criterion 1⟧
