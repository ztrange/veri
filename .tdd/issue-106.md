# Plan for #106 — Refactor loop runs up to 5 transforms by default and names what it left

- [ ] refactor-budget.sh defaults VERI_REFACTOR_BUDGET to 5: unset, count 4 exits 0 and count 5 exits 3, an explicit value still overrides, and the status line names the budget in force
- [ ] a refactor leaf's report names the candidates it still sees after applying a transform, one per line, and says none when nothing is left
- [ ] the conductor's Refactor narration distinguishes nothing-left-to-tidy from stopped-by-budget and lists the N candidates the leaf left
- [ ] a check fails when the default encoded in refactor-budget.sh and every prose statement of that default disagree
