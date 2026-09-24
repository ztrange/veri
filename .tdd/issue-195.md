# Plan for #195 — Open the draft PR when the plan is committed, not when the run ends

- [x] SKILL.md step 2 pushes the branch and opens a draft PR whose body carries Closes #<n> and whose title marks the work in progress, right after the plan commit and before the Plan comment ⟦criterion 1⟧
- [x] SKILL.md updates the PR body with the done-of-total step count read from the ledger at each step tick ⟦criterion 2⟧ ⟂ refactor pending
- [ ] SKILL.md step 4 creates no PR: it rewrites the existing one's title and body and marks it ready for review ⟦criterion 3⟧
- [ ] SKILL.md resume reuses the open PR already on the run's branch and never creates a second one ⟦criterion 4⟧
- [ ] SKILL.md Bailing leaves the draft PR open carrying the bail diagnostic, in place of opening no PR ⟦criterion 5⟧
- [ ] solvable-issues.sh leaves out an issue claimed by an open PR saying Closes #<n> even when no conductor pid answers ⟦criterion 5⟧
- [ ] CONTEXT.md, the solvable-issues.sh header comment and a new ADR state that an open PR is the cross-machine claim and the pid lock is only the same-machine worktree guard ⟦criterion 6⟧
