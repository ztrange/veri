# Plan for #820 — refactor-triage and refactor-owed never take an empty structural candidate for one

- [x] refactor-triage.sh given a report whose `CANDIDATES: structural |` line has nothing after the bar exits 2, with a diagnostic on stderr and nothing on stdout ⟦criterion 1⟧ ⟂ refactor pending
- [ ] refactor-triage.sh given a report whose `CANDIDATES: structural |` line has only whitespace after the bar exits 2, with a diagnostic on stderr and nothing on stdout ⟦criterion 1⟧
- [ ] refactor-owed.sh append given a report holding a `CANDIDATES: structural |` line with nothing after the bar and another structural candidate records only the other candidate under the step's heading, with no bare `- ` bullet ⟦criterion 2⟧
- [ ] refactor-owed.sh append given a report holding a `CANDIDATES: structural |` line with only whitespace after the bar and another structural candidate records only the other candidate under the step's heading ⟦criterion 2⟧
- [ ] the suites of refactor-triage.sh and refactor-owed.sh pass, as part of the repository's full test command ⟦full-suite⟧ ⟦criterion 3⟧
- [ ] no existing assertion in refactor-triage's or refactor-owed's suites (bash or pytest) changes, except one that pinned the empty-candidate defect, changed only to the exit code, stderr or file state criterion 1 or 2 names ⟦diff-checked⟧ ⟦criterion 3⟧
