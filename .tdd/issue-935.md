# Plan for #935 — transform, structural and diff leaves commit without the (#<n>) suffix: only develop-refactor.md states it

- [x] The prompt `build-develop-prompt.sh transform …` prints tells the leaf to give its commit a subject ending in `(#<issue>)`, the convention develop-refactor.md states ⟦criterion 1⟧
- [x] The prompt `build-develop-prompt.sh structural …` prints tells the leaf to give its commit a subject ending in `(#<issue>)` ⟦criterion 2⟧
- [x] The prompt `build-develop-prompt.sh diff …` prints tells the leaf to give its commit a subject ending in `(#<issue>)` ⟦criterion 2⟧
- [x] The prompt `build-develop-prompt.sh revise diff …` prints tells the leaf to give its commit a subject ending in `(#<issue>)` ⟦criterion 2⟧
- [x] A check over every `skills/tdd/scripts/prompts/develop-*.md` that tells the leaf to commit fails, naming the file, when a planted prompt asks for a commit without stating the `(#<issue>)` convention ⟦criterion 3⟧
- [x] That same check stays green over a planted prompt that makes no commit (its only instruction is "make no commit"), and over the real prompts directory ⟦criterion 3⟧
- [ ] develop-refactor.md's existing wording, and every case the prompt suites already hold, are unchanged by the branch ⟦diff-checked⟧ ⟦criterion 4⟧
