# Plan for #1656 — A run claims its issue at launch: refuse an issue already branched or claimed, then drop the opt-in label

- [x] A fresh run refuses an issue that already has an issue branch `tdd/<n>-*` on the remote: `issue-worktree.sh <n> <slug>`, with no worktree for the issue yet, exits 2 with stderr naming that remote branch, and leaves no worktree directory, no new local branch and no commit behind ⟦criterion 1⟧
- [x] A fresh run refuses an issue that an open PR claims (its body says `Closes #<n>`): `issue-worktree.sh <n> <slug>`, with no worktree for the issue yet, exits 2 with stderr naming that PR, and leaves no worktree directory, no new local branch and no commit behind ⟦criterion 1⟧
- [ ] A resume still starts: when the issue's worktree and its ledger `.tdd/issue-<n>.md` already exist, `issue-worktree.sh <n> <slug>` prints that worktree's path and exits 0 even though the issue's branch is on the remote and an open PR claims the issue ⟦criterion 1⟧
- [ ] A script removes the opt-in label (`VERI_LABEL`, default `ready-for-agent`) from a named issue, so `solvable-issues.sh` no longer lists it; run on an issue that does not carry the label it exits 0 and is not an error ⟦criterion 2⟧
- [ ] `SKILL.md` tells the conductor to run that label-removal script once preflight passes and before step 2's planning, on a fresh run ⟦criterion 2⟧
- [ ] `SKILL.md` names the label removal as the run's first claim and the draft PR as its durable claim, and says a bailed or parked issue stays unlabelled until a human relabels it, as parking already does ⟦criterion 3⟧
