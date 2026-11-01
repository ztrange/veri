## skills/vmerge/SKILL.md

| ID | Requirement | Why |
|---|---|---|
| M1 | Invoked as `/vmerge <issue-or-PR>`. It merges with the standing permission `vdev` and `vcoord` carry in the project repo, or with explicit permission; never in another repo. | |
| M2 | It merges only when all of these hold: the last comment is ✅ Done; the ledger has no unchecked step and no `⟂ refactor pending`; every ⟦human-owed⟧ line is ticked. | |
| M3 | An unticked ⟦human-owed⟧ line gets one read-only review subagent. NOT OK goes to the human. | |
| M4 | It takes the merge lock with `$S/merge-lock.sh take --pid <driver>` before its first write, where `<driver>` is the long-lived process driving the merge (`$PPID` in an agent session's Bash call), and releases it with `$S/merge-lock.sh release --pid <driver>` on every exit path; a merge that stops on a conflict or a refused push leaves the lock held and says so, for a human to clear with `$S/merge-lock.sh release --force`. | One merge lands at a time, and a stopped merge is visible instead of letting the next one rebase onto half-finished work. |
| M5 | If `main` moved, it rebases and force-pushes with `--force-with-lease` pinned to the recorded sha. | The bare form silently clobbers. |
| M6 | An empty or missing CI rollup is not a pass. | |
| M7 | The CI wait is `$S/wait-ci.sh`, called again on exit 3, capped at 2× the average of the last 5 runs, and at 10 minutes. | "30 min is too much." The wait is a blocking script (P3), not a wait the agent improvises. |
| M8 | A zero-step CI failure with a payments annotation goes to the human as billing. | |
| M9 | It runs `make merge-gates` when the repo has that target, and refuses to merge while `$S/prose-owed.sh` lists any unit or gives no answer (T6). | A missing or failing check never reads as "nothing owed": in PR #2166 a wrong script path printed nothing and skipped the refusal. |
| M10 | Deleting the branch, cutting the tag and removing the worktree each happen only after `state == MERGED` is read. | Deleting an open PR's head closes it (PR #74). |
| M11 | The tag is `vN.M`, chosen with `--sort=-v:refname`, with the capability in the issue's words as its message. | Lexically `v0.9` > `v0.10`. |
| M12 | It reports one line: PR url, merge sha, tag. | |
| M13 | It does not merge a run that ended with an open question for the human. | Merging would answer the question for them. |
| M14 | A merge that stops because CI is red, or because a gate before the merge refuses, releases the merge lock before it exits; only a conflict or a refused push (M4) keeps it held. | A red-CI stop otherwise blocks every later merge until the lock is removed by hand (#2224 waited 31 min). |
| M15 | The merge's Gates and CI steps run under `$S/merge-lock.sh gate --pid <driver> -- …` and its rebase and push under `$S/merge-lock.sh gate --keep --pid <driver> -- …`, and the merge-lock section lists the red-CI and refused-gate stops among those that release the lock. | A release rule only stated in prose is skipped; the gate in the command releases the lock whatever the reader does. |
| M16 | Before it rebases, it fetches `origin` and checks that the worktree's HEAD contains the remote branch's head (`git merge-base --is-ancestor origin/<branch> HEAD`); when it does not, it stops before the rebase and the push, pushes nothing and reports it, as a refused push does. | A lease pinned to a sha the worktree lacks matches the remote, and the force-push silently drops that commit; an unfetched `origin/main` rebases onto a stale main. |
| M17 | After the rebase and before the push, the merge runs `$S/grade-prose.sh --convert` at the worktree root and commits any GRADED line it rewrote, so the merged tree's `prose-owed.sh` exits 0 without a person recomputing a signature while reading a conflict. | A rebase onto a moved `main` changes the formula a GRADED line was signed under; re-signing by hand mid-conflict is error-prone. |
