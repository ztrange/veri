# Plan for #191 — A run's commits live on one disk until the draft PR

- [x] A push that fails leaves the run's exit status, ledger and commits unchanged, and records an event saying the push failed
- [x] After a step's green commit and tick, the branch exists on the remote at that commit
- [ ] The draft PR step opens the PR against the already-pushed branch without requiring a first push
- [ ] A branch pushed by a step, with no open PR, does not make its issue read as claimed
