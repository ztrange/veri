# Plan for #3972 — PRD 022.13: parked-issues.sh reads only a trusted parked comment

- [x] parked_issues.main takes the last trusted ### ⏸ Parked comment: when the last parked comment is untrusted, the printed line carries the trusted comment's cause, unblock text and ready/waiting answer ⟦criterion 1⟧
- [x] an issue whose only parked comments are untrusted exits 2 with the has-no-parked-comment line ⟦criterion 2⟧
- [x] a comments answer that is not a list of comment records exits 2 naming the read, printing no row
- [x] every reader of issue comments under veri/ goes through github.trusted_comment, or is listed with why it need not; a ratchet case names any that does not
- [ ] the parked-issues.sh entry of SCRIPTS.md says the comment read is the last trusted one ⟦criterion 3⟧
