# Plan for #3687 — gh_issue_view(n, "comments") returns the issue body, so release-issue.sh never releases a preflight-refused claim

- [x] `release-issue.sh` on an issue labelled only `taken:<lane>` whose comment starts `### ⛔ Preflight refused`, driven through the real REST adapter of `github.py` with only the gh process boundary faked by a fixture (the issue's labels, and its comments at `issues/<n>/comments`), exits 0 and swaps `taken:<lane>` for the opt-in label (fails on current code with exit 3; a small case, no real process) ⟦criterion 3⟧
- [x] The REST adapter's `issue_view(n, "comments")` returns the comment bodies of every page of `issues/<n>/comments`: a fixture of two pages with the `### ⛔ Preflight refused` comment on page 2 has that comment's body in the answer ⟦criterion 1⟧
- [x] The graphql adapter's `issue_view(n, "comments")` returns the issue's comment bodies of every page, not its label names: two pages, the `### ⛔ Preflight refused` comment on page 2, in the answer ⟦criterion 1⟧ ⟂ refactor pending
- [ ] The REST adapter's `issue_view` with a field it does not know raises `NoAnswer` rather than returning the issue body ⟦criterion 2⟧
- [ ] The graphql adapter's `issue_view` with a field it does not know raises `NoAnswer` rather than returning the label names ⟦criterion 2⟧
