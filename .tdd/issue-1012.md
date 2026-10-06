# Plan for #1012 — run-conductor.sh still refuses a launch when another conductor holds the skill clone's ref lock for more than ~5 s

- [ ] A ref lock on the skill clone held by another process past today's 5 × VERI_FETCH_RETRY_SLEEP window (still locked after the fifth fetch) but released within the new bound lets run-conductor.sh's launch proceed, pinned offline with VERI_FETCH_RETRY_SLEEP=0 so no real-clock wait is taken ⟦criterion 1⟧
- [ ] A ref lock on the skill clone that is never released makes run-conductor.sh refuse with exit 2 once the new retry bound is reached, launching no conductor, with stderr naming the ref lock ⟦criterion 2⟧
- [ ] A fetch of origin that fails for any reason other than `cannot lock ref` is still refused at once by run-conductor.sh with exit 2 after a single fetch, without waiting for any retry ⟦criterion 3⟧
- [ ] SKILL.md's *Launching the conductor* paragraph on the ref-lock retry states the new bound in place of "retried up to 5 times" ⟦diff-checked⟧
