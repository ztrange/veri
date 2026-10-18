# Plan for #1672 — The claim-at-launch checks fail open: an unanswered gh or remote lookup, or a nonexistent issue, reads as unclaimed

- [x] unlabel-issue.sh given no argument, or a non-numeric issue argument such as `abc`, exits 2 with stderr naming the bad argument, and asks gh nothing ⟦criterion 1⟧
- [x] unlabel-issue.sh on a nonexistent issue exits 2 with stderr naming the missing issue, while an existing issue that does not carry the label still exits 0 ⟦criterion 1⟧
- [x] unlabel-issue.sh whose label-removal request gets no answer from gh (a failure that is not a 404) exits 2 with stderr naming the unanswered request ⟦criterion 1⟧ ⟂ refactor pending
- [ ] issue-worktree.sh cutting a fresh branch exits 2, stderr naming the remote-branch lookup, when the origin `ls-remote` for `tdd/<n>-*` branches gets no answer, instead of treating silence as unclaimed ⟦criterion 2⟧
- [ ] issue-worktree.sh cutting a fresh branch exits 2, stderr naming the open-PR lookup, when the open-PR lookup gets no answer from gh, instead of treating silence as unclaimed ⟦criterion 2⟧
- [ ] issue-worktree.sh resuming the run's own existing issue branch still hands back its worktree (exit 0) when the remote-branch and open-PR lookups would get no answer ⟦criterion 2⟧
- [ ] issue-worktree.sh cutting a fresh branch from an origin naming a GitHub host other than github.com (a GitHub Enterprise host) runs the open-PR check, refusing with exit 2 when an open PR says `Closes #<n>` ⟦criterion 3⟧
