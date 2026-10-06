# Plan for #1063 — gh_pr_ready prints the ccr route's 404 JSON body on stdout outside a cloud session

- [ ] When the ccr/ready_for_review route is refused and the GraphQL-over-gh-api route readies the PR, gh_pr_ready exits 0 and its stdout carries nothing the refused ccr call printed ⟦criterion 1⟧
- [ ] When every route fails, the refused ccr route's response body (what it printed on stdout) reaches the caller on stderr and gh_pr_ready returns 2 ⟦criterion 2⟧
