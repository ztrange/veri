# Plan for #4155 — PRD 033.1b: github-status.sh wait blocks until the GitHub incident closes

- [x] `wait <max-seconds>` whose reads find a counting incident, then none, exits 0 after the read that found none, sleeping `VERI_GITHUB_STATUS_POLL` seconds between reads ⟦criterion 1⟧
- [x] `wait` whose reads all find a counting incident until `<max-seconds>` pass exits 3, making no read after that time ⟦criterion 2⟧
- [x] `wait` whose reads all get no answer until `<max-seconds>` pass exits 2 ⟦criterion 3⟧
- [x] `wait` whose reads are counting, no answer, then none exits 0 after the third read ⟦criterion 4⟧
- [x] `wait` matches the components named after `<max-seconds>`, else the default set ⟦criterion 5⟧
- [x] `wait` with a missing or non-positive-integer `<max-seconds>` exits 2 with the usage before any read ⟦criterion 6⟧
- [x] a `VERI_GITHUB_STATUS_POLL` that is not a positive integer exits 2 naming it before any read, one-shot and `wait` ⟦criterion 7⟧
- [x] `VERI_GITHUB_STATUS_POLL` is a `TUNABLES` key, default `300`, with its row in veri/README.md's table ⟦criterion 8⟧
- [ ] the shim's `# Usage:` header and `USAGE` name the `wait <max-seconds> [<component>…]` form ⟦criterion 9⟧
- [ ] SCRIPTS.md's `github-status.sh` entry names `wait`, its poll and its exits 0, 3 and 2, graded ⟦criterion 10⟧
