# Plan for #4110 — PRD 031.3b: closing a legacy coverage issue puts its refactor issue back on the queue

- [ ] `release-covered.sh <n>` releases #<m> through `release-issue.sh <m>` when #<n> is `Cover the behaviour #<m> refactors` and #<m> is open and `bailed`, prints `released #<m>`, exit 0 ⟦criterion 1⟧
- [ ] it exits 3 changing no label for another title shape, a closed #<m>, or #<m> not `bailed` ⟦criterion 2⟧
- [ ] it exits 2 when `gh` gives no answer or `release-issue.sh` exits 2 ⟦criterion 3⟧
- [ ] `solvable-issues.sh` lists #<m> once released and #<n> closed with its draft PR open, and not while #<n> is open ⟦criterion 4⟧
- [ ] docs: `LEGACY.md` runs it after `DRAFT-PR.md` sub-step 4, `SCRIPTS.md` entry, rows and grades ⟦criterion 5⟧
