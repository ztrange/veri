# Plan for #4316 — PRD 037.1: verify-cover-new.md has rows and a grade

- [x] `skills/tdd/scripts/prompts/verify-cover-new.md` gets its `## skills/tdd/scripts/prompts/verify-cover-new.md` section in `skills/tdd/scripts/prompts/REQUIREMENTS.md` with rows VN1-VN11 from the issue's `## Requirements`, mirroring the template's current text as is (no wording change), graded PASS by `grade-prose.sh` ⟦skill-edit⟧ ⟦criterion 1⟧
- [x] `skills/tdd/GRADED` holds a line for `skills/tdd/scripts/prompts/verify-cover-new.md`, added by the branch only through the skill-edit step's `grade-prose.sh` PASS and no other `GRADED` line changed ⟦diff-checked⟧ ⟦criterion 2⟧
- [x] the branch's diff leaves `skills/tdd/scripts/prompts/verify-cover-new.md` unchanged: `git diff <base>..HEAD -- skills/tdd/scripts/prompts/verify-cover-new.md` is empty ⟦diff-checked⟧ ⟦criterion 3⟧
- [ ] `prose-owed.sh` exits 0 on the branch, as run by the full suite ⟦full-suite⟧ ⟦criterion 3⟧
