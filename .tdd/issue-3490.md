# Plan for #3490 — queued-merge.sh on a non-tdd branch demands Closes lines for every ledger on main

- [ ] queued-merge.sh on a branch not named tdd/<n>-… whose PR body closes every ledger the PR adds or changes (the .tdd/issue-*.md files in git diff --name-only origin/main...HEAD) merges, ignoring the ledgers already on main that the PR does not touch; pinned by a case ⟦criterion 1⟧
- [ ] queued-merge.sh on a branch not named tdd/<n>-… still refuses with exit 2, naming the missing line, when the PR body lacks Closes #<n> for a ledger .tdd/issue-<n>.md the PR adds; pinned by a case ⟦criterion 2⟧
