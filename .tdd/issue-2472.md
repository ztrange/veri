# Plan for #2472 — skill-edit-step.sh reads --change as the issue-body file when --added comes first

- [x] skill_edit_step.main given --added "<step>" before --change "<change>" and then the issue-body and unit files applies both flags exactly as the --change-first order does, never reading the literal --change as the issue-body file (a case in tests/py/unit/test_skill_edit_step.py, red on today's code) ⟦criterion 1⟧ ⟂ refactor pending
- [ ] skill_edit_step's USAGE string names --change beside --added, and the usage refusal main prints on a bad argument list (fewer than two positional files) shows --change ⟦criterion 2⟧
- [ ] go-red control: a mutation reverting only the flag-parse change turns the new --added-first case red while an existing --change-first case stays green, recorded by a human ⟦human-owed⟧ ⟦criterion 3⟧
