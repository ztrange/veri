# Plan for #3971 — PRD 022.12: release-issue.sh releases a preflight-refused issue only on veri's comment

- [x] release_issue._preflight_refused reads the comments with their authors and holds only on a trusted one: an issue whose only ### ⛔ Preflight refused comment is untrusted exits 3 with the nothing-to-release line and nothing is written ⟦criterion 1⟧
- [x] a trusted comment holding ### ⛔ Preflight refused other than at its start does not make the issue releasable ⟦criterion 2⟧
- [x] a trusted comment starting with ### ⛔ Preflight refused still makes the issue releasable ⟦criterion 3⟧
- [ ] comments gh gives no answer for, or answers in the wrong shape, exit 2 naming the read and nothing is written
- [ ] the release-issue.sh entry of SCRIPTS.md says the comment must be veri's (trusted) and start with the heading ⟦criterion 4⟧
