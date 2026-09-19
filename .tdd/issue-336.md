# Plan for #336 — `make unit` runs a hand-picked fast tier; `make test` still runs everything with the same checks

- [x] `make -n unit` lists only suites matching `skills/tdd/scripts/tests/unit/*.test.sh` ⟦criterion 1⟧
- [x] `make -n test` lists suites from both `skills/tdd/scripts/tests/*.test.sh` and `skills/tdd/scripts/tests/unit/*.test.sh`, with no suite listed twice ⟦criterion 2⟧ ⟂ refactor pending
- [ ] `make unit` applies the same per-suite count-line check and the same `OFFLINE_BIN` network-block guard (reach log) as `make test` ⟦criterion 3⟧
- [ ] `make unit` runs each suite with `LC_ALL=C` and stdin from `/dev/null`, as `make test` does
- [ ] `make unit` shims `git`, `gh`, `curl` and `python3` to exit nonzero naming themselves, while `make test` does not: a unit fixture calling real `git` fails under `make unit` naming `git`, and passes through `make test`'s recipe, as does a sibling fixture mocking `git` as a shell function ⟦criterion 4⟧
- [ ] At least five existing suites move into `skills/tdd/scripts/tests/unit/`, each still passing its own cases, each recording in its header comment its git/python3/server/sleep usage count as the reason it qualifies ⟦criterion 5⟧
- [ ] CLAUDE.md's "Testing idiom" section states the admission bar (~100 ms/case, no git, network, servers, real waits or nested suites) and names `skills/tdd/scripts/tests/unit/` as the fast tier, pinned by a guard suite in the style of `model-knobs-recorded.test.sh` ⟦criterion 6⟧
