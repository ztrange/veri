# Plan for #1717 — PRD 011 S1: requirements.sh reads a prose unit's requirements list and never emits its Why column

- [x] `requirements.sh units <file>` prints each prose unit the file declares — every `## <path>` or `## <path>#<section heading>` heading over an `ID | Requirement | Why` table — one per line, in file order; the new script under skills/tdd/scripts/ also gets, in this same step, a usage line on stderr with exit 2 when called with no arguments, and a declared caller ⟦criterion 1⟧
- [x] `requirements.sh claims <file> <unit>` prints that unit's rows as `<ID><TAB><Requirement>` in table order, and no text from any of its `Why` cells appears in the output ⟦criterion 2⟧
- [x] `claims` on a unit whose table repeats an ID exits 2, prints nothing on stdout, and names the line number of the duplicate row on stderr ⟦criterion 3⟧
- [x] `claims` on a unit whose table has a row with an empty `Requirement` cell exits 2, prints nothing on stdout, and names that row's line number on stderr ⟦criterion 3⟧
- [x] `claims` on a unit whose table has a row with an empty `ID` cell exits 2, prints nothing on stdout, and names that row's line number on stderr ⟦criterion 3⟧
- [x] `claims` on a unit whose table header lacks one of the `ID`, `Requirement`, `Why` columns exits 2, prints nothing on stdout, and names the header's line number on stderr ⟦criterion 3⟧
- [x] `claims` given a file that does not exist exits 2 and says on stderr that the file is missing, naming it ⟦criterion 4⟧
- [x] `claims` given a unit the file does not declare exits 2 and says on stderr that the unit is not declared, naming it ⟦criterion 4⟧ ⟂ refactor pending
