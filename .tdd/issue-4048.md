# Plan for #4048 — PRD 025.10: .gitignore says what .tdd/ commits

- [x] under the repository's .gitignore, git check-ignore reports .tdd/issue-1-pr-body.md, -spec.md, -pairs.md and .tdd/events.jsonl ignored, and .tdd/issue-1.md, -added.md, -mutations.md, -refactor-owed.md and -metrics.md not ignored ⟦criterion 2⟧
- [x] .gitignore's comment names the five committed .tdd/ kinds and says everything else under .tdd/, events.jsonl included, is run state ⟦criterion 1⟧
- [x] the 25 tracked .tdd/ files of other kinds leave the index, so git ls-files .tdd lists only the five kinds ⟦criterion 3⟧
