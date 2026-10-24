### 📊 Metrics — issue 2288

Wall time for the issue: 668 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2326.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $3.45 over 69 turns, in 2 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.59 | 90404 |
| 2 | $0.04 | 91544 |
| 3 | $0.04 | 93496 |
| 4 | $0.03 | 93940 |
| 5 | $0.03 | 94291 |
| 6 | $0.03 | 94614 |
| 7 | $0.04 | 95210 |
| 8 | $0.04 | 96395 |
| 9 | $0.03 | 97162 |
| 10 | $0.04 | 97869 |
| 11 | $0.03 | 98421 |
| 12 | $0.03 | 99165 |
| 13 | $0.04 | 100561 |
| 14 | $0.04 | 101456 |
| 15 | $0.05 | 103824 |
| 16 | $0.04 | 104738 |
| 17 | $0.04 | 105777 |
| 18 | $0.04 | 107862 |
| 19 | $0.04 | 108664 |
| 20 | $0.04 | 109628 |
| 21 | $0.04 | 110355 |
| 22 | $0.04 | 111740 |
| 23 | $0.04 | 112541 |
| 24 | $0.04 | 113521 |
| 25 | $0.03 | 113966 |
| 26 | $0.04 | 114260 |
| 27 | $0.03 | 114540 |
| 28 | $0.04 | 115043 |
| 29 | $0.04 | 115368 |
| 30 | $0.03 | 115822 |
| 31 | $0.04 | 116387 |
| 32 | $0.04 | 117244 |
| 33 | $0.58 | 90408 |
| 34 | $0.03 | 91597 |
| 35 | $0.03 | 93519 |
| 36 | $0.02 | 94081 |
| 37 | $0.10 | 104761 |
| 38 | $0.05 | 108179 |
| 39 | $0.02 | 108571 |
| 40 | $0.03 | 108983 |
| 41 | $0.02 | 109267 |
| 42 | $0.02 | 109541 |
| 43 | $0.03 | 110149 |
| 44 | $0.03 | 110849 |
| 45 | $0.03 | 111496 |
| 46 | $0.03 | 112001 |
| 47 | $0.03 | 113338 |
| 48 | $0.03 | 114368 |
| 49 | $0.03 | 114805 |
| 50 | $0.03 | 115509 |
| 51 | $0.03 | 116214 |
| 52 | $0.03 | 116491 |
| 53 | $0.03 | 117201 |
| 54 | $0.03 | 117803 |
| 55 | $0.03 | 119144 |
| 56 | $0.03 | 120106 |
| 57 | $0.03 | 120536 |
| 58 | $0.03 | 121230 |
| 59 | $0.03 | 121696 |
| 60 | $0.03 | 122396 |
| 61 | $0.03 | 122779 |
| 62 | $0.03 | 123431 |
| 63 | $0.03 | 124094 |
| 64 | $0.03 | 124660 |
| 65 | $0.03 | 124954 |
| 66 | $0.03 | 125289 |
| 67 | $0.03 | 125798 |
| 68 | $0.03 | 126096 |
| 69 | $0.03 | 126503 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 7 | 5 | 1 | 2 | 558 | 17442 | 13954 | 0.04 |
| red | 4 | 2 | 0 | 0 | 70 | 52 | 14 | 28 | 6138 | 398523 | 68819 | 0.27 |
| green | 4 | 2 | 0 | 0 | 139 | 52 | 21 | 40 | 5801 | 582143 | 62697 | 0.27 |
| refactor | 3 | 1 | 0 | 0 | 49 | 22 | 11 | 22 | 2514 | 317014 | 47180 | 0.17 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 6 | 6 | 0 | 0 | 129 | 51 | 18 | 36 | 5699 | 473293 | 88272 | 0.33 |
| developer | claude-sonnet-5-5 | 6 | 0 | 0 | 0 | 136 | 80 | 29 | 56 | 9312 | 841829 | 104378 | 0.44 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| run-finished.sh decides a PR-body line human-owed by ledger_steps' rule (a leading mark or one in the trailing marker run): an unticked PR-body line quoting the human-owed mark mid-prose ("- [ ] a ⟦human-owed⟧ x") is not listed, while "- [ ] measure X ⟦human-owed⟧" and "- [ ] ⟦human-owed⟧ measure X" still are; pinned by a small in-process case in tests/py/unit/test_run_finished.py ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 65 | 26 | 52 | 7392 | 758278 | 98457 | 0.40 | 232 | unknown | 1/5 | nothing-left |  |  | full |
| is_human_owed (ledger.py:103-104) strips surrounding whitespace and reads a marker run with or without spaces between marks, so `measure X ⟦human-owed⟧` with trailing spaces, ` ⟦human-owed⟧ x` with a leading space and `measure X ⟦human-owed⟧⟦criterion 1⟧` are human-owed for both ledger_steps and run-finished.sh, while `a ⟦human-owed⟧ x` stays a step: pinned by small unit cases in tests/py/unit/test_ledger_steps.py and run_finished's unit tests ⟦added⟧ ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 61 | 20 | 38 | 7061 | 539402 | 80239 | 0.33 | 222 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| run-finished.sh decides a PR-body line human-owed by ledger_steps' rule (a leading mark or one in the trailing marker run): an unticked PR-body line quoting the human-owed mark mid-prose ("- [ ] a ⟦human-owed⟧ x") is not listed, while "- [ ] measure X ⟦human-owed⟧" and "- [ ] ⟦human-owed⟧ measure X" still are; pinned by a small in-process case in tests/py/unit/test_run_finished.py ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 44 | 0.13 |
| is_human_owed (ledger.py:103-104) strips surrounding whitespace and reads a marker run with or without spaces between marks, so `measure X ⟦human-owed⟧` with trailing spaces, ` ⟦human-owed⟧ x` with a leading space and `measure X ⟦human-owed⟧⟦criterion 1⟧` are human-owed for both ledger_steps and run-finished.sh, while `a ⟦human-owed⟧ x` stays a step: pinned by small unit cases in tests/py/unit/test_ledger_steps.py and run_finished's unit tests ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 5 | 0.04 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 1 | 1 | 1 | 2 | 1 | 1 | 1 | 2 |
| fast | 16 | 15 | 16 | 16 | 16 |  |  |  |  |  |
| target | 1 | 1 |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 47 | 92 | 15011 | 1315122 | 192650 | 0.76 |
