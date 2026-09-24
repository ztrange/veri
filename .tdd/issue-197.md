# Plan for #197 — A maintenance utility that reports branches with no PR and local branches never pushed

- [ ] A branch on origin for which no PR has ever been opened is reported, naming the branch, its tip, its commit count ahead of the default branch, and the number and state of the issue its tdd slug name refers to ⟦criterion 1⟧
- [ ] A local branch absent from origin is reported, naming the branch, its tip, how many commits it holds that origin does not, and the worktree holding it when there is one ⟦criterion 2⟧
- [ ] A branch whose PR is merged or closed is left out of the report, and so is the default branch ⟦criterion 3⟧
- [ ] The script exits 0 when it printed a finding and exits 3 with empty stdout when there is nothing to report ⟦criterion 4⟧
- [ ] The script exits 2 with a diagnostic on stderr and empty stdout when the remote is unreachable or gh cannot be read ⟦criterion 4⟧
- [ ] Every finding names the invariant it breaks, so a reader can tell a branch with no PR from a branch that never reached origin ⟦criterion 5⟧
- [ ] The gh issue and pull request documents are read as JSON parsed with python3, under a VERI_GH_JSON fixture directory override that lets the suite drive the script with no network ⟦criterion 5⟧
- [ ] The script writes to no ref: it creates, moves and deletes nothing, and its suite proves the refs are byte-identical after a run ⟦criterion 5⟧
- [ ] CLAUDE.md counts the new script and its suite, and the prose around those counts still describes the scripts truthfully
