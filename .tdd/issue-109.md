# Plan for #109 — status.sh renders every run in the repo and the scope's totals, as text or JSON

- [x] status.sh run from a repo with no `.tdd/wt/*` runs under its main working tree prints "no runs" and exits 3
- [x] status.sh lists every run under `.tdd/wt/*` with its issue number and title from the ledger heading, its branch, and step n of m from the ledger
- [x] status.sh shows each run's current phase, actor, current leaf name and elapsed seconds, and the attempts so far in the current step, read from its event log
- [x] status.sh shows each run's cost so far in dollars and tokens, summed from its event log
- [x] status.sh shows each run's state: running, done with its PR url, bailed with phase and classification, or stale when no event is newer than `VERI_TIMEOUT` and its conductor.pid does not answer `kill -0`
- [x] status.sh --scope <name> (or VERI_LABEL when no --scope) adds scope totals: issues attempted, done, bailed, total wall time and dollars
- [ ] status.sh scope totals include the count still solvable, from solvable-issues.sh for that scope, tested with VERI_GH_JSON fixtures and no network
- [ ] status.sh --json emits the same per-run and scope data as one JSON document
- [ ] status.sh --watch [seconds] redraws in place, recomputing everything from disk on every render
