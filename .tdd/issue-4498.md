# Plan for #4498 — skill-edit-half.sh exits 2 on a leading-marker ⟦skill-edit⟧ step

- [ ] skill-edit-half.sh judges the open step's text without its `- [ ] ` prefix: on a ledger whose open step is `- [ ] ⟦skill-edit⟧ reword the prompt in `skills/tdd/SKILL.md` ⟦criterion 1⟧` it passes the kind check and starts skill-edit-step.sh for unit `skills/tdd/SKILL.md` instead of exiting 2 (a small in-process case in tests/py/unit/test_skill_edit_half.py, failing on the current code) ⟦criterion 1⟧
