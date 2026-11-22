# Plan for #4577 — The refactor leaf is handed its step's near-duplicate pairs and names each one it leaves

- [x] `build-develop-prompt.sh refactor` with no sixth argument renders the near-duplicates section reading `none` ⟦criterion 1⟧
- [x] `build-develop-prompt.sh refactor` given a pairs file prints each of its lines in the near-duplicates section ⟦criterion 1⟧
- [x] `build-develop-prompt.sh refactor` given an empty pairs file renders the near-duplicates section reading `none` ⟦criterion 1⟧
- [x] `build-develop-prompt.sh refactor` given an unreadable pairs file exits 2 with no stdout
- [ ] `refactor-half.sh` runs `near-duplicates.sh` on the step's own green tick and passes what it printed as the pairs file, so `.tdd/develop-refactor.prompt` carries the pair ⟦criterion 2⟧
- [ ] `near-duplicates.sh` exit 3 still launches the refactor leaf, its prompt's near-duplicates section reading `none` ⟦criterion 3⟧
- [ ] `near-duplicates.sh` exit 2 stops `refactor-half.sh` with exit 2 before any leaf is launched ⟦criterion 3⟧
- [ ] `develop-refactor.md`'s near-duplicates section tells the leaf what the pairs are and to answer each, graded against its new RE rows ⟦criterion 4⟧
- [ ] `SKILL.md`'s Refactor loop sub-step 1 builds the prompt the way `refactor-half.sh` does, graded against its new RF row ⟦criterion 5⟧
- [ ] `SCRIPTS.md`'s `build-develop-prompt.sh` and `refactor-half.sh` entries state the pairs file and the `near-duplicates.sh` call, graded against new SC rows
