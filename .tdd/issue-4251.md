# Plan for #4251 — PRD 013.23: the PR names a plan's growth past the bound and where it would split best

- [x] `ledger-growth.sh split <ledger-file>` exits 0 printing the growth line when N − P > B, P the ledger's steps at the oldest `plan: scope` commit, repair lines uncounted; exits 3 printing nothing at N − P ≤ B ⟦criterion 1⟧
- [x] its second line names the criterion boundary leaving the sides' counts closest, the earlier on a tie, or that there is no split point ⟦criterion 2⟧
- [ ] it exits 2, nothing on stdout and one stderr line, on bad arguments, an unreadable ledger, no `plan: scope` commit, a malformed `VERI_STEP_GROWTH_PERCENT` or a set `VERI_STEP_GROWTH` ⟦criterion 3⟧
- [ ] DRAFT-PR.md sub-step 2 runs it and puts its output under `## Plan growth` before `## Owed steps`; row DP added; skills/tdd/GRADED regraded ⟦criterion 4⟧
- [ ] SCRIPTS.md lists `$S/ledger-growth.sh split <ledger-file>` as an entry of its own; row SC added; regraded ⟦criterion 5⟧
