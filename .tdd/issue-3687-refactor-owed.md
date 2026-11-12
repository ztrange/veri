### The graphql adapter's `issue_view(n, "comments")` returns the issue's comment bodies of every page, not its label names: two pages, the `### ⛔ Preflight refused` comment on page 2, in the answer ⟦criterion 1⟧
- `_comments` is a private method of `RestAdapter` that `GraphQLAdapter` calls through a fresh `RestAdapter()`. A module-level `_comments` function would remove that cross-class reach.
- `_comments` repeats `RestAdapter.list`'s page loop (page counter, empty-page stop, concatenation).
- `RestAdapter.issue_view` should raise `NoAnswer` for an unknown field. The `"body"` fall-through is still there.
### The REST adapter's `issue_view` with a field it does not know raises `NoAnswer` rather than returning the issue body ⟦criterion 2⟧
- GraphQLAdapter.issue_view's unknown-field case still runs `.labels[].name` instead of raising NoAnswer. This is a behaviour change, not a refactor.
