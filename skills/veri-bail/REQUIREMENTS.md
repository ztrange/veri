## skills/veri-bail/SKILL.md

| ID | Requirement | Why |
|---|---|---|
| B1 | Invoked as `/veri-bail <issue>`. `veri-dev` calls it on every exit that is not ✅ Done. | |
| B2 | It classifies from facts before acting: `$S/stop-reason.sh <issue>` for a usage limit or sleep, otherwise the run's `bail cause=` event read with `$S/classify-bail.sh <cause>` (killed-stuck, a budget, revise-exhausted, a red baseline, a ledger question). | Not from the comment's wording, and each class has one named source. |
| B3 | A usage limit or sleep is not a bail: in the run's worktree `.tdd/wt/<n>`, it saves every uncommitted leaf edit, untracked files included, as a patch under `.tdd/`, restores that worktree's tree, and resumes when usage is back. | The leaf's edit lives in the run's worktree; saved from the main clone the patch is empty and the edit is lost (PR #2175 review). |
| B4 | A first real bail is resumed once with `$S/detach-leaf.sh $S/run-conductor.sh <n>`, with `VERI_NEW_SKILL=1` when the fix it needs landed after the commit recorded in `.tdd/issue-<n>-skill-commit`. | The resume command and the "landed after" test are things an agent can run. |
| B5 | A second bail is parked: one issue comment with the cause and what would unblock it, then the next issue is taken. | |
| B6 | Budget raises and ledger amendments come only from the coordinator or the human, and apply to that one resume. | |
| B7 | It leaves the run's logs in place. | |
