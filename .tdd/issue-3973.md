# Plan for #3973 — PRD 022.14: selection's claims come only from PRs in this repository

- [x] `github.Pull.cross_repository` reads `isCrossRepository` from a `gh pr list --json` record ⟦criterion 1⟧
- [ ] `github.Pull.cross_repository` reads REST `head.repo.full_name` against `base.repo.full_name`, a null head repository counting as another ⟦criterion 1⟧
- [ ] a record carrying neither shape reads as cross-repository ⟦criterion 1⟧
- [ ] `solvable_issues.select` claims only from PRs whose head is in this repository, requesting `isCrossRepository` ⟦criterion 2⟧
- [ ] `github.joined_issues` counts a merged PR's `Closes #n` only when its head is in this repository
- [ ] a ratchet: every module of veri/ reading a PR's claim decides it through `Pull.cross_repository`
- [ ] the `solvable-issues.sh` entry of SCRIPTS.md says a claim counts only from a PR in this repository ⟦criterion 3⟧
