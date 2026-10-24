### 📊 Metrics — issue 2288

Wall time for the issue: 709 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 1 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2326.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.40 over 30 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.58 | 90404 |
| 2 | $0.03 | 91544 |
| 3 | $0.03 | 93496 |
| 4 | $0.02 | 93940 |
| 5 | $0.02 | 94291 |
| 6 | $0.02 | 94614 |
| 7 | $0.02 | 95210 |
| 8 | $0.03 | 96395 |
| 9 | $0.03 | 97162 |
| 10 | $0.03 | 97869 |
| 11 | $0.02 | 98421 |
| 12 | $0.03 | 99165 |
| 13 | $0.03 | 100561 |
| 14 | $0.03 | 101456 |
| 15 | $0.04 | 103824 |
| 16 | $0.03 | 104738 |
| 17 | $0.03 | 105777 |
| 18 | $0.04 | 107862 |
| 19 | $0.03 | 108664 |
| 20 | $0.03 | 109628 |
| 21 | $0.03 | 110355 |
| 22 | $0.03 | 111740 |
| 23 | $0.03 | 112541 |
| 24 | $0.03 | 113521 |
| 25 | $0.03 | 113966 |
| 26 | $0.03 | 114260 |
| 27 | $0.03 | 114540 |
| 28 | $0.03 | 115043 |
| 29 | $0.03 | 115368 |
| 30 | $0.03 | 115822 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 7 | 5 | 1 | 2 | 558 | 17442 | 13954 | 0.04 |
| red | 2 | 1 | 0 | 0 | 34 | 24 | 7 | 14 | 2684 | 199820 | 34127 | 0.13 |
| green | 2 | 1 | 0 | 0 | 65 | 22 | 10 | 20 | 2337 | 290255 | 31037 | 0.13 |
| refactor | 2 | 1 | 0 | 0 | 44 | 19 | 9 | 18 | 2371 | 268203 | 33293 | 0.13 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 4 | 4 | 0 | 0 | 77 | 27 | 11 | 22 | 2902 | 284078 | 58102 | 0.20 |
| developer | claude-sonnet-5-5 | 3 | 0 | 0 | 0 | 73 | 43 | 16 | 32 | 5048 | 491642 | 54309 | 0.24 |

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

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| run-finished.sh decides a PR-body line human-owed by ledger_steps' rule (a leading mark or one in the trailing marker run): an unticked PR-body line quoting the human-owed mark mid-prose ("- [ ] a ⟦human-owed⟧ x") is not listed, while "- [ ] measure X ⟦human-owed⟧" and "- [ ] ⟦human-owed⟧ measure X" still are; pinned by a small in-process case in tests/py/unit/test_run_finished.py ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 44 | 0.13 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 1 | 1 | 1 | 2 |
| fast | 16 | 15 | 16 |  |  |  |
| target | 1 |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 27 | 54 | 7950 | 775720 | 112411 | 0.44 |
