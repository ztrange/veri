# Plan for #2814 — pin-recheck replays a pin recorded through a run's scratch copy of the skill

- [ ] A mutations record whose command begins with a `timed-test-run.sh` path that no longer exists is replayed through the current skill's `timed-test-run.sh`, and a pin that still catches its mutant is not reported "needs a look" ⟦criterion 1⟧
- [ ] A mutations record whose command still cannot run prints "needs a look" as today, whether or not its command begins with a `timed-test-run.sh` path that no longer exists ⟦criterion 2⟧
