# Plan for #4737 — stop-reason.sh reads any "limit" in a bail's text as a usage limit (run_end.py:42 substring match)

- [x] a run whose latest conductor result text mentions `rate-limit`, with no `rate_limit` error event in its last leaf log, is not classified `usage-limit` by `run_end._launch_cause` ⟦criterion 1⟧
- [ ] a run whose latest conductor result text mentions `usage limit` mid-sentence (a bail's own wording, not the harness's message, which opens the result) is not classified `usage-limit` ⟦criterion 1⟧
