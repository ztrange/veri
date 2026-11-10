# Plan for #3554 — make test TESTS= with a serial case ends on the serial pass's "N deselected" line, so a subset run reads as most cases dropped

- [ ] After a pytest leg run that collects at least one `serial` case (so both the not-serial and the serial pass run), the leg's output ends with one combined line giving the cases run and passed across both passes, not the serial pass's `N deselected` line alone ⟦criterion 1⟧
- [ ] A `--subset` pytest leg run whose named files hold cases that neither pass selected (a `-m` mark expression excluding a named case from both the not-serial and the serial pass) exits non-zero, naming the count of unselected cases on its output ⟦criterion 2⟧
- [ ] A `make test TESTS=` subset run selects every case in the named files, `process`, `tree_audit` and `serial` marked cases included: the leg is handed no mark expression that deselects them
- [ ] The guard, broken on purpose (the combined line or the unselected-case check removed), goes red ⟦human-owed⟧ ⟦criterion 3⟧
