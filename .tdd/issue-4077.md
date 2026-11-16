# Plan for #4077 — PRD 013.22: a parked run resumes on the owner's decision

- [x] park-decision.sh <n> prints the bodies of the trusted comments posted after the newest trusted parked comment, oldest first, exit 0 ⟦criterion 1⟧
- [x] park-decision.sh <n> exits 3 when no trusted comment follows the newest parked comment, or the issue has none ⟦criterion 1⟧
- [x] a stranger's comment, even one holding the exact decision text or a parked heading, never counts ⟦criterion 1⟧
- [x] text inside a quote or a code fence is not part of a decision; a comment holding only such text is not counted ⟦criterion 1⟧
- [x] a comments answer gh does not give, or that is not comment records, is exit 2; bad arguments exit 2 ⟦criterion 1⟧
- [ ] SKILL.md step 1 says a resumed run reads park-decision.sh before its first leaf and applies a plan-changing decision as a plan: rewrite commit ⟦criterion 2⟧
