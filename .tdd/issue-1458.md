# Plan for #1458 — A merge conflict CI reports after the cost-report push has no rebase path

- [ ] SKILL.md, where it describes the `metrics:` (cost-report) push and its `wait-ci.sh` wait, gives a merge conflict CI reports there the same one-rebase path as a conflict at the first CI wait (and the `ci-conflict` bail on a second), so the run does not wait into or bail with `ci-timeout`; pinned by a prose case that goes red when that sentence is removed or reversed ⟦criterion 1⟧
