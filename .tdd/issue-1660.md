# Plan for #1660 — A REPLACES: line in a bullet, or with a bare test name, counts as unreplaced, and no prompt states the form

- [x] The Red prompt built for a `⟦replaces-case⟧` step states that the `REPLACES:` test id is the pytest node id, `<path from the repository root>::<test name>`, and that the line starts at column 0 with no bullet or other prefix ⟦criterion 1⟧ ⟂ refactor pending
- [ ] The `develop-replaces-report` correction prompt states that the `REPLACES:` test id is the pytest node id, `<path from the repository root>::<test name>`, and that the line starts at column 0 with no bullet or other prefix ⟦criterion 1⟧
- [ ] unreplaced-cases.sh counts a `REPLACES:` line carrying a `- ` markdown bullet in front exactly like the same line without it ⟦criterion 2⟧
- [ ] unreplaced-cases.sh counts a `REPLACES:` line carrying a `* ` markdown bullet in front exactly like the same line without it ⟦criterion 2⟧
- [ ] unreplaced-cases.sh counts a `REPLACES:` line whose test id is a bare test name with no `::` as replaced when exactly one test function of that name exists under `skills/tdd/scripts/tests/py/` ⟦criterion 3⟧
- [ ] unreplaced-cases.sh still counts a bare-name `REPLACES:` line as unreplaced when no test function of that name exists under `skills/tdd/scripts/tests/py/`, and the printed case says that no test of that name was found ⟦criterion 3⟧
- [ ] unreplaced-cases.sh still counts a bare-name `REPLACES:` line as unreplaced when several test functions of that name exist under `skills/tdd/scripts/tests/py/`, and the printed case says that the name is ambiguous ⟦criterion 3⟧
- [ ] unreplaced-cases.sh's exit codes are unchanged by this branch's diff: 0 when every named case is replaced, 1 naming each unreplaced case, 2 with no answer ⟦diff-checked⟧ ⟦criterion 4⟧
