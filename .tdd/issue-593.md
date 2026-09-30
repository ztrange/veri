# Plan for #593 — make test is red under uid 0: profile.sh's PS4 comes from the environment, and push-branch's unwritable-.tdd case relies on chmod

- [x] profile.sh prints its stamped "<secs> <suite> case <n> L<a>-<b>" lines and exits 0 for a suite whose cases cross the threshold even when the traced bash takes no PS4 from its environment (PS4 unset or overridden there), because PS4 is set inside the traced shell ⟦criterion 1⟧
- [x] push-branch.test.sh's failing-event-write case forces the failed event write by a means directory permissions play no part in (no chmod of .tdd), and still sees push-branch.sh exit 2 for both an unreachable origin and a non-fast-forward rejection ⟦criterion 2⟧
- [ ] profile.test.sh passes when run as root ⟦human-owed⟧ ⟦criterion 1⟧
- [ ] push-branch.test.sh passes when run as root, and its failing-event-write case goes red when push-branch.sh stops turning a failed event write into exit 2 — watched failing on purpose, then restored ⟦human-owed⟧ ⟦criterion 2⟧
- [ ] No other suite fails under uid 0 — a full make test run as root ⟦human-owed⟧ ⟦criterion 3⟧
- [ ] CI (Linux, non-root) stays green ⟦full-suite⟧ ⟦criterion 4⟧
