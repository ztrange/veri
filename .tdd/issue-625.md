# Plan for #625 — a detached leaf ignores SIGPIPE, so ledger.sh's Broken pipe error lands in a verifier's reason file

- [x] a command launched by `detach-leaf.sh` runs with SIGPIPE at its default disposition: a writer whose reader closes early dies silently, printing no `write error: Broken pipe`, as it does outside a leaf ⟦criterion 1⟧
- [x] a non-PASS verdict's reason output carries only the verifier's reason: stderr written by anything `verify.sh` runs — `preserve_attempt` included — never reaches the reason file the conductor reads ⟦criterion 2⟧
- [x] a failure of `preserve-attempt.sh` during a non-PASS verdict is still reported where a human reads it (the verifier's stderr or the run's event log), never silenced ⟦criterion 3⟧
- [ ] the full suite is green ⟦full-suite⟧
