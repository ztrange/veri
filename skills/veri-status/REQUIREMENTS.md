## skills/veri-status/SKILL.md

| ID | Requirement | Why |
|---|---|---|
| A1 | Invoked as `/veri-status`. It reports what changed since the previous ask, whose time is kept in `.tdd/status-last`. | |
| A2 | Sections, in order: **Landed** (PR, tag, capability) · **Running** (per issue: awake wall time, steps k/n, phase, cost, model split) · **Queue** (counts by label, blockers, drain ETA at the current N) · **Waiting** (ready PRs, empty slots, bails, decisions). | The format Mario specified twice. |
| A3 | Every ETA comes from observed rates and carries a range. | |
| A4 | It reads `status.sh --json`, `metrics.sh`, `git tag` and `gh`. More than three reads go to one subagent. | |
| A5 | It reads issue states, labels, blockers and wall times from `.tdd/report-cache.json` after one `report-cache.sh refresh`, the same file `/vreport` reads. `status.sh`, `metrics.sh` and `git tag` stay direct reads. | The two skills read the same issue data; one cache keeps their figures consistent and their asks cheap. |
| A6 | The **Running** section has one block per live run: a run whose `.tdd/wt/<n>/.tdd/conductor.pid` names a pid that answers `kill -0` and whose start time matches the one recorded on the lock's second line, the same definition `skills/tdd/SKILL.md` preflight step 1.2 uses. A lock whose pid is dead or reused is not a running run. | A reused pid must never list a bailed run as running (#2537). |
| A7 | The sentence stating what each cached issue carries lists `links`, and `body` for a PRD only, and no `comments`. | It reads the same file as `/vreport`, so its list must match what that file holds. |
| A8 | Every date and time the report shows is in the machine's local timezone, whatever zone its source carries; `.tdd/status-last` stays ISO 8601. | The reader acts on the report in local time, and `gh` and the cache read in UTC. |
