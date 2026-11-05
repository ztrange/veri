# Plan for #3113 — A suite-repair step whose repair is test-only finishes without a red bar

- [x] `suite-red-resume.sh test-only <base-sha> <alone-cmd> <suite>…` exits 0 when the working tree differs from `<base-sha>` in test files only (the `case_reader.is_test_path` rule) and every named suite passes when run alone with `<alone-cmd>` ⟦criterion 1⟧
- [x] `suite-red-resume.sh test-only` exits 1, naming the suite on stderr, when a named suite is still red when run alone with `<alone-cmd>`, though the diff touches test files only ⟦criterion 1⟧
- [x] `suite-red-resume.sh test-only` exits 1, naming the case on stderr, when the diff from `<base-sha>` deletes a test case that `<base-sha>` holds, though the diff touches test files only and the named suites pass ⟦criterion 1⟧
- [x] `suite-red-resume.sh test-only` exits 1, naming the case on stderr, when the diff from `<base-sha>` removes an assertion line from a case it keeps, though the diff touches test files only and the named suites pass ⟦criterion 1⟧
- [ ] `suite-red-resume.sh test-only` exits 1, naming the production file on stderr, when the diff from `<base-sha>` touches a production file (one `case_reader.is_test_path` does not count as a test file), whatever the named suites do ⟦criterion 2⟧
- [ ] `suite-red-resume.sh` with no arguments prints a usage line naming the `test-only <base-sha> <alone-cmd> <suite>…` verb beside the others on stderr and exits 2
- [ ] skills/tdd/SKILL.md: a `⟦suite-repair⟧` step's Red leaf is followed, before verify-red, by `suite-red-resume.sh test-only` on the step base sha and the suites the step names; exit 0 ticks the step without `--refactor-pending` and commits it with a `test:` subject, with no verify-red, no revise leaf and no `revise-impossible` bail; exit 1 takes the ordinary Red, verify-red and revise path unchanged (CY135) ⟦skill-edit⟧ ⟦criterion 1⟧
- [ ] skills/tdd/SCRIPTS.md: the `suite-red-resume.sh` entry catalogues the `test-only` verb, its arguments and its exit codes ⟦skill-edit⟧
- [ ] Go-red control: with the test-only completion removed, the first criterion's case fails ⟦human-owed⟧ ⟦criterion 3⟧
