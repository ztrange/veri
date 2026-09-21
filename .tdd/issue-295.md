# Plan for #295 — dashboard.sh: the Metrics pane treats a bailed run like a finished one, and can silently print an empty report

- [x] a bailed run — its event log ending in a `bail` mark — reports its committed `.tdd/issue-<n>-metrics.md` verbatim on `/api/metrics`, the same as a `done` run does ⟦criterion 1⟧
- [ ] an ended run whose committed `.tdd/issue-<n>-metrics.md` is missing reports a marker a viewer can tell apart from a real empty report, never the empty string ⟦criterion 2⟧
