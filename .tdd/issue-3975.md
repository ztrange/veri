# Plan for #3975 — PRD 022.16: dispatch's overlap check reads only run PRs in this repository

- [x] `dispatch.run_prs` lists a draft `tdd/…` PR as a run PR only when its head is in this repository, requesting `isCrossRepository`: a fork draft on `tdd/9-x` changing a path #7 names prints no `skip 7 …` and #7 is launched; the same draft from this repository still skips #7 ⟦criterion 1⟧
- [x] the PR-claim ratchet no longer exempts `dispatch`
- [ ] the `dispatch.sh` entry of SCRIPTS.md says an open run draft PR is one on a `tdd/` branch of this repository ⟦criterion 2⟧
