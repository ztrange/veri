# Plan for #280 — status.sh: test gaps — JSON bail_phase field, and solvable-issues.sh's non-0/3 exit

- [x] status.sh --json reports bail_phase from the bail event's own phase, not the last launch's phase, when the two differ
- [x] status.sh renders the solvable count as ? (text `solvable ?`, JSON `"solvable": "?"`) when solvable-issues.sh exits other than 0 or 3
