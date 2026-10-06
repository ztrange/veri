# Plan for #1037 — Six suites still pass regexes through awk -v, which drops their backslashes (17 gawk warnings on CI)

- [ ] prompt-test-tiers.test.sh's `numbered_item`, given a pattern containing `\.`, selects the numbered item where a literal dot stands and rejects one where an arbitrary character stands in the dot's place ⟦criterion 3⟧
- [ ] skill-timeout.test.sh's `section`, given a pattern containing `\.`, starts at the line where a literal dot stands and rejects one where an arbitrary character stands in the dot's place ⟦criterion 3⟧
- [ ] record-helpers.sh's `bullet`, given a pattern containing `\.`, starts at the bullet where a literal dot stands and rejects one where an arbitrary character stands in the dot's place ⟦criterion 3⟧
- [ ] skill-red-untestable.test.sh's `doc_text`, given a `from` pattern containing `\.`, starts its output at the line where a literal dot stands, not at one where an arbitrary character stands in the dot's place ⟦criterion 3⟧
- [ ] skill-test-command.test.sh's `at`, given a pattern containing `\.`, prints the line number of the line where a literal dot stands and rejects one where an arbitrary character stands in the dot's place ⟦criterion 3⟧
- [ ] None of the sites the issue lists (prompt-test-tiers.test.sh, skill-timeout.test.sh, record-helpers.sh, skill-red-untestable.test.sh, skill-test-command.test.sh's two, and selection-order-recorded.test.sh's own) hands a backslash-carrying value to awk through `-v`; each reads it from `ENVIRON[...]` ⟦diff-checked⟧ ⟦criterion 2⟧
- [ ] no-awk-v-patterns.test.sh, run over a scratch tree holding a planted suite with `awk -v re="$1"` whose `re` is later used on the right of `~` or in `match(`, fails naming `<suite>:<line>`; a planted `awk -v` whose variable is only compared with `==` or `index(` is not flagged ⟦criterion 4⟧
- [ ] no-awk-v-patterns.test.sh honours an exemption table: a flagged site listed there with a reason passes, and an entry with no reason fails the run ⟦criterion 4⟧
- [ ] no-awk-v-patterns.test.sh is green over the repository's own suites: every remaining `awk -v` pattern variable it flags is moved to `ENVIRON[...]` or carries an exemption with a reason ⟦criterion 4⟧
- [ ] `make test` on gawk prints no `escape sequence` warning from any suite — checked by reading this PR's CI `make test` log ⟦human-owed⟧ ⟦criterion 1⟧
