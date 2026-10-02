# Plan for #663 — the refactor leaf records test-file-only candidates as owed structural debt, which the structural pass can never work

- [x] the develop-refactor prompt template defines a third candidate class: a candidate whose transform would change only files under a tests/ directory is reported on a `CANDIDATES: test-only | <transform>` line, never on a `CANDIDATES: structural` line ⟦criterion 1⟧
- [x] `refactor-owed.sh append` keeps a `CANDIDATES: test-only` candidate in the owed file under its step's heading ⟦criterion 2⟧ ⟂ refactor pending
- [ ] `refactor-owed.sh list` never prints a test-only candidate, and an owed file holding only test-only candidates makes `list` exit 3 with nothing on stdout ⟦criterion 2⟧
- [ ] `refactor-owed.sh list` on an owed file holding both structural and test-only candidates prints the structural candidates exactly as it does for a file holding them alone ⟦criterion 3⟧
- [ ] `refactor-owed.sh render` prints the test-only candidates under a heading of their own inside `## Refactor owed`, saying the structural pass does not work them ⟦criterion 4⟧
- [ ] `refactor-triage.sh` treats a `CANDIDATES: test-only | …` line as no reason to launch another refactor leaf: a report whose only candidates are test-only exits 3, and one mixing structural and test-only prints only the structural transforms ⟦criterion 5⟧
- [ ] `refactor-overflow.sh` never files a test-only candidate: an owed file whose unreached candidates are all test-only files nothing and exits 3 ⟦criterion 6⟧
- [ ] a refactor report with only `structural` and `cosmetic` candidate lines is handled by `refactor-owed.sh append`/`list`/`render`, `refactor-triage.sh` and `refactor-overflow.sh` exactly as before ⟦criterion 7⟧
