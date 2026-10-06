# Plan for #1054 — gh_pr_ready prints 'gh: Not Found (HTTP 404)' on every successful ready outside a cloud session

- [x] When pulls/<n>/ccr/ready_for_review is refused with a 404 and the GraphQL-over-gh-api route then readies the PR, gh_pr_ready exits 0 and its stderr carries no HTTP 404 line ⟦criterion 1⟧ ⟂ refactor pending
- [ ] When the ccr/ready_for_review route and the GraphQL-over-gh-api route both fail, gh_pr_ready exits 2 and its stderr carries each route's own failure message ⟦criterion 2⟧
- [ ] When pulls/<n>/ccr/ready_for_review succeeds, gh_pr_ready readies the PR by that route alone, never calling the GraphQL-over-gh-api route, and exits 0 ⟦criterion 3⟧
