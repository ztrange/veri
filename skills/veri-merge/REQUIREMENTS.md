## skills/veri-merge/SKILL.md

| ID | Requirement | Why |
|---|---|---|
| M1 | Invoked as `/veri-merge <issue-or-PR>`. It merges with the standing permission `veri-dev` and `veri-coord` carry in the project repo, or with explicit permission; never in another repo. | |
| M2 | It merges only when all of these hold: the last comment is ✅ Done; the ledger has no unchecked step and no `⟂ refactor pending`; every ⟦human-owed⟧ line is ticked. | |
| M3 | An unticked ⟦human-owed⟧ line gets one read-only review subagent. NOT OK goes to the human. | |
| M4 | It holds the merge lock from the first write to the last, and releases it on every exit path. | |
| M5 | If `main` moved, it rebases and force-pushes with `--force-with-lease` pinned to the recorded sha. | The bare form silently clobbers. |
| M6 | An empty or missing CI rollup is not a pass. | |
| M7 | The CI wait is capped at 2× the average of the last 5 runs, and at 10 minutes. | "30 min is too much." |
| M8 | A zero-step CI failure with a payments annotation goes to the human as billing. | |
| M9 | It runs `make merge-gates` when the repo has that target, and refuses to merge while `prose-owed.sh` lists any unit (T6). | |
| M10 | Deleting the branch, cutting the tag and removing the worktree each happen only after `state == MERGED` is read. | Deleting an open PR's head closes it (PR #74). |
| M11 | The tag is `vN.M`, chosen with `--sort=-v:refname`, with the capability in the issue's words as its message. | Lexically `v0.9` > `v0.10`. |
| M12 | It reports one line: PR url, merge sha, tag. | |
| M13 | It does not merge a run that ended with an open question for the human. | Merging would answer the question for them. |
