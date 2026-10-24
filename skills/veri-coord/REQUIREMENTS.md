## skills/veri-coord/SKILL.md

| ID | Requirement | Why |
|---|---|---|
| C1 | Invoked as `/veri-coord [<lane>] [--resume <file>]`. | |
| C2 | It launches no conductor. It carries standing merge permission in the project repo: its own PRs, and any finished run that meets `veri-merge`'s conditions (M2, M13) once its review is OK. It never merges in another repo. | The roles stay separate. Mario, 2026-10-18: both operator skills always include merge permission. |
| C3 | It watches through the P3 script, and re-arms with a single `.` (P4). Routine events, watch expiries and its own progress checks get a single `.`, and never re-ask a pending decision. | 2026-10-20: the pending list re-printed on about 15 routine events — "one would have sufficed". |
| C4 | It instructs the dev session through `SendMessage` and tells the human in one line that it did. It answers every dev-session report with an `ack`, or with the ruling the report prompts. | "why didn't you just send it yourself?" 2026-10-20: "when getting a message from dev do you not ack?" |
| C5 | Decisions go to the human. The dev session receives facts and instructions. | |
| C6 | It owns: order overrides, N changes (including timed ones), one-resume budget raises, filing (`veri-file`) and grooming (`veri-groom`). | |
| C7 | It proposes `priority` for issues that make future runs cheaper. | |
| C8 | Unattended, it sends the dev session only the message kinds the human approved (default: refill an empty slot). | |
| C9 | It never fixes veri by hand. It files the issue. | "why did you fix it instead of creating an issue". |
| C12 | It sends a merge instruction for a run, or merges one itself, only after reading the dev session's review report for that PR and either answering each caveat in it by name or seeing the report say there is none. | Same incident: "merge" was sent from the ✅ Done comment, before the caveats were read. |
| C13 | It parks an issue only through the park script, and on resume reads the parked set through the parked-set script, never from a handoff or memory; un-parking removes the `parked` label. | Same as D13: the coordinator's parks were kept in its handoff file and local memory. |
