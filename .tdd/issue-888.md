# Plan for #888 — gh_pr_ready's default REST route 404s on github.com, so the Draft PR step cannot ready the PR

- [x] With VERI_GH_DRIVER unset, when gh api's POST to pulls/<n>/ccr/ready_for_review fails with a 404 (github.com has no such REST route), gh_pr_ready marks the draft ready through GraphQL's markPullRequestReadyForReview mutation sent as a `gh api graphql` call carrying that PR's node id, never runs `gh pr ready`, and returns 0
- [x] With VERI_GH_DRIVER unset, when the ccr/ready_for_review POST and the `gh api graphql` markPullRequestReadyForReview fallback both fail, gh_pr_ready returns 2 and the PR is reported not readied
