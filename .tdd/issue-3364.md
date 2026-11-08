# Plan for #3364 — dispatch queued_merges() counts queued-merge.sh processes from any clone, including test-suite cases

- [ ] `queued_merges()` still returns the PR URL of a `queued-merge.sh` process launched from this clone's `skills/tdd/scripts/` (a small unit case under `skills/tdd/scripts/tests/py/unit/` faking only the `ps` listing; no production change expected — a pin) ⟦criterion 2⟧
- [ ] `queued_merges()` omits a `queued-merge.sh` process whose script path is outside this clone's `skills/tdd/scripts/` (a small unit case faking a `ps` listing with a foreign path such as `/private/tmp/x/queued-merge.sh https://github.com/o/r/pull/7`, failing on the current code) ⟦criterion 1⟧
