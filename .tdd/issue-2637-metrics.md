### 📊 Metrics — issue 2637

Wall time for the issue: 4768 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2638.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $3.31 over 79 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 84244 tokens, largest 168373 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.53 | 84244 |
| 2 | $0.07 | 90862 |
| 3 | $0.04 | 93882 |
| 4 | $0.03 | 95554 |
| 5 | $0.02 | 96185 |
| 6 | $0.02 | 96871 |
| 7 | $0.02 | 97274 |
| 8 | $0.02 | 97565 |
| 9 | $0.02 | 98214 |
| 10 | $0.02 | 98591 |
| 11 | $0.04 | 100677 |
| 12 | $0.03 | 102003 |
| 13 | $0.02 | 102400 |
| 14 | $0.03 | 103088 |
| 15 | $0.03 | 103645 |
| 16 | $0.03 | 104332 |
| 17 | $0.03 | 104883 |
| 18 | $0.03 | 106145 |
| 19 | $0.03 | 107031 |
| 20 | $0.03 | 107615 |
| 21 | $0.03 | 108854 |
| 22 | $0.03 | 109658 |
| 23 | $0.03 | 110312 |
| 24 | $0.02 | 110576 |
| 25 | $0.03 | 111262 |
| 26 | $0.03 | 111883 |
| 27 | $0.03 | 113325 |
| 28 | $0.03 | 113688 |
| 29 | $0.03 | 114499 |
| 30 | $0.09 | 122654 |
| 31 | $0.09 | 130693 |
| 32 | $0.03 | 131050 |
| 33 | $0.04 | 132150 |
| 34 | $0.03 | 132585 |
| 35 | $0.03 | 133609 |
| 36 | $0.03 | 134392 |
| 37 | $0.05 | 136705 |
| 38 | $0.03 | 137614 |
| 39 | $0.04 | 138896 |
| 40 | $0.03 | 139365 |
| 41 | $0.03 | 140048 |
| 42 | $0.03 | 140606 |
| 43 | $0.04 | 141955 |
| 44 | $0.04 | 142857 |
| 45 | $0.04 | 143734 |
| 46 | $0.04 | 144735 |
| 47 | $0.04 | 145712 |
| 48 | $0.04 | 146703 |
| 49 | $0.04 | 147629 |
| 50 | $0.04 | 148515 |
| 51 | $0.03 | 149168 |
| 52 | $0.04 | 150145 |
| 53 | $0.04 | 151677 |
| 54 | $0.04 | 152454 |
| 55 | $0.04 | 153183 |
| 56 | $0.03 | 153523 |
| 57 | $0.04 | 154406 |
| 58 | $0.03 | 154859 |
| 59 | $0.04 | 155990 |
| 60 | $0.05 | 158379 |
| 61 | $0.04 | 159087 |
| 62 | $0.03 | 159350 |
| 63 | $0.04 | 160214 |
| 64 | $0.04 | 161433 |
| 65 | $0.04 | 162185 |
| 66 | $0.04 | 163003 |
| 67 | $0.04 | 163415 |
| 68 | $0.04 | 163917 |
| 69 | $0.04 | 164659 |
| 70 | $0.04 | 165258 |
| 71 | $0.04 | 165717 |
| 72 | $0.04 | 166253 |
| 73 | $0.04 | 166571 |
| 74 | $0.04 | 166840 |
| 75 | $0.04 | 167064 |
| 76 | $0.04 | 167335 |
| 77 | $0.04 | 167634 |
| 78 | $0.04 | 168023 |
| 79 | $0.04 | 168373 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 7 | 1 | 2 | 893 | 0 | 33966 | 0.09 |
| red | 7 | 2 | 0 | 0 | 365 | 292 | 57 | 112 | 26961 | 2136679 | 213802 | 1.51 |
| green | 5 | 1 | 1 | 0 | 400 | 94 | 27 | 54 | 10721 | 829366 | 134943 | 0.67 |
| red-contradicted | 1 | 0 | 0 | 0 | 42 | 22 | 6 | 12 | 2832 | 200827 | 22461 | 0.10 |
| refactor | 1 | 0 | 0 | 0 | 6 | 3 | 2 | 4 | 142 | 50695 | 16276 | 0.05 |
| pin | 2 | 2 | 0 | 0 | 50 | 33 | 9 | 18 | 2512 | 262202 | 34538 | 0.14 |
| rebase | 2 | 1 | 0 | 0 | 1178 | 22 | 8 | 16 | 2126 | 164649 | 99556 | 0.29 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 7 | 1 | 0 | 1376 | 102 | 29 | 58 | 9819 | 744403 | 222801 | 0.73 |
| developer | claude-opus-5-5 | 3 | 0 | 0 | 0 | 256 | 224 | 39 | 76 | 19138 | 1583863 | 114414 | 1.13 |
| developer | claude-sonnet-5-5 | 8 | 0 | 0 | 0 | 419 | 147 | 42 | 84 | 17230 | 1316152 | 218327 | 0.99 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 400 | 0.67 | 0 | 0.00 |
| red-contradicted | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| rebase | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| check-earlier skips a ghost case: with a ledger holding `- [x] B` and `- [ ] C`, and B's record holding a body line for `test_ghost` in `test_suite.py` that is in neither the work-tree file nor any revision of that file reachable from HEAD, `check-earlier <ledger> --step C` exits 0 with nothing on stdout, and its stderr names `test_ghost`, B and B's record path (`.tdd/tests-frozen-<k>.record`), saying the case is in no revision of this branch and was skipped; a small case in skills/tdd/scripts/tests/py/unit/test_tests_frozen.py faking only the git-facing helpers (`_toplevel`, `_cases_at`, `_work_tree_hash`, `_write_pass_marker`, and whatever lists the file's revisions), as the existing check_earlier cases there do ⟦criterion 1⟧ | 12 | 3 | 1 | 0 | 0 | 0 | 364 | 81 | 160 | 35054 | 2846645 | 341853 | 2.12 | 1142 | green 1/2, red 2/2 | 0/5 | nothing-left |  |  | full |
| check-earlier still flags a deleted real case: with the same ledger, a case B's record holds that a revision of `test_suite.py` reachable from HEAD held but the work-tree file no longer holds makes `check-earlier <ledger> --step C` exit 1 and print `<case> (B)` on stdout; a small case in skills/tdd/scripts/tests/py/unit/test_tests_frozen.py faking only the git-facing helpers ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 9 | 18 | 3597 | 279558 | 39750 | 0.16 | unknown | unknown | unknown | unknown |  |  | pin |
| check-earlier reports a real change when a ghost sits beside it: when B's record holds both a ghost case and a case whose work-tree body has changed, `check-earlier <ledger> --step C` exits 1, its stdout names only the changed case (`<case> (B)`), and its stderr names the ghost as skipped; a small case in skills/tdd/scripts/tests/py/unit/test_tests_frozen.py faking only the git-facing helpers ⟦criterion 3⟧ | 4 | 2 | 0 | 0 | 0 | 0 | 68 | 19 | 38 | 6643 | 518215 | 139973 | 0.47 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| check-earlier skips a ghost case: with a ledger holding `- [x] B` and `- [ ] C`, and B's record holding a body line for `test_ghost` in `test_suite.py` that is in neither the work-tree file nor any revision of that file reachable from HEAD, `check-earlier <ledger> --step C` exits 0 with nothing on stdout, and its stderr names `test_ghost`, B and B's record path (`.tdd/tests-frozen-<k>.record`), saying the case is in no revision of this branch and was skipped; a small case in skills/tdd/scripts/tests/py/unit/test_tests_frozen.py faking only the git-facing helpers (`_toplevel`, `_cases_at`, `_work_tree_hash`, `_write_pass_marker`, and whatever lists the file's revisions), as the existing check_earlier cases there do ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 6 | 0.05 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 3 | 3 | 2 | 10 | 2 | 9 | 14 | 2 | 8 | 2 | 8 | 8 | 9 | 2 | 2 |
| fast | 30 | 26 | 26 | 26 | 26 |  |  |  |  |  |  |  |  |  |  |
| target | 2 | 2 | 3 | 2 | 3 | 2 |  |  |  |  |  |  |  |  |  |
| all | 34 | 1111 |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 110 | 218 | 46187 | 3644418 | 555542 | 6.16 (estimate) |
