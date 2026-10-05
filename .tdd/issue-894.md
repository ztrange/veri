# Plan for #894 — wait-ci.sh's deadline for a head starts while the PR is still a draft, so the post-ready wait times out on CI that never ran

- [x] wait-ci.sh called on a draft PR whose checks are pending records no .tdd/ci-deadline-<sha> file and exits 3 when its slice runs out ⟦criterion 1⟧
- [x] after a draft call left no deadline, a call on the same PR once it is ready with the same head sha records the deadline counted from that call, and checks turning green within it exit 0 ⟦criterion 2⟧
- [ ] a ready PR whose checks stay pending past a deadline already recorded for its head still exits 2 ⟦criterion 3⟧
