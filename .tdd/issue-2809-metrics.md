### 📊 Metrics — issue 2809

Wall time for the issue: 7141 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2817.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.99 over 34 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87285 tokens, largest 155806 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 87285 |
| 2 | $0.07 | 94287 |
| 3 | $0.03 | 95668 |
| 4 | $0.04 | 97721 |
| 5 | $0.02 | 98210 |
| 6 | $0.10 | 108344 |
| 7 | $0.02 | 108659 |
| 8 | $0.02 | 108929 |
| 9 | $0.02 | 109209 |
| 10 | $0.04 | 111167 |
| 11 | $0.04 | 113523 |
| 12 | $0.13 | 126535 |
| 13 | $0.03 | 127595 |
| 14 | $0.04 | 129209 |
| 15 | $0.03 | 130013 |
| 16 | $0.04 | 131890 |
| 17 | $0.08 | 138945 |
| 18 | $0.05 | 141996 |
| 19 | $0.03 | 142748 |
| 20 | $0.04 | 144738 |
| 21 | $0.05 | 147010 |
| 22 | $0.05 | 149079 |
| 23 | $0.04 | 149908 |
| 24 | $0.05 | 151845 |
| 25 | $0.04 | 152585 |
| 26 | $0.03 | 152852 |
| 27 | $0.03 | 153177 |
| 28 | $0.03 | 153501 |
| 29 | $0.04 | 154078 |
| 30 | $0.03 | 154361 |
| 31 | $0.03 | 154633 |
| 32 | $0.03 | 154937 |
| 33 | $0.03 | 155239 |
| 34 | $0.04 | 155806 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 8 | 1 | 2 | 1045 | 0 | 32135 | 0.09 |
| red | 5 | 2 | 0 | 0 | 270 | 86 | 25 | 50 | 10258 | 826996 | 137353 | 0.53 |
| green | 4 | 2 | 0 | 0 | 581 | 40 | 17 | 32 | 4080 | 447874 | 60874 | 0.24 |
| refactor | 3 | 1 | 0 | 0 | 150 | 18 | 9 | 18 | 1690 | 241058 | 43499 | 0.15 |
| pin | 1 | 1 | 0 | 0 | 26 | 13 | 4 | 8 | 1415 | 109845 | 15668 | 0.06 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 7 | 7 | 0 | 0 | 565 | 64 | 21 | 42 | 6808 | 538718 | 126910 | 0.44 |
| developer | claude-sonnet-5-5 | 7 | 0 | 0 | 0 | 474 | 101 | 35 | 68 | 11680 | 1087055 | 162619 | 0.63 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| rerecord-refactored leaves an earlier step's record unchanged when a refactor changes a line of a Go case's body starting `t.Fatal`, `t.Error`, `t.Fail` or `require.`, whichever of the four forms it is (one parametrised case in skills/tdd/scripts/tests/py/test_tests_frozen_process.py, a process case with real git) ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 58 | 22 | 42 | 6479 | 624638 | 108093 | 0.40 | 564 | unknown | 0/5 | nothing-left |  |  | full |
| rerecord-refactored re-records an earlier step's case whose verified body has no recognised assertion line when its body at HEAD differs from the verified body only in whitespace (a pin in skills/tdd/scripts/tests/py/test_tests_frozen_process.py, a process case with real git) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 39 | 10 | 20 | 4475 | 328922 | 45869 | 0.19 | unknown | unknown | unknown | unknown |  |  | pin |
| rerecord-refactored leaves an earlier step's record unchanged when the case's verified body has no recognised assertion line and its body at HEAD differs from the verified body other than in whitespace (a case in skills/tdd/scripts/tests/py/test_tests_frozen_process.py, a process case with real git) ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 60 | 23 | 46 | 6489 | 672213 | 103432 | 0.39 | 733 | unknown | 1/5 | nothing-structural |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| rerecord-refactored leaves an earlier step's record unchanged when a refactor changes a line of a Go case's body starting `t.Fatal`, `t.Error`, `t.Fail` or `require.`, whichever of the four forms it is (one parametrised case in skills/tdd/scripts/tests/py/test_tests_frozen_process.py, a process case with real git) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.04 |
| rerecord-refactored leaves an earlier step's record unchanged when the case's verified body has no recognised assertion line and its body at HEAD differs from the verified body other than in whitespace (a case in skills/tdd/scripts/tests/py/test_tests_frozen_process.py, a process case with real git) ⟦criterion 2⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 143 | 0.11 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 6 | 7 | 33 | 35 | 3 | 21 | 30 | 36 | 37 | 36 | 34 |
| fast | 46 | 45 | 49 | 44 | 45 |  |  |  |  |  |  |  |
| target | 1 | 7 | 4 | 5 | 6 | 7 | 7 |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 56 | 110 | 18488 | 1625773 | 289529 | 3.06 (estimate) |
