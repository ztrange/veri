# Plan for #2547 — watch-runs.sh spends a GitHub call every 2s on an issue_state it never reads, and --max-wait overshoots by a whole poll

- [x] A watch-runs.sh poll decides which conductors are live and how one ended without any GitHub read: with gh refused, the watch still reports a conductor's exit as `exited <issue> <state>`, and no issue-state read is made during the poll; reproduced by a case that fails on the current code and passes after ⟦criterion 1⟧
- [ ] watch-runs.sh --max-wait <n> returns `timeout` (exit 3) within about a second of <n> when <n> is shorter than one poll, rather than after a whole poll's sleep — pinned by a small case driving the module's clock and sleep fakes, never a real wait ⟦criterion 2⟧
- [ ] The go-red control: with the no-gh path reverted, the first criterion's case goes red — watched red by hand and restored ⟦human-owed⟧ ⟦criterion 3⟧
