# Plan for #4375 — The verifier takes --branch-base <sha> from the conductor's record, not a remote-tracking ref

- [ ] verify.sh given `--branch-base <sha>` reads its run lines at that sha, not at the merge base of a rewritten origin/HEAD ⟦criterion 1⟧
- [ ] run-verdict.sh finds the phase past a `--branch-base <sha>` pair and hands the flag on to verify.sh
- [ ] the fused red, green, refactor and plan verdict launches forward `--branch-base` read from the main tree's `.tdd/issue-<n>-branch-base`, stopping with exit 2 when that record is missing
- [ ] verify.sh with `--branch-base` missing or not matching `^[0-9a-f]{7,40}$` exits 2 naming the flag, and its pin and surround phases take their before-state from it ⟦criterion 2⟧
- [ ] the procedure's verifier call sites and SCRIPTS.md pass `--branch-base <base>`, the recorded base, graded by rows SC602 and CY412 ⟦criterion 3⟧
