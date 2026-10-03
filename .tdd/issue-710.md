# Plan for #710 — the unit-tier python3 guard lets a shim's hand-off to a veri/ module through, and refuses every other python3 call

- [x] under `make unit`'s guard PATH, a `/bin/sh` shim that `exec`s `python3` on a module file under `skills/tdd/scripts/veri/` runs that module through the real interpreter and answers with the module's own stdout, stderr and exit code ⟦added⟧ ⟦criterion 1⟧
- [x] under `make unit`'s guard PATH, that shim's hand-off still reaches the real interpreter when one or more PATH directories after the guard and before the real `python3` hold no `python3`, answering with the module's own stdout, stderr and exit code ⟦added⟧ ⟦criterion 1⟧
- [x] under `make unit`'s guard PATH, a direct `python3` call — `python3 -c …`, `python3` on a file outside `skills/tdd/scripts/veri/`, and `python3` with no arguments — still exits 1, its stderr naming `python3` as today, and is written to `$UNIT_GUARD_LOG` ⟦criterion 2⟧
- [x] when the guard cannot resolve a `veri/` directory beside it, every `python3` call — a file included — is refused with exit 1, naming `python3`, and logged to `$UNIT_GUARD_LOG`; none reaches the real interpreter ⟦added⟧ ⟦criterion 2⟧
- [ ] under `make test`, a suite under `tests/unit/` gets the same guard: a shim's hand-off to a `skills/tdd/scripts/veri/` module goes through and a direct `python3` call is refused, named and logged, while a suite outside `tests/unit/` gets no guard ⟦criterion 3⟧
- [ ] the `git` guard is unchanged: any `git` call from a unit-tier suite, including one whose first argument is a file under `skills/tdd/scripts/veri/`, still exits 1 naming `git` and is logged to `$UNIT_GUARD_LOG`
- [ ] a planted unit-tier suite calling `python3 -c` directly is watched go red under the changed guard, then removed, and the run is recorded in the PR body ⟦human-owed⟧ ⟦criterion 4⟧
- [ ] `tests/unit-tier.test.sh`, `tests/make-test-env.test.sh` and `tests/pytest-leg.test.sh` pass unmodified ⟦full-suite⟧ ⟦criterion 5⟧
- [ ] CLAUDE.md's fast-tier paragraph (the admission bar, "`make unit` shims `git`, `gh`, `curl` and `python3`…") says which `python3` call the guard lets through: one whose first argument is a module file under `skills/tdd/scripts/veri/`, the hand-off a ported script's shim makes ⟦criterion 6⟧

## Owed steps

- under `make unit`'s guard PATH, `python3 -c …` and `python3` with no arguments run from a working directory inside `skills/tdd/scripts/veri/` are still refused with exit 1, naming `python3`, and logged to `$UNIT_GUARD_LOG`
- when the guard cannot resolve a `veri/` directory beside it, every `python3` call is refused with exit 1, naming `python3`, and logged to `$UNIT_GUARD_LOG` — none reaches the real interpreter
