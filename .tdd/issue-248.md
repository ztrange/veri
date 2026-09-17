# Plan for #248 — Metrics report's issue-wall line still says "from the first event of the log" after #229 changed the start

- [ ] On a resumed run (a log carrying a `resume` mark), the metrics report's issue-wall sentence says the wall starts at the last `resume` and no longer claims "from the first event of the log", pinned by a test in `metrics.test.sh` on the sentence's wording, not just the seconds figure
- [ ] On a run with no `resume` mark, the metrics report's issue-wall sentence describes the start as the log's first event, pinned by a test in `metrics.test.sh` on the sentence's wording
