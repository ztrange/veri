## skills/veri-status/SKILL.md

| ID | Requirement | Why |
|---|---|---|
| A1 | Invoked as `/veri-status`. It reports what changed since the previous ask, whose time is kept in `.tdd/status-last`. | |
| A2 | Sections, in order: **Landed** (PR, tag, capability) · **Running** (per issue: awake wall time, steps k/n, phase, cost, model split) · **Queue** (counts by label, blockers, drain ETA at the current N) · **Waiting** (ready PRs, empty slots, bails, decisions). | The format Mario specified twice. |
| A3 | Every ETA comes from observed rates and carries a range. | |
| A4 | It reads `status.sh --json`, `metrics.sh`, `git tag` and `gh`. More than three reads go to one subagent. | |
