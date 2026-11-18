# Plan for #4307 — ledger.unit_of cuts a heading unit whose heading contains backticks, so a step cannot name 4 of the graded SKILL.md sections

- [x] `ledger.unit_of` returns the whole heading unit `skills/tdd/SKILL.md#Before the Red of a `⟦suite-repair⟧` step — is the suite still red?` for a skill-edit step that names it in backticks ⟦criterion 1⟧
- [x] `ledger.unit_of` ends a backticked-heading unit at its own closing backtick when another backticked span follows it in the step
- [ ] `ledger.unit_of` still returns a heading unit whose closing backtick is followed by punctuation rather than raising ⟦added⟧
- [ ] `scope_check.skill_edit_refused` does not refuse a skill-edit step whose unit is a backticked-heading unit with a matching `### <unit>` heading in the issue's `## Requirements` ⟦criterion 2⟧
- [ ] `add_ledger_step` accepts a skill-edit step on a backticked-heading unit when the unit file exists ⟦criterion 3⟧
