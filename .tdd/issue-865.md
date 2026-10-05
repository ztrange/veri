# Plan for #865 — without origin/HEAD, run-conductor runs unpinned and rebase-onto-default, issue-worktree and invisible-work guess or fail unnamed

- [x] run-conductor.sh, with an origin remote, no refs/remotes/origin/HEAD, and a remote whose HEAD names its default branch, pins the run to that branch's tip: the skill-commit record is written, the snapshot is archived, and VERI_SKILL_UNPINNED is not exported ⟦criterion 1⟧
- [ ] run-conductor.sh, with an origin remote, no refs/remotes/origin/HEAD, and a remote whose default branch cannot be resolved, exits 2 before launching the conductor with stderr naming refs/remotes/origin/HEAD, and never runs unpinned ⟦criterion 2⟧
- [ ] rebase-onto-default.sh with no refs/remotes/origin/HEAD resolves the default branch from the remote and answers exit 3, 0 or 1 by the same rules as when the ref is set ⟦criterion 3⟧
- [ ] rebase-onto-default.sh with no refs/remotes/origin/HEAD and a remote whose default cannot be resolved exits 2 with stderr naming refs/remotes/origin/HEAD, HEAD unchanged and no rebase started ⟦criterion 3⟧
- [ ] issue-worktree.sh, with an origin remote and no refs/remotes/origin/HEAD, cuts the issue branch from the remote's own default branch even when a local main exists and the remote's default has another name ⟦criterion 4⟧
- [ ] issue-worktree.sh, with an origin remote, no refs/remotes/origin/HEAD and a remote whose default cannot be resolved, exits 2 with stderr naming refs/remotes/origin/HEAD and creates no worktree ⟦criterion 4⟧
- [ ] issue-worktree.sh with no origin remote at all still falls back to a local main or master as the base ⟦criterion 4⟧
- [ ] invisible-work.sh with no refs/remotes/origin/HEAD resolves the default branch from the remote and reports as it does when the ref is set ⟦criterion 5⟧
- [ ] invisible-work.sh with no refs/remotes/origin/HEAD and a remote whose default cannot be resolved exits 2 with stderr naming refs/remotes/origin/HEAD ⟦criterion 5⟧
- [ ] SKILL.md's *The skill snapshot* section describes the launch resolving the default branch from the remote when refs/remotes/origin/HEAD is absent, refusing with exit 2 when it cannot, and running unpinned only for a launch with no resolvable commit at all ⟦criterion 6⟧
- [ ] SKILL.md's issue-worktree.sh entry describes the default branch's name resolved from the remote when refs/remotes/origin/HEAD is absent, a refusal naming that ref when it cannot be, and the local main/master fallback only when there is no origin remote ⟦criterion 6⟧
- [ ] the branch's diff changes no existing assertion in the touched scripts' suites except one that pins the local main/master guess or the silent unpinned run this issue removes ⟦diff-checked⟧ ⟦criterion 7⟧
- [ ] every case the touched scripts' suites already hold passes ⟦full-suite⟧ ⟦criterion 7⟧
- [ ] the PR body lists by file:line every existing suite assertion the branch changed because it pinned the removed guess ⟦human-owed⟧ ⟦criterion 7⟧
