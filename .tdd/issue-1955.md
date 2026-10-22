# Plan for #1955 — report-cache.sh keeps .tdd/report-cache.json of every issue's state, blockers, wall time and lane, refreshed incrementally

- [ ] `report-cache.sh` (a new `/bin/sh` shim exec'ing `python3` on a new module `veri/report_cache.py`, its usage line in the shim's header) called with no subcommand, or with an unknown one, exits 2 with its usage on stderr ⟦criterion 5⟧
- [ ] `report-cache.sh refresh` with no cache yet, `gh` faked, writes `.tdd/report-cache.json` in the main working tree holding every issue, open and closed, each with its number, title, state, labels, `closedAt` and `updatedAt`, plus a top-level `fetched_at`, and exits 0 ⟦criterion 1⟧
- [ ] Each issue in the cache a first refresh writes carries the issue numbers listed under its body's `## Blocked by` section, an empty list when it names none ⟦criterion 1⟧
- [ ] Each issue in the cache a first refresh writes carries the wall-time seconds read from its last `### 📊 Metrics` comment (the `Wall time for the issue: <n> s` line), and a null wall time and null lane when it has no such comment ⟦criterion 1⟧
- [ ] A refresh run when `.tdd/report-cache.json` already exists asks `gh` only for the issues updated since its `fetched_at` (an `updated:>=<fetched_at>` query), merges the issues it receives into the file by number, keeps every issue it did not receive unchanged, and moves `fetched_at` forward ⟦criterion 2⟧
- [ ] A refresh whose `gh` read fails exits 2 with exactly one stderr line naming the failure and leaves `.tdd/report-cache.json` byte-identical ⟦criterion 3⟧
- [ ] A refresh whose `gh` read answers with something unparseable exits 2 with exactly one stderr line naming the failure and leaves `.tdd/report-cache.json` byte-identical ⟦criterion 3⟧
- [ ] The `### 📊 Metrics` report `metrics.sh` writes for an issue carries a `Lane: <label>` line naming the opt-in label the run ran under, `VERI_LABEL`, or `ready-for-agent` when it is unset ⟦criterion 4⟧
- [ ] A refresh reads the `Lane: <label>` line of an issue's last `### 📊 Metrics` comment into that issue's `lane` in the cache ⟦criterion 4⟧
