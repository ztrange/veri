# Plan for #460 — The ## Blocked by parsing is locked inside solvable-issues.sh's Python heredoc, so a second reader has to copy it

- [x] An importable Python module under skills/tdd/scripts/lib/ returns the issue numbers a body names under `## Blocked by`, reading both the `#<n>` form and the full `https://github.com/<owner>/<name>/issues/<n>` URL of the given repository ⟦criterion 1⟧ ⟂ refactor pending
- [ ] The blocked-by module returns no blockers for a section reading `None.` and for a body with no `## Blocked by` section at all ⟦criterion 3⟧
- [ ] The blocked-by module ignores an issue URL naming another repository when a repository slug is given, and reads any github.com issue URL as local when none is ⟦criterion 3⟧
- [ ] The blocked-by module stops reading the section at the next `## ` heading, so a `#<n>` under a later heading is not a blocker ⟦criterion 3⟧
- [ ] solvable-issues.sh takes its blocker parsing from the blocked-by module rather than defining its own, with solvable-issues.test.sh passing unmodified ⟦criterion 2⟧
- [ ] A caller that is not solvable-issues.sh can import the blocked-by module and get its answers with no gh, no repository and no child process started ⟦criterion 4⟧
