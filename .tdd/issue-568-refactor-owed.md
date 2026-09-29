### The helper's ready-for-review returns exit 2 when GitHub fails for a reason other than the GraphQL refusal (network error, 404, 5xx), on either route ⟦criterion 5⟧
- merge the near-identical GraphQL-refusing `gh()` stubs of github.test.sh cases 2 and 3 into one helper (they differ in how `gh api` answers, so this needs a parameter no test requires yet)
