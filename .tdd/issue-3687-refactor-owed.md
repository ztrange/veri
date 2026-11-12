### The graphql adapter's `issue_view(n, "comments")` returns the issue's comment bodies of every page, not its label names: two pages, the `### ⛔ Preflight refused` comment on page 2, in the answer ⟦criterion 1⟧
- `_comments` is a private method of `RestAdapter` that `GraphQLAdapter` calls through a fresh `RestAdapter()`. A module-level `_comments` function would remove that cross-class reach.
- `_comments` repeats `RestAdapter.list`'s page loop (page counter, empty-page stop, concatenation).
- `RestAdapter.issue_view` should raise `NoAnswer` for an unknown field. The `"body"` fall-through is still there.
### The REST adapter's `issue_view` with a field it does not know raises `NoAnswer` rather than returning the issue body ⟦criterion 2⟧
- GraphQLAdapter.issue_view's unknown-field case still runs `.labels[].name` instead of raising NoAnswer. This is a behaviour change, not a refactor.
applied | 4c12990d8bbe6a0c06ef103d6fd7fd6ec9b687ba | `_comments` is a private method of `RestAdapter` that `GraphQLAdapter` calls through a fresh `RestAdapter()`. A module-level `_comments` function would remove that cross-class reach.	refactor: make _comments a module-level function in github.py (#3687)
applied | 6e7cdf1b12d21f5cc489f731112510bde149923f | `_comments` repeats `RestAdapter.list`'s page loop (page counter, empty-page stop, concatenation).	refactor: share one page loop between RestAdapter.list and _comments (#3687)
applied | 5ba9726c4ea685071a73de69786f898c89734b5f | `RestAdapter.issue_view` should raise `NoAnswer` for an unknown field. The `"body"` fall-through is still there.	chore: record the structural pass's applied candidate (#3687)
