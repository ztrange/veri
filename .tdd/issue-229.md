# Plan for #229 — The metrics report's outcome and issue wall read the first ending mark, so a resumed run is described by the run it resumed

- [x] A log carrying a `bail` mark followed by a `resume` and a `done` reports the run as landed, naming the PR, not as bailed.
- [x] On a log carrying a `bail`, then a `resume`, then a `done`, the issue wall runs from the last `resume` to the `done` mark, not from the log's first event.
- [ ] A log with no `resume` is unchanged: the wall still runs from its first event, and its single ending mark still decides the outcome.
- [ ] Counts, times and costs stay accumulated across every run in the log — only the outcome and the wall are scoped to the last run.
