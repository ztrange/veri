# Plan for #4086 — PRD 016.8: /vinstall records the one-test-file runner

- [x] record-test-commands.sh --one-file <cmd> puts a veri: one test file: <cmd> line in the same commit, and on it detect-test-command.sh --tier "one test file" prints <cmd> exactly ⟦criterion 1⟧
- [x] an existing veri: one test file: line is replaced where it stands, never duplicated, every other line unchanged ⟦criterion 2⟧
- [x] without --one-file the commit adds no veri: one test file: line and leaves an existing one unchanged ⟦criterion 3⟧
- [x] with --one-file, exit 3 holds only when the tip also declares veri: one test file: with exactly <cmd>; otherwise the branch and PR are made ⟦criterion 4⟧
- [ ] an empty --one-file argument is exit 2 with nothing written ⟦criterion 5⟧
- [ ] skills/vinstall/SKILL.md asks for the one-file command, proposes none, passes it with --one-file, records the tier lines alone without an answer, asks only for it when both tier lines exist (VI10, VI11), graded with VI6–VI9; the recorded form round-trips through detect-test-command.sh and tick-ledger.sh --already-holds --case in a real run ⟦criterion 6⟧
