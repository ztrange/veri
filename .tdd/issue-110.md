# Plan for #110 — Local web dashboard, part 1: dashboard.sh serving the Runs, Metrics and Events panes

- [x] dashboard.sh starts a stdlib-only Python server on default port 8765 serving the one HTML page at / and exits 0 when sent SIGINT ⟦criterion 1⟧
- [x] dashboard.sh binds the port given as its argument, and binds 127.0.0.1 only — never another interface ⟦criterion 1⟧
- [x] The Runs endpoint returns what status.sh --json returns ⟦criterion 2⟧ ⟂ refactor pending
- [ ] The Metrics endpoint returns the per-issue table, recomputed from the event log for a running run and read from the committed report for a finished one ⟦criterion 2⟧
- [ ] The Events endpoint returns the selected run's events.jsonl tail, newest last ⟦criterion 2⟧
- [ ] The served page's Runs, Metrics and Events panes each poll their own JSON endpoint every 2 seconds ⟦criterion 1⟧
- [ ] make test runs a dashboard suite that starts the server on a spare port against fabricated run fixtures and asserts each endpoint's JSON ⟦criterion 3⟧
