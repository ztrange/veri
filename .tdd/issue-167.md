# Plan for #167 — The refactor loop's touched-files list always includes the ledger

- [x] For a green commit that changed `.tdd/issue-<n>.md` and two source files, a script that prints the commit's touched files for the refactor bounds names exactly the two source files, in `git diff` order, and never the ledger
- [x] `SKILL.md` computes the refactor loop's touched-files list with that one script in both places — the cycle loop's first computation and Resume sub-step 2's recomputation from `$green` — so both give the same list and the `.tdd/` rule is stated once ⟂ refactor pending
