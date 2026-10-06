# Plan for #1031 — preserve-attempt.sh files an attempt under the first ledger step whose text merely contains the step argument

- [x] With a ledger whose step 1 text contains the digit `2` and which has a step 2, a digits-only step argument `2` is read as a ledger index and writes the ref under `refs/veri/attempts/<issue>/2/` ⟦criterion 1⟧
- [x] A step argument equal to step N's full text writes under index N even when an earlier step's text contains that argument as a substring ⟦criterion 2⟧
- [x] A step argument equal to step N's text with its trailing marks removed — ` ⟦criterion k⟧` and ` ⟂ refactor pending`, the way `next-pending-refactor.sh` prints a step and `supervise.sh` passes it on through `VERI_STEP` — still writes under index N
- [x] A step argument that is only a substring of ledger steps' text, equal to none of them by index or full text, keeps today's fallback, the sanitised argument itself: the two-matches scenario of `test_main_names_the_ref_by_the_first_matching_step_and_keeps_the_argument_when_the_ledger_gives_none` changes from index 2 to `abcd` ⟦criterion 3⟧ ⟂ refactor pending
- [ ] The existing contract cases in `tests/preserve-attempt.test.sh` and `tests/py/test_preserve_attempt.py` are unchanged except the first-match-substring scenario, which changes to the new rule ⟦diff-checked⟧ ⟦criterion 4⟧
- [ ] `make test` is green ⟦full-suite⟧ ⟦criterion 5⟧
