# Plan for #4073 — PRD 013.14: a question the judge decided once is not asked again

- [x] `skills/vjudge/SKILL.md` *The procedure* says that before judging, the judge reads the issue's comments and `.tdd/decisions.jsonl` for an earlier decision of the same question, and follows it unless a fact it rested on changed ⟦criterion 1⟧
- [x] `issue-decisions.sh <n>` prints each trusted, non-veri comment on the issue, oldest first, as `owner:` or (starting `Decided:`) `judge:`; exit 3 none, 2 no answer
