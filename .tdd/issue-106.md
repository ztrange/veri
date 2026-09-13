# Plan for #106 — Refactor loop runs up to 5 transforms by default and names what it left

- [x] refactor-budget.sh defaults VERI_REFACTOR_BUDGET to 5: unset, count 4 exits 0 and count 5 exits 3, an explicit value still overrides, and the status line names the budget in force
- [x] a refactor leaf's report names the candidates it still sees after applying a transform, one per line, and says none when nothing is left
- [x] the conductor's Refactor narration distinguishes nothing-left-to-tidy from stopped-by-budget and lists the N candidates the leaf left
- [x] a check fails when the default encoded in refactor-budget.sh and every prose statement of that default disagree
- [x] a triangulating test fails when the Refactor narration bullet alone stops naming the leaf's CANDIDATES: lines, even while sub-step 1 still names them
