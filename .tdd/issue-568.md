# Plan for #568 — veri cannot run in a Claude Code cloud session: every gh issue/pr/repo command goes through GraphQL, which the session refuses

- [x] A helper sourced from skills/tdd/scripts/lib/ marks a draft PR ready for review through the ordinary `gh pr ready` route when the `gh` on PATH answers GraphQL ⟦criterion 3⟧
- [x] With a `gh` stub that refuses every `issue`/`pr`/`repo` subcommand and `api graphql` with the GraphQL-403 message, the helper's ready-for-review marks the PR ready by calling `pulls/{n}/ccr/ready_for_review` over `gh api` ⟦criterion 3⟧
- [x] The helper's ready-for-review returns exit 2 when GitHub fails for a reason other than the GraphQL refusal (network error, 404, 5xx), on either route ⟦criterion 5⟧
- [x] capture-spec.sh prints the same spec and exit code under the GraphQL-refusing stub as it does today against a working `gh`, reading the issue over REST ⟦criterion 1⟧
- [x] solvable-issues.sh, run with no arguments under the GraphQL-refusing gh stub (which answers only `gh api` REST calls under `repos/{owner}/{repo}/`), prints the same issue numbers and exit code as it does against a working `gh` ⟦added⟧ ⟦criterion 1⟧ ⟂ refactor pending
- [ ] solvable-issues.sh --repo owner/name, run under the GraphQL-refusing gh stub, reads that named repository's issues and pull requests over REST (the stub answers only `repos/owner/name/...` paths) and prints the same issue numbers and exit code as it does against a working `gh` ⟦added⟧ ⟦criterion 1⟧
- [ ] solvable-issues.sh writes nothing to stderr under the GraphQL-refusing gh stub, the same as against a working `gh`: the GraphQL-403 refusal message is not passed through to the caller ⟦added⟧ ⟦criterion 1⟧
- [ ] workqueue.sh produces the same stdout and exit code under the GraphQL-refusing stub as it does today against a working `gh` ⟦criterion 1⟧
- [ ] tick-issue-criterion.sh ticks the issue body's criterion and exits as today under the GraphQL-refusing stub, reading and writing the body over REST ⟦criterion 1⟧
- [ ] coverage-blocker.sh files the coverage issue and records the block, with the same stdout and exit code, under the GraphQL-refusing stub ⟦criterion 1⟧
- [ ] parallel-conductors.sh produces the same stdout and exit code under the GraphQL-refusing stub as it does today against a working `gh` ⟦criterion 1⟧
- [ ] wait-ci.sh reads a PR's head sha and check state and exits 0/1/2/3 as today under the GraphQL-refusing stub ⟦criterion 1⟧
- [ ] invisible-work.sh produces the same stdout and exit code under the GraphQL-refusing stub as it does today against a working `gh` ⟦criterion 1⟧
- [ ] Each converted script still exits 2, never 1, when its REST call to GitHub fails for a reason other than the GraphQL refusal (network error, 404, 5xx) ⟦criterion 5⟧
- [ ] SKILL.md's steps that read the default branch, read or comment on the issue, and create, view, edit, ready or comment on the PR do it through the helper or `gh api`, and the `skill-*` suites pinning those steps still pass ⟦criterion 4⟧
- [ ] A suite fails naming `<file>:<line>` for any `gh issue`, `gh pr` or `gh repo` call left in skills/tdd/SKILL.md or skills/tdd/scripts/*.sh, exempting only the helper's ready-for-review route ⟦criterion 2⟧
- [ ] `make test` stays green on CI (Linux) ⟦full-suite⟧ ⟦criterion 6⟧
