# Plan for #2072 — A skill-edit step grades a new, empty unit before its author runs, and the grader returns no verdict

- [x] On a unit that is 0 bytes, skill-edit-step.sh launches the author leaf before any grader call: a stub CLAUDE_BIN that records every invocation by role (grader vs author) records the author first and the grader zero times before it (a medium case with a real process, in skills/tdd/scripts/tests/py/test_skill_edit_step_process.py) ⟦criterion 2⟧
- [ ] On a unit that is 0 bytes, when the first author attempt writes a gradable unit the grader then passes, skill-edit-step.sh exits 0 (not 2) and commits the authored unit ⟦criterion 1⟧
- [ ] On a unit that does not exist and is created by the step from a `### <unit> (new)` requirements heading, skill-edit-step.sh launches the author leaf before any grader call and exits 0 (not 2) when the author writes a gradable unit the grader passes ⟦criterion 1⟧
- [ ] On a non-empty existing unit, skill-edit-step.sh still calls the grader before any author leaf, and exits 3 without launching an author when the grader passes every requirement ⟦criterion 3⟧
