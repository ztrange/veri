# Plan for #4090 — PRD 016.6b: /vready proves a push is accepted, without pushing

- [x] the `push dry-run` row is `ok` when `git push --dry-run origin HEAD:refs/heads/veri-permission-probe-<random>` exits 0 ⟦criterion 1⟧
- [x] a refused dry run fails the row, carrying git's last non-empty stderr line ⟦criterion 1⟧
- [x] the push runs with `GIT_TERMINAL_PROMPT=0` in its environment ⟦criterion 3⟧
- [x] every push the check makes is a dry run to a fresh `veri-permission-probe-*` name, and it makes only git calls, so `origin` gains no probe branch ⟦criterion 2⟧ ⟦criterion 4⟧
- [x] ready-check.sh prints the `push dry-run` row ⟦criterion 1⟧
