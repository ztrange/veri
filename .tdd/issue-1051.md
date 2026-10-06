# Plan for #1051 — solvable-issues.sh drops an issue when another closes mid-listing: REST page offsets shift

- [x] With a fake `gh api` serving the issue listing in pages that shift between calls (an item closed and removed from the open-only listing after page 1 is served), solvable-issues.sh still prints every solvable issue the fake holds ⟦criterion 1⟧
- [x] With a fake `gh api` serving the PR listing in pages that shift between calls (a PR closed after page 1 is served), an issue claimed by an open PR on a later page is still left out of solvable-issues.sh's output ⟦criterion 1⟧
- [ ] Output, ordering bands, and exit codes are unchanged for a listing that does not shift ⟦full-suite⟧ ⟦criterion 2⟧
