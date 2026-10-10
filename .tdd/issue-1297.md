# Plan for #1297 — SKILL.md: a resumed run rebases onto origin/main before its next step

- [x] SKILL.md says a resumed run — one whose worktree and ledger already exist — runs `rebase-onto-default.sh` before its preflight baseline, so the baseline runs on the rebased tip, and that a new branch's run does not rebase there ⟦criterion 1⟧
- [x] SKILL.md says the resume rebase's exit 3 goes on unchanged, its exit 1 goes on from the old base and leaves the conflict to the Draft PR step, and its exit 2 bails as the Draft PR step's does (`no-verdict`) ⟦criterion 1⟧
- [x] The Draft PR step's rebase text in SKILL.md is unchanged by this branch ⟦diff-checked⟧ ⟦criterion 1⟧
- [x] SKILL.md says a resume rebase that moved the branch is published, once the baseline is green, with `push-branch.sh --force-with-lease=<branch>:<pre-rebase-sha>`, never a bare force ⟦criterion 2⟧
- [x] SKILL.md says a red baseline on the resume-rebased tip resets to `<pre-rebase-sha>` before the run bails ⟦criterion 2⟧
- [ ] SKILL.md says a resume rebase that moved the branch is marked in the run log as its own event carrying the pre-rebase and rebased shas, under a name distinct from anything the Draft PR step's rebase records ⟦criterion 3⟧
