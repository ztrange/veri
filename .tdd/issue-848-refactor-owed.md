### Python veri/github.py with VERI_GH_DRIVER unset: gh_issue_view, gh_list and gh_json with gh args run only their REST gh api call and no GraphQL gh call; a REST failure raises NoAnswer ⟦criterion 1⟧
- replace NoRouteAdapter + FallbackAdapter with a REST-only adapter exposing list/rest_list/issue_view/issue_edit/issue_create/json directly, so "rest" is not expressed as a fallback whose first route always fails
- test-only | add REST-failure NoAnswer assertions for gh_list and gh_json-with-gh-args under VERI_GH_DRIVER unset, alongside the existing gh_issue_view one
