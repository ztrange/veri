# Plan for #4322 — PRD 034.6: vmerge joins a hand-developed pull request based on the stack branch

- [ ] queued-merge.sh joins a pull request whose head branch is `hand/<n>-x` (no ledger, no run state) to the stack with real git: exit 0, the stack pushed ⟦criterion 3⟧
- [ ] vmerge's *Preconditions* states the hand pull request variant: no `✅ Done` or ledger bullet, its body has `Closes #<n>`, the review's OK is the gate, the human-owed, open-question and `lsof` bullets still apply; row M43 graded ⟦criterion 1⟧
- [ ] the same variant requires every commit of `origin/<stack>..<head>` to end `(#<n>)` for the issue `Closes` names, one that does not a failed precondition, named; row M43 regraded ⟦criterion 2⟧
- [ ] no script or skill this change touches names a repository, issue, branch, label or person ⟦criterion 4⟧
