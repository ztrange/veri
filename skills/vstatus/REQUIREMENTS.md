## skills/vstatus/SKILL.md

| ID | Requirement | Why |
|---|---|---|
| A1 | Invoked as `/vstatus`. It reports what changed since the previous ask, whose time is kept in `.tdd/status-last`. | |
| A2 | Sections, in order: **Landed** (PR, tag, capability) · **Running** (per issue: awake wall time, steps k/n, phase, cost, model split) · **Queue** (counts by label, blockers, drain ETA at the current N) · **Waiting** (ready PRs, empty slots, bails, decisions). | The format Mario specified twice. |
| A3 | Every ETA comes from observed rates and carries a range. | |
| A4 | The skill's reads section tells it to run `status.sh --report` once and print the output verbatim. It names no other read, and it spawns no subagent. | The skill's whole cost becomes one command and its output. |
| A5 | The skill states that issue data comes from the snapshot `status.sh --report` reads, whose age the report's Queue section prints, and that the skill itself never runs `report-cache.sh refresh`. | A stale figure is acceptable only when labelled, and the ask must not wait on GitHub. |
| A6 | The skill defines a live run by pointing at `status.sh --report`'s **Running** section, and it restates no liveness check of its own. | One definition, in the code that applies it. |
| A11 | The skill says that when `status.sh --report` exits 2, it reports that and stops, printing no figures of its own. | A failed render must not turn back into a model assembling figures. |
