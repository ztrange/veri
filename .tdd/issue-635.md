# Plan for #635 — unit-tier.test.sh stops re-running the whole fast tier: make test applies the unit guard to tests/unit/ itself

- [x] under `make test`, a suite under tests/unit/ that calls real git, python3, gh or curl fails, and the output names the command it called ⟦criterion 1⟧
- [x] under `make test`, a suite outside tests/unit/ that calls real git still passes — case 5's `run_make test TESTS=… UNIT_TESTS=` arm unchanged ⟦criterion 2⟧
- [ ] unit-tier.test.sh still checks, over the real tests/unit/ roster without running any suite, that every unit suite's header carries its `git <n>, python3 <n>, server <n>, sleep <n>` line, that no unit suite is still duplicated in tests/, and that at least 5 suites are under tests/unit/ — and a fixture tree with one header lacking that line proves the header check fails, naming the suite ⟦criterion 4⟧
- [ ] unit-tier.test.sh runs no nested `make unit` or `make test` over the real roster; every nested run names a fixture suite ⟦criterion 3⟧
- [ ] the Makefile's comment on the unit guard and CLAUDE.md's fast-tier paragraph say that `make test` applies the guard to the suites under tests/unit/ and to no other suite ⟦criterion 6⟧
- [ ] `make unit`'s own behaviour is unchanged — cases 3–5 of unit-tier.test.sh still pass ⟦full-suite⟧ ⟦criterion 5⟧
- [ ] each assertion unit-tier.test.sh keeps (rosters, count-line and reach-log, locale and stdin, the four shims, the header line) watched going red when the property it pins is broken, then restored ⟦human-owed⟧ ⟦criterion 4⟧
- [ ] a planted unit suite calling real git watched going red under `make test`, then removed ⟦human-owed⟧ ⟦criterion 1⟧
