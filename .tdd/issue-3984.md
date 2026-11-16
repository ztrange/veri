# Plan for #3984 — PRD 021.15: `queued-merge.sh`'s network calls end after a bound

- [x] a VERI_GIT_NETWORK_TIMEOUT that is not a whole number of at least 1 makes queued-merge.sh exit 2 naming it before the lock is taken; the name is a TUNABLES entry, default 600 ⟦criterion 3⟧
- [ ] the gated fetch origin, faked to never return, ends after VERI_GIT_NETWORK_TIMEOUT seconds: exit 2, stderr naming the call and the limit, the lock released as a failed fetch leaves it ⟦criterion 1⟧
- [ ] the leased push, faked to never return, ends after VERI_GIT_NETWORK_TIMEOUT seconds: exit 2, stderr naming the call and the limit, the lock kept as a refused push leaves it ⟦criterion 1⟧
- [ ] the tag push, faked to never return, ends after VERI_GIT_NETWORK_TIMEOUT seconds and is handled as a failed tag push: exit 2 naming tag, stderr naming the call and the limit, the lock released after cleanup ⟦criterion 1⟧
- [ ] push origin --delete, faked to never return, ends after VERI_GIT_NETWORK_TIMEOUT seconds and is handled as a failed branch delete: exit 2, stderr naming the call and the limit, the lock released after cleanup ⟦criterion 1⟧
- [ ] the merge call, faked to never return after landing, ends after VERI_GH_TIMEOUT seconds and the settle window, holding the lock, reads the PR merged ⟦criterion 2⟧
- [ ] the queued-merge.sh entry of SCRIPTS.md states both bounds and how a timed-out call is handled (SC160) ⟦criterion 4⟧
