# Plan for #3403 — dispatch queued_merges() misses running merges: after exec, ps shows queued_merge.py, not queued-merge.sh

- [x] queued_merges() returns the PR URL of a process whose ps args are `<python> <this clone's scripts>/veri/queued_merge.py <pr-url> …` (small in-process case faking the ps listing in tests/py/unit/test_dispatch.py) ⟦criterion 1⟧
- [ ] queued_merges() still returns the PR URL of a pre-exec `<this clone's scripts>/queued-merge.sh <pr-url> …` process in the same faked ps listing that also holds a post-exec queued_merge.py line ⟦criterion 2⟧
- [ ] queued_merges() ignores a process that merely names this clone's veri/queued_merge.py as a later argument, not as its script word (for example `vim <scripts>/veri/queued_merge.py <pr-url>` or `grep queued_merge.py`) ⟦criterion 3⟧
- [ ] queued_merges() omits a post-exec `<python> <other clone>/veri/queued_merge.py <pr-url> …` process whose script path is outside this clone, the same clone-path filter #3364 applies to queued-merge.sh
