# Plan for #3490 — queued-merge.sh on a non-tdd branch demands Closes lines for every ledger on main

- [x] queued-merge.sh on a branch not named tdd/<n>-… whose PR body closes every ledger the PR adds or changes (the .tdd/issue-*.md files in git diff --name-only origin/main...HEAD) merges, ignoring the ledgers already on main that the PR does not touch, and a changed file outside .tdd/ named issue-<n>.md is not demanded; pinned by a real-git process case (@pytest.mark.process), not a faked git ⟦added⟧ ⟦criterion 1⟧
- [x] queued-merge.sh on a branch not named tdd/<n>-… still refuses with exit 2, naming the missing line, when the PR body lacks Closes #<n> for a ledger .tdd/issue-<n>.md the PR adds; pinned by a case ⟦criterion 2⟧ ⟂ retired unpinnable
