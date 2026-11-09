# Plan for #3366 — One unparseable line in a run's events.jsonl kills dispatch.sh and status.sh for every run

- [x] With two runs under .tdd/wt/<n>/, one whose .tdd/events.jsonl holds an unparseable line, status.sh exits 0 and lists the other run normally (its activity line read as usual) instead of dying with the ValueError ⟦criterion 1⟧
- [x] With the same two-run fixture, status.sh names the unreadable run and its events.jsonl file on stderr, so the bad run is reported as unreadable rather than silently skipped ⟦criterion 1⟧
- [ ] With the same two-run fixture, dispatch.sh --target N does not exit 2 for the unparseable file: it keeps its loop and its exit codes and keeps watching the other run, reporting that run's done/bail/stall line as usual ⟦criterion 2⟧
- [ ] With the same two-run fixture, dispatch.sh --target N names the unreadable run and its events.jsonl file on stderr, while its exit code stays one of 0/1/2/3 as today and is not a new code ⟦criterion 2⟧
- [ ] Guard: restoring the strict raise in status.py's run_activity and scope_totals turns both the status.sh case and the dispatch.sh case red, broken on purpose, watched red and restored ⟦human-owed⟧ ⟦criterion 3⟧
