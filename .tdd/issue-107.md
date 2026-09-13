# Plan for #107 — Every run writes an event log: launches, exits, verdicts and each leaf's time, tokens and cost

- [x] `event.sh <event> [key=value …]` appends one line to `.tdd/events.jsonl` that parses as JSON and carries `ts`, `issue`, `actor`, `phase`, `step`, `event` and `attempt`, plus every `key=value` payload given
- [x] `event.sh` appends rather than truncates, creating the log on first write, so a run's events accumulate in the order they happened
- [x] A leaf name maps once to its role: `develop-red` is actor `developer` phase `red` attempt 1, `revise-green-2` is `developer`/`green`/attempt 2, `verify-refactor` is `verifier`/`refactor`
- [x] `leaf-role.sh` fails closed on a leaf name whose leading word it does not recognise: a diagnostic naming the script and the name on stderr, nothing on stdout, exit 2
- [ ] `leaf-role.sh` refuses a leaf name with a recognised leading word but no phase after it, the same fail-closed way: diagnostic on stderr, nothing on stdout, exit 2
- [ ] `supervise.sh` appends a `launch` event naming the leaf, the command it ran and the attempt number
- [ ] `supervise.sh` appends a `retry` event carrying the kill cause when a killed-stuck leaf is relaunched
- [ ] `supervise.sh` appends an `exit` event carrying its 0/1/2 status, the kill cause when there is one, and the attempt's wall seconds
- [ ] `verify.sh` appends a `verdict` event carrying the phase, `PASS`/`REJECT`/malformed and the reason's first line
- [ ] A harvester appends one `usage` event per finished leaf with wall ms, API ms, turns, the four token counts and dollars read from that leaf's closing stream-json `result` record
- [ ] The harvester appends nothing and says so on stderr when the leaf's log carries no closing `result` record, so absence is never recorded as zero
- [ ] `SKILL.md` prescribes an `event.sh` call for each conductor mark — `step-start`, `step-done`, `pin`, `revise`, `bail`, `done`, `resume` — beside the issue comment it already mirrors
