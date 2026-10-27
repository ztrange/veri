# Plan for #2478 — DT2 says the test-command script prints the full-suite command; DT1 and the prose say the tier asked for

- [x] skill-edit step for the unit `skills/tdd/SKILL.md`, pin file `skills/tdd/REQUIREMENTS.md`: DT2's requirement text becomes "The script prints the one test command of that tier on stdout and exits 0.", no longer claiming the full-suite command, the SKILL.md prose itself left as it is; `skills/tdd/SKILL.md` grades PASS against its list and is re-signed in `skills/tdd/GRADED` inside this step ⟦skill-edit⟧ ⟦criterion 1⟧
- [ ] `skills/tdd/scripts/prose-owed.sh .` exits 0 on the resulting tree and `make unit` is green ⟦full-suite⟧ ⟦criterion 2⟧
- [ ] The go-red control: corrupting the re-signed `GRADED` line for `skills/tdd/SKILL.md` makes `prose-owed.sh` exit 1 and name that file ⟦human-owed⟧ ⟦criterion 3⟧
