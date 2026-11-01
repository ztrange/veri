## skills/vcoord/SKILL.md

| ID | Requirement | Why |
|---|---|---|
| C1 | Invoked as `/vcoord [<lane>] [--resume <file>]`. | |
| C2 | It launches no conductor. It carries standing merge permission in the project repo: its own PRs, and any finished run that meets `vmerge`'s conditions (M2, M13) once its review is OK. It never merges in another repo. | The roles stay separate. Mario, 2026-10-18: both operator skills always include merge permission. |
| C3 | It watches through the P3 script, and re-arms with a single `.` (P4). Routine events, watch expiries and its own progress checks get a single `.`, and never re-ask a pending decision. | 2026-10-20: the pending list re-printed on about 15 routine events — "one would have sufficed". |
| C4 | It instructs the dev session through `SendMessage` and tells the human in one line that it did. It answers every dev-session report with an `ack`, or with the ruling the report prompts. | "why didn't you just send it yourself?" 2026-10-20: "when getting a message from dev do you not ack?" |
| C5 | Decisions go to the human. The dev session receives facts and instructions. | |
| C6 | It owns: order overrides, N changes (including timed ones), one-resume budget raises, filing (`vfile`) and grooming (`vgroom`). | |
| C7 | It proposes `priority` for issues that make future runs cheaper, and for issues that give the human something usable, or feedback on a plan, sooner. | |
| C8 | Unattended, it sends the dev session only the message kinds the human approved (default: refill an empty slot). | |
| C9 | It never fixes veri by hand. It files the issue. | "why did you fix it instead of creating an issue". |
| C10 | It never says that `vgroom` or `vfile` does not exist. | PR #2061's review: lines 46-49 still said vgroom does not exist; vfile landed in #1841. |
| C11 | Filing goes through `/vfile`; it names no other filer. | Filing is sent to `/vfile` alone. |
| C12 | It sends a merge instruction for a run, or merges one itself, only after reading the dev session's review report for that PR and either answering each caveat in it by name or seeing the report say there is none. | Same incident: "merge" was sent from the ✅ Done comment, before the caveats were read. |
| C13 | It parks an issue only through the park script, and on resume reads the parked set through the parked-set script, never from a handoff or memory; un-parking removes the `parked` label. | Same as D13: the coordinator's parks were kept in its handoff file and local memory. |
| C14 | At start, the coordinator switches off, for its own session only, every claude.ai connector loaded in it, with the desktop app's per-session connector tool, and never changes the account's settings. It needs none of them. | Their tool definitions are re-read on every turn: ~20k tokens on the coordinator, 2026-10-23. |
| C15 | The *Watching* section names `$S/watch-runs.sh` as the blocking watch of P3, and says a Monitor (or a background command) runs `watch-runs.sh` itself, never a hand-written script. | The repo's watcher is tested; each operator's hand-written copy was not, and the dev session's copy reported two false "#2173 exited" events on 2026-10-24 while the conductor was alive. |
| C16 | The *Watching* section says `watch-runs.sh` prints one line per conductor exit, and does not say it reports conductor starts or merges to the default branch. | `watch-runs.sh` reports exits only; the sentence claiming starts and merges was left ungraded by #2336 and tells the coordinator to wait for events the watch never prints. |
| C17 | It runs `vmerge` and `vjudge` through a subagent on the cheapest model that can do the job, briefed to return at most 10 lines, reading the skill at `<base dir>/../<skill>/SKILL.md`. | The body stays out of a long-lived context. |
| C18 | It loads `vhandoff` itself, by reading `<base dir>/../vhandoff/SKILL.md`. | It needs the role's own state. |
