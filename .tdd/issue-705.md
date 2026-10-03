# Plan for #705 — Four guard suites share one plant/probe harness

- [ ] A sourced library under skills/tdd/scripts/tests/lib/ defines the guard-plant harness once — making the scratch tree with the guard copy, its lib and the companions, running the guard over a document, reading the guard's failure count, and the guard-is-there, guard-is-red and green-unplanted probes, each parameterised by the guard and document the sourcing suite names — and a unit suite pins each function's outcome over a stub guard ⟦criterion 1⟧
- [ ] beyond-spec-narration-guard.test.sh sources the shared guard-plant library and no longer defines any function the library defines ⟦diff-checked⟧ ⟦criterion 1⟧
- [ ] flag-class-amendment-guard.test.sh sources the shared guard-plant library and no longer defines any function the library defines ⟦diff-checked⟧ ⟦criterion 1⟧
- [ ] verifier-launch-guard.test.sh sources the shared guard-plant library and no longer defines any function the library defines ⟦diff-checked⟧ ⟦criterion 1⟧
- [ ] docs-read-guard.test.sh sources the shared guard-plant library and no longer defines any function the library defines ⟦diff-checked⟧ ⟦criterion 1⟧
- [ ] verifier-launch-guard.test.sh's planted-run case calls probe_guard_is_red instead of repeating its own exit-status pair check (formerly :246-256) ⟦diff-checked⟧
- [ ] Across the four suites every case name, every expectation and every suite-specific probe (probe_guard_names_the_narration_case, probe_guard_names_the_routing_case and the like) is left unchanged by the branch ⟦diff-checked⟧ ⟦criterion 2⟧
- [ ] Each of the four suites was broken on purpose — its guard removed or neutralised in the planted tree — and seen red naming the case, recorded by a human ⟦human-owed⟧ ⟦criterion 3⟧
- [ ] no-nested-suites.test.sh's exemption entry for docs-read-guard.test.sh is left naming that suite with its reason, unchanged by the branch ⟦diff-checked⟧ ⟦criterion 4⟧
- [ ] make test is green ⟦full-suite⟧ ⟦criterion 5⟧
