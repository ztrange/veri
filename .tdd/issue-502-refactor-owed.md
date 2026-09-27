### Each per-pass row carries that pass's verify-refactor verdict, the wall seconds and the cost of that pass's refactor-phase leaves ⟦criterion 3⟧
- pass_costs_say's cost-column matcher (`"$" in c or "cost" in c`) duplicates the prelude's money() helper, but switching would also match "dollar"/"usd" headings, so it is left as is
