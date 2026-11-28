# Plan for #4868 — TS helper digest spans sibling test cases: a rebase adding any case to the file stales every frozen record in it and bails needs-user

- [ ] helper_digest of a JS case is unchanged when a sibling it(...) joins the describe below its helper, and changes when the helper's assertion line is edited ⟦criterion 1⟧
- [ ] helper_digest of a Python case is unchanged when a sibling test method joins the class below its helper, and changes when the helper's assertion line is edited ⟦criterion 2⟧
- [ ] check-earlier accepts a helpers: record holding the unscoped digest over the unchanged file and re-records it to the scoped one ⟦criterion 3⟧
- [ ] check-earlier exits 0 after a rebase only adds a sibling case to the frozen case's file ⟦criterion 4⟧
