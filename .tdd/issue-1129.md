# Plan for #1129 — orchestrate.sh exits 0 without launching when the solvable answer's first line is empty

- [x] an answer whose first line is empty and whose later lines name issues launches a conductor for the first non-empty, unparked line ⟦criterion 1⟧
- [x] an empty line between a parked issue and an unparked one is skipped, not taken as the issue, so the conductor is launched for the unparked line after it ⟦criterion 2⟧
- [x] an answer whose every line is empty or parked ends the run with exit 0, launching no conductor ⟦criterion 3⟧
