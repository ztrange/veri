### 📊 Metrics — issue 1167

Wall time for the issue: 1982 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1211.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 8 | 6 | 1 | 2 | 679 | 12385 | 29989 | 0.13 |
| red | 5 | 2 | 0 | 0 | 130 | 104 | 28 | 54 | 10525 | 1199140 | 214555 | 1.85 |
| green | 4 | 2 | 0 | 0 | 310 | 93 | 29 | 54 | 9500 | 1188152 | 160713 | 1.36 |
| refactor | 4 | 2 | 0 | 0 | 156 | 62 | 20 | 40 | 6361 | 838028 | 157105 | 1.23 |
| pin | 1 | 1 | 0 | 0 | 11 | 8 | 3 | 6 | 1045 | 103686 | 38141 | 0.18 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 8 | 0 | 0 | 263 | 91 | 32 | 62 | 10426 | 1179314 | 294793 | 1.52 |
| developer | claude-opus-5-5 | 7 | 0 | 0 | 0 | 352 | 182 | 49 | 94 | 17684 | 2162077 | 305710 | 3.23 |

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
| A suite killed by signal N after it printed its count line makes run-suite.sh exit 128+N ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 81 | 29 | 54 | 8562 | 1092109 | 237819 | 1.82 | 279 | unknown | 0/5 | nothing-left |  |  | full |
| A suite path that does not exist makes run-suite.sh print `<name>: never reached its count line` and `<name>: its output was empty` on stderr, with no traceback, and exit 1 ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 146 | 41 | 80 | 14571 | 1807022 | 250523 | 2.14 | 387 | unknown | 1/5 | nothing-left |  |  | full |
| A suite path that exists but is not executable makes run-suite.sh print `<name>: never reached its count line` and `<name>: its output was empty` on stderr, with no traceback, and exit 1 ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 40 | 10 | 20 | 4298 | 429875 | 82172 | 0.67 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A suite killed by signal N after it printed its count line makes run-suite.sh exit 128+N ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 55 | 0.56 |
| A suite path that does not exist makes run-suite.sh print `<name>: never reached its count line` and `<name>: its output was empty` on stderr, with no traceback, and exit 1 ⟦criterion 2⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 101 | 0.67 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 0 | 30 | 0 | 0 | 1 | 1 | 1 | 29 | 7 | 27 | 0 | 1 |
| fast | 27 | 27 | 27 | 28 | 28 | 27 |  |  |  |  |  |  |  |  |
| target | 1 | 1 | 1 | 0 |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 81 | 156 | 28110 | 3341391 | 600503 | 4.75 |
