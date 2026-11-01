## skills/vhandoff/SKILL.md

| ID | Requirement | Why |
|---|---|---|
| H1 | Invoked as `/vhandoff dev\|coord`. Resume is `/vdev --resume <file>` or `/vcoord --resume <file>`. | |
| H2 | For the dev role, it refuses while `$S/merge-lock.sh holder` names a live holder, or a launch is half done. | A reset mid-merge would hand the next session a merge it does not know is running; a lock held by a dead process does not block the handoff. |
| H3 | It writes the handoff to `.tdd/handoff-<role>.md` in the main clone. | `/tmp` and scratch dirs vanish mid-run. |
| H4 | It carries: time, main sha and tag, live conductors (issue, step k/n, phase, cost), parked runs with their reason, PRs awaiting merge, N and any timed change, overrides and one-off permissions with their expiry, pending decisions. | |
| H5 | It carries no rule that the role's skill states (P2). | |
| H6 | It is ≤40 lines, and every item names its issue number and title. | |
| H7 | It stops no conductor. | Conductors are detached and outlive both sessions. |
| H8 | It prints the resume command in a fenced block. | |
