# Plan for #4541 — run-conductor.sh and skill-edit-step.sh refuse <reword> of a held letter-suffixed row ID (QU6b<reword>)

- [x] `requirements.malformed_row_id` returns None for a `## Requirements` table whose only row is `QU6b<reword>`, so `run-conductor.sh`'s launch check accepts the letter-suffixed amendment ⟦criterion 1⟧
- [x] `skill-edit-step.sh` accepts an issue row `QU6b<reword>` that amends the unit's held row `QU6b`, with no exit 2 naming the ID ⟦criterion 2⟧
- [x] fix the weak-assertion case skills/tdd/scripts/tests/py/unit/test_skill_edit_step.py::test_a_step_whose_issue_row_is_a_letter_suffixed_id_reword_of_a_held_row_is_not_refused_as_a_malformed_id_4541: it asserts only exit != 2 and "QU6b" absent from stderr, never exit 0 or that the author ran; edit only that case, no production code ⟦test-quality⟧ ⟦diff-checked⟧ ⟦added⟧ ⟦criterion 2⟧
