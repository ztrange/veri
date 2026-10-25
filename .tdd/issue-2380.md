# Plan for #2380 — Waiting on the full-suite lock never counts toward a leaf's stuck timeout

- [ ] A supervised leaf whose full `make test` waits on a held full-suite lock for longer than `VERI_TIMEOUT` (shrunk for the test), then runs a short suite, finishes with its own exit code and is not killed stuck (a medium case driving supervise.sh over a stub leaf at the process boundary, the lock held by the test) ⟦criterion 1⟧
- [ ] A supervised leaf whose full `make test` waits silently on a held full-suite lock for longer than the `VERI_HEARTBEAT` silence window (shrunk for the test) is not killed for silence, and finishes with its own exit code (a medium case at the process boundary, the lock held by the test)
- [ ] A supervised leaf that hangs after acquiring the full-suite lock is still killed stuck once `VERI_TIMEOUT` has elapsed counted from the acquisition, not from the leaf's start (a medium case at the process boundary, the lock held by the test and then released) ⟦criterion 2⟧
