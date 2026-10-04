# Plan for #569 — verify.sh refuses a verifier that ran make -C projects/docs test: projects/docs/.tdd/events.jsonl appears in the tree

- [x] a verifier whose run creates an untracked .tdd/ run-state file in a subdirectory of the repo (projects/docs/.tdd/events.jsonl) has its PASS verdict accepted — verify.sh exits 0 with no "modified the repository" refusal ⟦criterion 1⟧
- [x] a verifier whose run creates an untracked .tdd/ file two directories deep (a/b/.tdd/run.log) has its REJECT verdict accepted — verify.sh exits 1, not 2 ⟦criterion 1⟧
- [x] a verifier that edits the root ledger .tdd/issue-<n>.md is still refused with exit 2, the refusal naming .tdd/issue-<n>.md, even when the same run also creates an untracked subdirectory .tdd/ file ⟦criterion 2⟧
- [x] a verifier that modifies, adds or deletes a tracked file outside .tdd/ is still refused with exit 2, the refusal naming that path ⟦criterion 2⟧
- [x] in this repository the root ledger .tdd/issue-<n>.md is not ignored by git and the root blind spec .tdd/issue-<n>-spec.md is ignored ⟦criterion 3⟧
- [x] every case verify.test.sh held at the branch point keeps its assertions unchanged in the branch's diff ⟦diff-checked⟧ ⟦criterion 4⟧
- [x] every case verify.test.sh already holds passes under the repository's test command ⟦full-suite⟧ ⟦criterion 4⟧
