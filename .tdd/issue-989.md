# Plan for #989 — refactor-owed.sh render prints a step heading with nothing under it when all its leftovers went to Test-only or Applied

- [ ] `refactor-owed.sh render` over a file whose only step holds test-only leftovers prints no `### <that step>` line, while the leftovers still appear under `### Test-only` ⟦criterion 1⟧
- [ ] `refactor-owed.sh render` over a file where one step's leftovers are all test-only and another's are structural prints the structural step's heading and bullet, and not the test-only step's heading ⟦criterion 2⟧
- [ ] `refactor-owed.sh render` over a file whose only step's every structural bullet has an `applied` line prints no `### <that step>` line, while the transforms still appear under `### Applied` ⟦criterion 3⟧
