# Plan for #1438 — preserve-attempt.sh preserves nothing on a machine with no git identity

- [x] With no user.name/user.email in any git config, preserve-attempt.sh still writes the snapshot ref under refs/veri/attempts/<issue>/<step>/<phase>-<attempt> and exits 0 ⟦criterion 1⟧
- [x] With no user.name/user.email in any git config, preserve-attempt.sh given a mark still copies .tdd/<phase>.log and .tdd/<phase>.out under .tdd/attempts/ ⟦criterion 1⟧
