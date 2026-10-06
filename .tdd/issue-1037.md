# Plan for #1037 — Six suites still pass regexes through awk -v, which drops their backslashes (17 gawk warnings on CI)

- [x] prompt-test-tiers.test.sh's `numbered_item`, given a pattern containing `\.`, selects the numbered item where a literal dot stands and rejects one where an arbitrary character stands in the dot's place ⟦criterion 3⟧
- [x] skill-timeout.test.sh's `section`, given a pattern containing `\.`, starts at the line where a literal dot stands and rejects one where an arbitrary character stands in the dot's place ⟦criterion 3⟧
- [x] record-helpers.sh's `bullet`, given a pattern containing `\.`, starts at the bullet where a literal dot stands and rejects one where an arbitrary character stands in the dot's place ⟦criterion 3⟧
- [x] skill-red-untestable.test.sh's `doc_text`, given a `from` pattern containing `\.`, starts its output at the line where a literal dot stands, not at one where an arbitrary character stands in the dot's place ⟦criterion 3⟧
- [x] skill-test-command.test.sh's `at`, given a pattern containing `\.`, prints the line number of the line where a literal dot stands and rejects one where an arbitrary character stands in the dot's place ⟦criterion 3⟧
- [x] selection-order-recorded.test.sh's `entry`, given a name whose pattern carries `\.`, starts at the line where a literal dot stands and rejects one where an arbitrary character stands in the dot's place ⟦criterion 3⟧
- [x] None of the sites the issue lists (prompt-test-tiers.test.sh, skill-timeout.test.sh, record-helpers.sh, skill-red-untestable.test.sh, skill-test-command.test.sh's two, and selection-order-recorded.test.sh's own) hands a backslash-carrying value to awk through `-v`; each reads it from `ENVIRON[...]` ⟦diff-checked⟧ ⟦criterion 2⟧
- [x] no-awk-v-patterns.test.sh, run over a scratch tree holding a planted suite with `awk -v re="$1"` whose `re` is later used on the right of `~` or in `match(`, fails the run naming `<suite>:<line>` ⟦added⟧ ⟦criterion 4⟧
- [x] no-awk-v-patterns.test.sh does not flag a planted suite's comment line (`# awk -v re="$1" … $0 ~ re`) that only quotes an `awk -v` pattern site ⟦added⟧ ⟦criterion 4⟧
- [x] no-awk-v-patterns.test.sh does not flag a planted `awk -v re="$1" -f prog.awk` whose program is not single-quoted in the suite, even when a later line of that suite (holding no single quote) uses `re` on the right of `=~` ⟦added⟧ ⟦criterion 4⟧
- [x] no-awk-v-patterns.test.sh does not flag a planted `awk -v` whose variable is only compared with `==` or passed to `index(` ⟦criterion 4⟧
- [x] no-awk-v-patterns.test.sh flags a planted awk line binding two `-v` variables, `awk -v a="$x" -v re="$1" '$0 ~ re'`, whose second variable is the one used on the right of `~` ⟦added⟧ ⟦criterion 4⟧
- [x] no-awk-v-patterns.test.sh passes a flagged planted site that its exemption table lists with a reason ⟦criterion 4⟧
- [x] no-awk-v-patterns.test.sh fails the run on an exemption-table entry that carries no reason ⟦criterion 4⟧
- [x] no-awk-v-patterns.test.sh is green over the repository's own suites: every remaining `awk -v` pattern variable it flags carries an exemption with a reason naming why its value can hold no backslash ⟦criterion 4⟧ ⟂ refactor pending
- [ ] `make test` on gawk prints no `escape sequence` warning from any suite — checked by reading this PR's CI `make test` log ⟦human-owed⟧ ⟦criterion 1⟧
