# Plan for #946 — commit-suffix guard misses a prompt that asks for a commit in words outside its closed list

- [x] commit_suffix_offenders reports a planted develop-*.md saying "Commit these changes." with no (#<issue>) ⟦criterion 1⟧
- [ ] commit_suffix_offenders reports a planted develop-*.md saying "commit them" with no (#<issue>) ⟦added⟧ ⟦criterion 1⟧
- [ ] commit_suffix_offenders reports a planted develop-*.md saying "make a commit" with no (#<issue>) ⟦criterion 1⟧
- [ ] commit_suffix_offenders does not report a planted develop-*.md that only mentions "the step's green commit" without asking for a commit ⟦criterion 2⟧
- [ ] every shipped prompts/develop-*.md still passes commit_suffix_offenders ⟦criterion 3⟧
