### When the ccr/ready_for_review route is refused and the GraphQL-over-gh-api route readies the PR, gh_pr_ready exits 0 and its stdout carries nothing the refused ccr call printed ⟦criterion 1⟧
- test-only | the inline `gh()` mock in case 19 of skills/tdd/scripts/tests/unit/github.test.sh repeats the mocks in cases 17–18 almost line for line (only the ccr branch differs), so it could become one shared mock helper that takes the ccr response
- test-only | case 19 sets `$calls` and `$err` but asserts on neither, so they could be dropped or asserted on
