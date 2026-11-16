# Plan for #4170 — PRD 034.1b: a run in a stacking repository is cut from the stack and ends Done as a draft

- [x] git.run_base answers the stack branch where stack-branch.sh would exit 0, the default branch where it would exit 3, and raises the refusal where it would exit 2 ⟦criterion 1⟧
- [x] issue-worktree.sh cuts a new run's branch from origin/<stack> as just fetched where a stack branch is named ⟦criterion 2⟧
- [x] with no <stack> on origin, issue-worktree.sh first pushes it at the default branch's tip, never forced, then cuts from it ⟦criterion 3⟧
- [ ] a refused or unanswered push of the stack exits 2 with no branch and no worktree made ⟦criterion 3⟧
- [ ] a push refused because the stack now exists on origin is followed by a fetch and the cut from origin/<stack>, exit 0 ⟦criterion 3⟧
- [ ] rebase-onto-default.sh, with and without --graded-only, rebases onto origin/<stack> where a stack branch is named, exit 3 when the branch already contains it ⟦criterion 4⟧
- [ ] where no stack branch is named, issue-worktree.sh and rebase-onto-default.sh push no branch to origin ⟦criterion 5⟧
- [ ] SKILL.md step 2.3 opens the draft PR against the stack branch where one is named and defines the run's base once (PL71, GD17), within its byte ceiling, graded ⟦criterion 6⟧
- [ ] SKILL.md stays within its byte ceiling ⟦criterion 7⟧
- [ ] DRAFT-PR.md: a stacked run skips pr-ready.sh and every wait-ci.sh call, ticks no ⟦full-suite⟧ line, drops the WIP: prefix leaving a draft, ends Done (DP109, DP110), graded ⟦criterion 8⟧
- [ ] the retitle that drops the WIP: prefix leaves a stacked run's PR a draft ⟦criterion 9⟧
- [ ] SCRIPTS.md's issue-worktree.sh and rebase-onto-default.sh entries state the stack's place (SC196, SC197), graded ⟦criterion 10⟧
