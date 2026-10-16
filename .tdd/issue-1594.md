# Plan for #1594 — mutation-parity.sh can never prove a row whose old bash suite holds a single case

- [ ] A row whose old suite holds exactly one case reads `proven` when, under the mutation, that suite runs to its count line (`0 passed, 1 failed`) with the named case failed and the replacement is caught ⟦criterion 1⟧
- [ ] A row whose old suite holds exactly one case reads `owed` when, under the mutation, that suite dies before its count line, instead of mutation-parity.sh stopping with no row ⟦criterion 1⟧
- [ ] A row whose old suite holds exactly one case reads `unproven` when, under the mutation, that suite runs to its count line with the named case failed but the replacement is not caught ⟦criterion 1⟧
- [ ] Regression pin, no production change (the behaviour already holds, so this step's test passes against the unmodified code and takes the pin path): a row whose old suite holds more than one case is judged as before the change: `proven` only when the named case fails, at least one other case passes and the replacement is caught, and `owed` when the mutation fails every case of that multi-case suite ⟦criterion 1⟧
