# Plan for #3978 — PRD 021.2: `queued-merge.sh` gives up on a head that never matches

- [x] `decide`, on a mismatched head, records a `head` mark keyed by the wanted sha at the first sighting and exits 2 naming the expected and the reported sha once `VERI_CI_HEAD_WAIT` seconds have passed since it ⟦criterion 1⟧
- [x] `wait-ci.sh <pr> 540 "" <A>` against a PR reporting head B writes `.tdd/ci-head-<A>` on its first call and exits 2 naming A and B on a call made 600 s later ⟦criterion 1⟧
- [ ] a `VERI_CI_HEAD_WAIT` that is not a non-negative whole number makes `wait-ci.sh` exit 2 before any read, naming the variable ⟦criterion 2⟧
- [ ] `queued-merge.sh` whose `wait-ci.sh` exits 2 on a never-matching head exits 2 with the lock released and no merge call made ⟦criterion 3⟧
- [ ] a read finding the PR's head equal to the expected sha removes the `head` mark and waits on; a later mismatch writes a new one ⟦criterion 4⟧
- [ ] `wait-ci.sh --fresh-window <sha>` removes `.tdd/ci-head-<sha>` ⟦criterion 5⟧
- [ ] the `wait-ci.sh` and `queued-merge.sh` entries of `skills/tdd/SCRIPTS.md` state the head wait, its knob, the `--fresh-window` removal and the merge's exit 2 ⟦criterion 6⟧
