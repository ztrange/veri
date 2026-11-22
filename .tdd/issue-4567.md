# Plan for #4567 — vish requires each criterion's test watched red, and each added guard mutated, before the PR is readied

- [x] `## Closing the change` requires, per acceptance criterion and before the PR is readied, a product-code break, the criterion's test watched red, and the code restored (VSH28) ⟦criterion 1⟧
- [x] `## Closing the change` requires each added guard, exit-code and delete path mutated, and a test for every surviving mutant (VSH29) ⟦criterion 2⟧
- [x] `## Closing the change` requires the PR body to list, per criterion, the test and that it was watched red (VSH30) ⟦criterion 3⟧
