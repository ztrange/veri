# Plan for #3877 — dispatch queued_merges() counts queued merges of other target repos

- [x] queued_merges() omits this clone's queued-merge.sh running for a PR in another owner/repo than the dispatch's target repo ⟦criterion 1⟧
- [ ] queued_merges() omits this clone's post-exec veri/queued_merge.py running for a PR in another owner/repo ⟦criterion 2⟧
- [ ] queued_merges() still counts a target-repo PR whose URL spells the owner/repo in another letter case than origin's remote
