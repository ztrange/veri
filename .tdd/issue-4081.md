# Plan for #4081 — PRD 013.12: every run state reads off the issue's labels

- [x] a `stop` event, given VERI_STATE_LABEL_ISSUE, adds the `stopped` label ⟦criterion 1⟧
- [x] a `start` or `resume` event takes `stopped` off as it takes `bailed` off ⟦criterion 2⟧
- [x] park-issue.sh in a repository with no `parked` label exits 2, creates no label, posts no comment ⟦criterion 3⟧
- [x] ready-check.sh prints a row per state label (pr-ready, bailed, parked, stopped), failing with the create fix and exit 1 when one is missing ⟦criterion 4⟧
- [x] event.sh's header names the `stopped` label ⟦criterion 5⟧
- [ ] SCRIPTS.md's event.sh, ready-check.sh and park-issue.sh entries say it (SC29, SC46, SC77 reworded) ⟦criterion 6⟧
