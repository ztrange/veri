# Plan for #1600 — unreplaced-cases.sh reports a case as unreplaced when the Red report names it in the step's own quote characters

- [x] unreplaced-cases.sh counts a REPLACES: line whose case name is wrapped in one pair of backticks, the delimiter the step uses for its names, as a replacement for that case (exit 0, case not printed) ⟦criterion 1⟧
- [x] unreplaced-cases.sh counts a REPLACES: line whose case name is wrapped in one pair of the step's own single-quote or double-quote delimiter as a replacement for that case ⟦criterion 1⟧
- [x] unreplaced-cases.sh still counts a REPLACES: line whose case name is bare as a replacement for that case ⟦criterion 2⟧
- [x] unreplaced-cases.sh still prints the step's case and exits 1 when the only REPLACES: line names a different case, bare or wrapped in the step's delimiter ⟦criterion 3⟧
- [x] the Red prompt build-develop-prompt.sh builds for a ⟦replaces-case⟧ step asks for each case name in REPLACES: lines without the quote characters the step wraps it in ⟦criterion 4⟧
- [x] unreplaced-cases.sh reads a REPLACES: line whose case name is wrapped in a quote character other than the step's own delimiter as that wrapped text: for a backtick-delimited step naming case a, REPLACES: 'a' => <id> and REPLACES: "a" => <id> each leave a printed as unreplaced, exit 1 ⟦criterion 5⟧
- [ ] unreplaced-cases.sh counts one REPLACES: line for one named case only: for a backtick-delimited step naming both 'a' and a, the single line REPLACES: 'a' => <id> leaves a printed as unreplaced, exit 1 ⟦criterion 6⟧
- [ ] unreplaced-cases.sh counts a REPLACES: line whose case name is wrapped in one pair of ' as a replacement for that case when the step delimits its names with ' ⟦criterion 7⟧
