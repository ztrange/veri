# Plan for #4087 — PRD 016.5a: /vready reports the one-test-file runner

- [x] ready-check.sh prints `ok    one test file` when `detect-test-command.sh --tier "one test file"` exits 0 ⟦criterion 1⟧
- [ ] a `detect-test-command.sh --tier "one test file"` exit 3 fails the `one test file` row, its fix naming the `veri: one test file: <command>` CLAUDE.md line taking the test file as `"$1"`, and the check exits 1 ⟦criterion 1⟧
- [ ] an exit 2 from that call fails the row, naming exit 2 from `detect-test-command.sh --tier "one test file"` ⟦criterion 2⟧
