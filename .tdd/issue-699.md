# Plan for #699 — no-job-spec-kills keys its exemptions by the exempted line's text, not its number

- [x] An EXEMPT entry in no-job-spec-kills.test.sh names its site by file and the exempted line's text, not its number (the two real skill-leaf-env.test.sh entries included), so lines inserted above an exempted line leave both cases green ⟦criterion 1⟧
- [x] Editing an exempted line's text turns "every exemption names a line under skills/ that ends a background process by a job spec" red, naming the entry ⟦criterion 2⟧
- [x] A line that kills by a job spec with no exemption matching its text still turns "no file under skills/ ends a background process by a job spec" red, naming `<file>:<line>` ⟦criterion 2⟧
- [x] An EXEMPT entry whose text matches more than one line of its file fails the run, naming each matching line, so one entry never silently excuses a second site ⟦criterion 3⟧
- [x] An EXEMPT entry with an empty reason still fails the run under the text key ⟦criterion 4⟧
- [ ] fix the full-suite failure: job-spec-guard.test.sh — FAIL - no-job-spec-kills.test.sh names a file under skills/ that kills a background process by a job spec as <file>:<line>, leaves a kill by recorded pid alone, and honours an exemption entry only when it carries a reason (its planted [file:line] exemption key is no longer honoured, and the new cases fail in its scratch tree); no-nested-suites.test.sh — FAIL - no suite under skills/tdd/scripts/tests/ (or its unit/ tier) launches another real suite outside the exemptions recorded here (no-job-spec-kills.test.sh names skill-leaf-env.test.sh outside a comment) ⟦suite-repair⟧ ⟦criterion 4⟧
- [ ] Each failure path above was broken on purpose and seen red ⟦human-owed⟧ ⟦criterion 5⟧
- [ ] make test is green ⟦full-suite⟧ ⟦criterion 6⟧
