# Plan for #886 — run-conductor.sh refuses to start when a parallel conductor's fetch holds the skill clone's ref lock

- [x] When run-conductor.sh's fetch of origin fails only because another process holds a ref lock in the skill clone (reproduced offline: a local bare remote as origin, plus a held `refs/remotes/origin/<branch>.lock` released while the run waits), the run is not refused — the fetch is retried and the conductor starts ⟦criterion 1⟧ ⟂ refactor pending
- [ ] A fetch of origin that fails for any other reason (an origin URL pointing at a path that is no remote) is still refused with exit 2 and the existing `fetch of origin failed` message, without waiting out the lock retries ⟦criterion 2⟧
- [ ] The branch adds a case under skills/tdd/scripts/tests/ that reproduces the concurrent ref-lock case without the network — a local bare remote plus a held lock or competing ref update — and touches no other suite's existing cases ⟦diff-checked⟧ ⟦criterion 3⟧
- [ ] make test is green ⟦full-suite⟧ ⟦criterion 4⟧
