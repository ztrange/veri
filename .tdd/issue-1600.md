# Plan for #1600 — unreplaced-cases.sh reports a case as unreplaced when the Red report names it in the step's own quote characters

- [x] unreplaced-cases.sh counts a REPLACES: line whose case name is wrapped in one pair of backticks, the delimiter the step uses for its names, as a replacement for that case (exit 0, case not printed) ⟦criterion 1⟧
- [x] unreplaced-cases.sh counts a REPLACES: line whose case name is wrapped in one pair of the step's own single-quote or double-quote delimiter as a replacement for that case ⟦criterion 1⟧
- [ ] unreplaced-cases.sh still counts a REPLACES: line whose case name is bare as a replacement for that case ⟦criterion 2⟧
- [ ] unreplaced-cases.sh still prints the step's case and exits 1 when the only REPLACES: line names a different case, bare or wrapped in the step's delimiter ⟦criterion 3⟧
- [ ] the Red prompt build-develop-prompt.sh builds for a ⟦replaces-case⟧ step asks for each case name in REPLACES: lines without the quote characters the step wraps it in ⟦criterion 4⟧
