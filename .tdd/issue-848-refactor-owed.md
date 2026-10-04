### Python veri/github.py with VERI_GH_DRIVER unset: gh_issue_view, gh_list and gh_json with gh args run only their REST gh api call and no GraphQL gh call; a REST failure raises NoAnswer ⟦criterion 1⟧
- replace NoRouteAdapter + FallbackAdapter with a REST-only adapter exposing list/rest_list/issue_view/issue_edit/issue_create/json directly, so "rest" is not expressed as a fallback whose first route always fails
- test-only | add REST-failure NoAnswer assertions for gh_list and gh_json-with-gh-args under VERI_GH_DRIVER unset, alongside the existing gh_issue_view one
### Bash lib/github.sh with VERI_GH_DRIVER unset: gh_issue_view, gh_list, gh_json with gh args and gh_pr_ready run only their REST gh api call and no GraphQL gh call; a REST failure returns 2 ⟦criterion 1⟧
- test-only | github.test.sh case 8 runs `grep -E "^$op gh (issue|pr) " "$calls"` twice (in the `if` test and again in the message), and could capture it once into a variable
