### 📊 Metrics — issue 2845

Wall time for the issue: 1238 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2850.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.76 over 26 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 86589 tokens, largest 155369 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.55 | 86589 |
| 2 | $0.23 | 113306 |
| 3 | $0.04 | 114954 |
| 4 | $0.04 | 117002 |
| 5 | $0.03 | 117909 |
| 6 | $0.03 | 118300 |
| 7 | $0.04 | 119892 |
| 8 | $0.04 | 121610 |
| 9 | $0.04 | 123076 |
| 10 | $0.04 | 125074 |
| 11 | $0.04 | 127148 |
| 12 | $0.03 | 127999 |
| 13 | $0.04 | 129579 |
| 14 | $0.03 | 130344 |
| 15 | $0.05 | 132906 |
| 16 | $0.06 | 136765 |
| 17 | $0.04 | 138382 |
| 18 | $0.05 | 140703 |
| 19 | $0.04 | 141914 |
| 20 | $0.04 | 143770 |
| 21 | $0.05 | 146847 |
| 22 | $0.05 | 149409 |
| 23 | $0.04 | 151024 |
| 24 | $0.05 | 153764 |
| 25 | $0.04 | 154783 |
| 26 | $0.04 | 155369 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 9 | 6 | 1 | 2 | 766 | 0 | 31461 | 0.09 |
| red | 5 | 1 | 0 | 0 | 156 | 70 | 22 | 44 | 9072 | 640118 | 108761 | 0.43 |
| green | 5 | 2 | 1 | 0 | 331 | 57 | 20 | 38 | 6595 | 528542 | 59749 | 0.27 |
| pin | 3 | 3 | 0 | 0 | 56 | 26 | 10 | 20 | 2898 | 261121 | 44035 | 0.17 |
| refactor | 1 | 0 | 0 | 0 | 8 | 5 | 3 | 6 | 269 | 79403 | 14454 | 0.05 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 7 | 1 | 0 | 306 | 80 | 25 | 50 | 9282 | 646784 | 122393 | 0.46 |
| developer | claude-sonnet-5-5 | 7 | 0 | 0 | 0 | 254 | 84 | 31 | 60 | 10318 | 862400 | 136067 | 0.53 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 331 | 0.27 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A report with `MISSING_TEST: none; <text>` (lower case, trailing text) makes `wrong-test-route.sh` route exactly as the same report with `MISSING_TEST: NONE` does: it answers `revise`, never `missing`. A small in-process case in tests/py/unit/test_wrong_test_route.py ⟦criterion 1⟧ | 10 | 4 | 1 | 0 | 0 | 0 | 109 | 38 | 74 | 12685 | 1011113 | 158357 | 0.62 | 679 | unknown | 0/5 | nothing-left |  |  | already-satisfied |
| `MISSING_TEST: None`, `MISSING_TEST: NONE.` and `MISSING_TEST: none - <text>` each route as `MISSING_TEST: NONE` does, answering `revise`. A small in-process case in tests/py/unit/test_wrong_test_route.py ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 27 | 9 | 18 | 3334 | 274904 | 35679 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |
| A report with `MISSING_TEST: nonexistent <behaviour>`, whose text merely begins with a longer word, still answers `missing nonexistent <behaviour>`. A small in-process case in tests/py/unit/test_wrong_test_route.py ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 22 | 8 | 16 | 2815 | 223167 | 32963 | 0.13 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A report with `MISSING_TEST: none; <text>` (lower case, trailing text) makes `wrong-test-route.sh` route exactly as the same report with `MISSING_TEST: NONE` does: it answers `revise`, never `missing`. A small in-process case in tests/py/unit/test_wrong_test_route.py ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 8 | 0.05 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 4 | 3 | 5 | 5 | 4 | 5 | 4 | 4 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 30 | 42 | 36 | 35 | 29 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 4 | 3 | 3 | 3 | 0 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 4 | 3 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 56 | 110 | 19600 | 1509184 | 258460 | 2.75 (estimate) |
