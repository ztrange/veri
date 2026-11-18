# Plan for #4374 — The conductor records the run's branch base sha itself, and a resume reads it back from the record

- [ ] A fresh launch writes the merge base of HEAD and origin/HEAD, read once the branch is cut, to the main working tree's `.tdd/issue-<n>-branch-base`, and reads its fast command at it ⟦criterion 1⟧
- [ ] A resume reads its fast command at the recorded base, never at the merge base of a rewritten origin/HEAD ⟦criterion 2⟧
- [ ] A resume whose record is missing, unreadable, not hex or not an ancestor of HEAD exits 2 naming the record, never recomputing the base ⟦criterion 3⟧
- [ ] The run's records on refs/veri/runs/<n> carry `issue-<n>-branch-base` ⟦criterion 4⟧
- [ ] A resume with no local record restores the carried one only when it is a hex commit name that is an ancestor of HEAD ⟦criterion 4⟧
- [ ] rebase-onto-default.sh, on an exit 0 that rebased a run's branch, re-records the base as the onto sha it rebased onto ⟦criterion 5⟧
- [ ] SCRIPTS.md, PREFLIGHT.md and CLAUDE.md state where the record lives and who writes it (rows SC594, SC595, PF72, CM305), regraded ⟦criterion 6⟧
