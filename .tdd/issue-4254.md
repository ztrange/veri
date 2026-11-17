# Plan for #4254 — a pytest leg in which no case starts or reports for a bounded window ends itself, and a TERM ends it without waiting on the hang

- [ ] a leg idle for `VERI_PYTEST_IDLE` seconds (no case starts or reports) ends its workers (TERM, KILL by pid after 5 s), prints the idle line naming the last case, removes its registry entry, releases the full-run lock and exits 2; a case reporting within the window is never ended ⟦criterion 1⟧
- [ ] an idle leg dumps its own threads' stacks and sends each worker SIGUSR1, on which a plugin the leg loads dumps the worker's stacks ⟦criterion 2⟧
- [ ] a leg sent TERM or HUP ends its workers the same way, removes its entry, releases the lock and exits 128 + the signal without xdist's worker teardown ⟦criterion 3⟧
- [ ] a `VERI_PYTEST_IDLE` that is not a whole number of at least 1 is exit 2 before any suite; the key is in `veri.tunables.TUNABLES` and the `## tunables` table ⟦criterion 4⟧
- [ ] CLAUDE.md's *Testing idiom* says how a leg ends a hang and a TERM, graded by its row ⟦criterion 5⟧
