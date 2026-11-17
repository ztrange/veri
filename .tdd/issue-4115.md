# Plan for #4115 — PRD 032.1: a refactor is judged against a published smell catalogue

- [x] `skills/tdd/SMELLS.md` exists and is at most 60 lines ⟦criterion 1⟧
- [x] the prompts `build-develop-prompt.sh refactor`, `build-develop-prompt.sh structural` and `build-verify-prompt.sh refactor` render each contain the text of `skills/tdd/SMELLS.md`, whatever it says ⟦criterion 2⟧
- [x] `build-verify-prompt.sh refactor` takes the same arguments, options and environment, its usage line unchanged ⟦criterion 3⟧
- [ ] `SMELLS.md` lists each smell with a name, a numeric threshold where a diff can show one and its named refactorings, and states the transform guards and test-code rules ⟦criterion 4⟧
- [ ] `develop-refactor.md` and `develop-structural.md` tell their leaves to name the catalogue smell and refactoring on their report lines and commits, and to report `nothing left to tidy` when no catalogue smell is met ⟦criterion 5⟧
- [ ] `verify-refactor.md` judges design against the catalogue, a design REJECT naming one catalogue smell, its file and symbol ⟦criterion 6⟧
