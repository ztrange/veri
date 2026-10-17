# Plan for #1527 — A test-only issue is not routed to ⟦diff-checked⟧ steps, and a refactor plan may hold test-only or ⟦phases⟧ steps

- [x] SKILL.md states that an issue whose work changes only tests is not refactor-kind and is planned as ⟦diff-checked⟧ steps, pinned by a prose case reading SKILL.md ⟦criterion 1⟧
- [x] The rendered plan prompt for a spec carrying a ## Refactor section tells the verifier to REJECT a refactor-kind plan that holds a ⟦phases: …⟧ step ⟦criterion 2⟧
- [ ] The rendered plan prompt for a spec carrying a ## Refactor section tells the verifier to REJECT a refactor-kind plan that holds a step that only edits tests ⟦criterion 3⟧
