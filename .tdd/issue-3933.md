# Plan for #3933 — PRD 018.6: comment.sh posts a switched-off verify-refactor as SKIPPED, not PASS

- [x] `comment.sh <n> verify-refactor` posts `### 🔎 verify-refactor — SKIPPED (switched off)` and appends a `comment` event with `kind=verify-refactor` when `.tdd/verdict-refactor.exit` reads `skipped` ⟦criterion 1⟧
- [x] skill-edit step for the unit `skills/tdd/SKILL.md`: add CY147 under `## skills/tdd/SKILL.md`, amend the Refactor loop's step 5 **Switched off** to name `$S/comment.sh <n> verify-refactor`, grade and sign ⟦skill-edit⟧ ⟦criterion 3⟧
- [x] skill-edit step for the unit `skills/tdd/SCRIPTS.md`: add SC142 under `## skills/tdd/SCRIPTS.md`, amend the `$S/comment.sh` entry, grade and sign ⟦skill-edit⟧ ⟦criterion 4⟧
