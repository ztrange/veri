# Plan for #4541 — run-conductor.sh and skill-edit-step.sh refuse <reword> of a held letter-suffixed row ID (QU6b<reword>)

- [x] `requirements.malformed_row_id` returns None for a `## Requirements` table whose only row is `QU6b<reword>`, so `run-conductor.sh`'s launch check accepts the letter-suffixed amendment ⟦criterion 1⟧
- [ ] `skill-edit-step.sh` accepts an issue row `QU6b<reword>` that amends the unit's held row `QU6b`, with no exit 2 naming the ID ⟦criterion 2⟧
