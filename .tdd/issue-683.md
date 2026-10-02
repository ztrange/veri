# Plan for #683 — the test-only candidate match, the count-line check and the stop-mode list each live in one place

- [x] `test_only_candidate <line>` in `lib/candidate-line.sh` returns 0 for a `CANDIDATES: test-only | <transform>` line, setting `TEST_ONLY_TRANSFORM` to `<transform>`, and returns 1 (leaving it unset) for a structural, cosmetic or `none` line ⟦criterion 1⟧
- [x] `refactor-owed.sh append` records a test-only candidate through `test_only_candidate`, with no test-only regex of its own (`! grep -nE 'test-only\)?\[\[:space:\]\]' skills/tdd/scripts/refactor-owed.sh`) ⟦criterion 2⟧
- [x] `refactor-triage.sh` accepts a test-only candidate line through `test_only_candidate`, with no test-only regex of its own (`! grep -nE 'test-only\)?\[\[:space:\]\]' skills/tdd/scripts/refactor-triage.sh`), and still exits 3 on a report whose only leftovers are test-only ⟦criterion 2⟧
- [x] `run-suite.sh` over a suite that prints its count line on stdout and then one line on stderr exits with the suite's own code (0 for a green suite), as `make test` does ⟦criterion 4⟧
- [x] `run-suite.sh` over a suite that exits 0 without its count line prints `<suite>: never reached its count line` and then `<suite>: its last line was: <line>`, or `<suite>: its output was empty` when it printed nothing, and exits 1 ⟦criterion 5⟧
- [x] `run-suite.sh` with no `lib/count-line-guard.sh` beside it exits 2 with a stderr line naming that file, and runs no `make` ⟦criterion 6⟧
- [ ] `make test` holds every suite to its count line by running it through `run-suite.sh` (no `tail -n 1` left in the Makefile): a suite that exits 0 without its count line still fails the run, printing `<suite>: never reached its count line` and then its last line or that its output was empty ⟦criterion 3⟧
- [ ] The Makefile has no `count-line-guard` target (`! grep -n '^count-line-guard:' Makefile`), and no suite reads one ⟦criterion 7⟧
- [ ] `stop-run.sh` takes its accepted stop modes from one sourced list in `lib/`, and still refuses a mode outside it with `stop-run: unknown mode — want at-ledger, at-leaf or now: '<mode>'` ⟦criterion 8⟧
- [ ] `stop-requested.sh` takes its accepted stop modes from the same sourced list, and still refuses a `.tdd/stop` naming a mode outside it with today's exit-2 message; no script under `skills/tdd/scripts/` spells `at-ledger | at-leaf | now)` ⟦criterion 8⟧
- [ ] `make test` is green ⟦full-suite⟧ ⟦criterion 9⟧
