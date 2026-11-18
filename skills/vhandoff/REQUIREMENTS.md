## skills/vhandoff/SKILL.md

| ID | Requirement | Why |
|---|---|---|
| H1 | Invoked as `/vhandoff dev`. Resume is `/vdev --resume <file>`. | One operator role (PRD 026.5). |
| H2 | For the dev role, it refuses while `$S/merge-lock.sh holder` names a live holder, or a launch is half done. | A reset mid-merge would hand the next session a merge it does not know is running; a lock held by a dead process does not block the handoff. |
| H3 | It writes the handoff to `.tdd/handoff-<role>.md` in the main clone. | `/tmp` and scratch dirs vanish mid-run. |
| H4 | It carries: time, main sha and tag, live conductors (issue, step k/n, phase, cost), parked runs with their reason, PRs awaiting merge, N and any timed change, pending decisions; for overrides and one-off permissions it copies none and points at the role state file (`.tdd/role-<role>.state`), where they are written. | P9: an override is written down in the role state file, never in a handoff (#3245). |
| H5 | It carries no rule that the role's skill states (P2). | |
| H6 | It is ≤40 lines, and every item names its issue number and title. | |
| H7 | It stops no conductor. | Conductors are detached and outlive both sessions. |
| H8 | It prints the resume command in a fenced block. | |
| H10 | The dev handoff also carries whether `.tdd/github-outage` exists in the main working tree, read from the file when the handoff is written, and, when it exists, each PR url it lists, in the file's order. | A handoff carries state, and a reset mid-outage must not resume merging (PRD 033, VO9; P2). |
| H11 | In a session that has the app's `start_session` tool, `/vhandoff dev` writes nothing and says the dev session resets itself and recovers from its role state file; in a session without it, it works as the other rows say. | The desktop dev session needs no handoff (RC4); the terminal keeps `--resume`, which reads this skill's file (PRD 026, settled 2026-11-15). |
| H12 | The dev handoff carries the `Stack` section's lines as `status.sh` prints them, and where none is printed it says no stack is named. | A fresh session must not guess the freeze. |
