# Plan for #3122 — A refactor that adds or changes an assertion line of a frozen case is rejected by verify-refactor

- [x] skills/tdd/scripts/prompts/verify-refactor.md: check 4 says a refactor that adds or changes an assertion line of a case frozen at any earlier step (not only one removed or weakened) is a REJECT naming the case (VF19) ⟦skill-edit⟧ ⟦criterion 1⟧
- [ ] skills/tdd/scripts/prompts/develop-refactor.md: the prompt says a refactor may not add or change an assertion line of a frozen case of any step, while moving it into a helper unchanged modulo whitespace is allowed (RE26) ⟦skill-edit⟧ ⟦criterion 1⟧
