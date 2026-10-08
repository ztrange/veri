# Plan for #623 — gh_pr_ready prints a GraphQL 403 in every cloud run before its REST fallback succeeds

- [x] With VERI_GH_DRIVER unset (the cloud default), gh_pr_ready 42 against a gh whose `gh pr ready` fails with GraphQL's HTTP 403 readies PR 42 over the REST route, never runs `gh pr ready`, returns 0 and prints nothing on stderr
- [x] With VERI_GH_DRIVER=auto, gh_pr_ready 42 against a gh whose `gh pr ready` fails with GraphQL's HTTP 403 and whose REST ready route then succeeds returns 0 with no line of that 403 on stderr
