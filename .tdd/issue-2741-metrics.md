### 📊 Metrics — issue 2741

Wall time for the issue: 1218 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: unknown of 3 planned.
Outcome: the run bailed — no-verdict, a system failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.69 over 26 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87076 tokens, largest 155023 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.55 | 87076 |
| 2 | $0.07 | 94078 |
| 3 | $0.03 | 94941 |
| 4 | $0.03 | 96926 |
| 5 | $0.02 | 97585 |
| 6 | $0.02 | 97968 |
| 7 | $0.02 | 98288 |
| 8 | $0.02 | 98560 |
| 9 | $0.04 | 100755 |
| 10 | $0.10 | 110281 |
| 11 | $0.04 | 112346 |
| 12 | $0.05 | 115163 |
| 13 | $0.04 | 117798 |
| 14 | $0.03 | 118881 |
| 15 | $0.04 | 120732 |
| 16 | $0.03 | 122074 |
| 17 | $0.09 | 130605 |
| 18 | $0.04 | 132912 |
| 19 | $0.04 | 134045 |
| 20 | $0.03 | 134909 |
| 21 | $0.04 | 136801 |
| 22 | $0.04 | 138364 |
| 23 | $0.04 | 139447 |
| 24 | $0.12 | 150541 |
| 25 | $0.05 | 153575 |
| 26 | $0.04 | 155023 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 9 | 6 | 1 | 2 | 793 | 0 | 31611 | 0.09 |
| red | 2 | 1 | 0 | 0 | 139 | 46 | 10 | 20 | 5492 | 294339 | 59855 | 0.23 |
| green | 5 | 0 | 2 | 0 | 524 | 89 | 29 | 52 | 10405 | 793372 | 92858 | 0.60 |
| red-missing | 1 | 0 | 0 | 0 | 197 | 47 | 11 | 22 | 5677 | 554472 | 59822 | 0.26 |
| pin | 2 | 0 | 0 | 0 | 57 | 25 | 7 | 14 | 2771 | 186905 | 34399 | 0.13 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 6 | 2 | 2 | 0 | 365 | 70 | 20 | 40 | 8144 | 532533 | 101149 | 0.39 |
| developer | claude-sonnet-5-5 | 2 | 0 | 0 | 0 | 259 | 80 | 17 | 34 | 9706 | 738113 | 103716 | 0.43 |
| developer | claude-opus-5-5 | 3 | 0 | 0 | 0 | 302 | 63 | 21 | 36 | 7288 | 558442 | 73680 | 0.49 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 139 | 0.23 |
| green | 0 | 0.00 | 524 | 0.60 |
| red-missing | 0 | 0.00 | 197 | 0.26 |
| pin | 0 | 0.00 | 57 | 0.13 |
| verify-pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A pytest leg (`veri/pytest_leg.py`) whose run ends in an xdist INTERNALERROR after some cases had failed prints each failed case's node id ⟦criterion 1⟧ | 10 | 1 | 2 | 0 | 0 | 0 | 207 | 57 | 108 | 24345 | 1829088 | 246934 | 1.22 | unknown | 2/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 22 | 8 | 22 | 23 | 16 | 15 | 19 | 19 |
| fast | 49 | 45 | 38 | 32 | 29 |  |  |  |
| target | 7 | 14 | 5 | 5 | 5 | 5 |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 58 | 110 | 25138 | 1829088 | 278545 | 3.00 (estimate) |
