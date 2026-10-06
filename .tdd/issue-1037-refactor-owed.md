### record-helpers.sh's `bullet`, given a pattern containing `\.`, starts at the bullet where a literal dot stands and rejects one where an arbitrary character stands in the dot's place ⟦criterion 3⟧
- test-only | `bullet` in record-helpers.sh: read `ENVIRON["want"]` once in a `BEGIN` block instead of on every line, to match `numbered_item` in prompt-test-tiers.test.sh (commit 3a5567507)
