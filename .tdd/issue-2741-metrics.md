### 📊 Metrics — issue 2741

Wall time for the issue: 3974 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2761.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $4.57 over 70 turns, in 2 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87076 tokens, largest 160603 tokens
Conductor context: first turn 87121 tokens, largest 180892 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 87076 |
| 2 | $0.09 | 94078 |
| 3 | $0.04 | 94941 |
| 4 | $0.05 | 96926 |
| 5 | $0.04 | 97585 |
| 6 | $0.04 | 97968 |
| 7 | $0.04 | 98288 |
| 8 | $0.04 | 98560 |
| 9 | $0.05 | 100755 |
| 10 | $0.11 | 110281 |
| 11 | $0.06 | 112346 |
| 12 | $0.06 | 115163 |
| 13 | $0.06 | 117798 |
| 14 | $0.05 | 118881 |
| 15 | $0.05 | 120732 |
| 16 | $0.06 | 122074 |
| 17 | $0.10 | 130605 |
| 18 | $0.06 | 132912 |
| 19 | $0.06 | 134045 |
| 20 | $0.05 | 134909 |
| 21 | $0.05 | 136801 |
| 22 | $0.06 | 138364 |
| 23 | $0.05 | 139447 |
| 24 | $0.14 | 150541 |
| 25 | $0.07 | 153575 |
| 26 | $0.05 | 155023 |
| 27 | $0.08 | 159162 |
| 28 | $0.06 | 160603 |
| 29 | $0.56 | 87121 |
| 30 | $0.07 | 94123 |
| 31 | $0.03 | 95624 |
| 32 | $0.10 | 105173 |
| 33 | $0.05 | 109303 |
| 34 | $0.03 | 109981 |
| 35 | $0.02 | 110313 |
| 36 | $0.03 | 110788 |
| 37 | $0.03 | 111172 |
| 38 | $0.03 | 111840 |
| 39 | $0.16 | 128568 |
| 40 | $0.04 | 130245 |
| 41 | $0.04 | 131672 |
| 42 | $0.04 | 133447 |
| 43 | $0.04 | 135441 |
| 44 | $0.05 | 138002 |
| 45 | $0.04 | 139287 |
| 46 | $0.05 | 141974 |
| 47 | $0.04 | 142936 |
| 48 | $0.05 | 145583 |
| 49 | $0.04 | 147138 |
| 50 | $0.04 | 148812 |
| 51 | $0.06 | 152039 |
| 52 | $0.04 | 153221 |
| 53 | $0.05 | 155084 |
| 54 | $0.05 | 157594 |
| 55 | $0.04 | 158877 |
| 56 | $0.05 | 161228 |
| 57 | $0.12 | 172003 |
| 58 | $0.04 | 173138 |
| 59 | $0.05 | 174960 |
| 60 | $0.04 | 175882 |
| 61 | $0.05 | 177418 |
| 62 | $0.04 | 178125 |
| 63 | $0.04 | 178709 |
| 64 | $0.05 | 179960 |
| 65 | $0.04 | 180892 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 9 | 6 | 1 | 2 | 793 | 0 | 31611 | 0.09 |
| red | 6 | 2 | 0 | 0 | 361 | 123 | 32 | 64 | 14801 | 975778 | 183923 | 0.71 |
| green | 14 | 2 | 5 | 0 | 1651 | 305 | 72 | 132 | 34495 | 2034882 | 247519 | 1.68 |
| red-missing | 2 | 0 | 0 | 0 | 253 | 67 | 16 | 32 | 8399 | 687425 | 94933 | 0.39 |
| pin | 5 | 3 | 0 | 0 | 171 | 64 | 20 | 40 | 7164 | 556968 | 85091 | 0.34 |
| refactor | 1 | 0 | 0 | 0 | 7 | 3 | 2 | 4 | 313 | 48723 | 14548 | 0.04 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 15 | 8 | 5 | 0 | 1200 | 182 | 57 | 112 | 21564 | 1561925 | 229225 | 0.95 |
| developer | claude-sonnet-5-5 | 12 | 0 | 0 | 0 | 1039 | 299 | 76 | 146 | 35365 | 2478084 | 380054 | 1.83 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 213 | 87 | 10 | 16 | 9036 | 263767 | 48346 | 0.48 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 7190 | 6.05 | 0 | 0.00 |
| red-missing | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A pytest leg (`veri/pytest_leg.py`) whose run ends in an xdist INTERNALERROR after some cases had failed prints each failed case's node id ⟦criterion 1⟧ | 24 | 5 | 5 | 0 | 0 | 0 | 499 | 122 | 232 | 57737 | 3694872 | 549976 | 2.84 | 1795 | 4/2 | 0/5 | nothing-left |  |  | already-satisfied |
| A pytest leg whose run ends in an xdist INTERNALERROR says on stderr that the leg was cut short ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 30 | 10 | 20 | 3511 | 296919 | 33458 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |
| A pytest leg whose run ends in an xdist INTERNALERROR after some cases had failed exits non-zero ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 33 | 10 | 20 | 3924 | 311985 | 42580 | 0.18 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A pytest leg (`veri/pytest_leg.py`) whose run ends in an xdist INTERNALERROR after some cases had failed prints each failed case's node id ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.04 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 22 | 8 | 22 | 23 | 16 | 15 | 19 | 19 | 20 | 18 | 23 | 23 | 14 | 15 | 21 | 22 | 22 | 17 | 16 | 6 |  |  |  |
| fast | 49 | 45 | 38 | 32 | 29 | 54 | 47 | 32 | 31 | 43 | 47 | 50 | 41 | 37 |  |  |  |  |  |  |  |  |  |
| target | 7 | 14 | 5 | 5 | 5 | 5 | 10 | 14 | 21 | 8 | 10 | 10 | 15 | 4 | 5 | 5 | 4 | 4 | 4 | 4 | 6 | 5 | 6 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 143 | 274 | 65965 | 4303776 | 657625 | 7.82 (estimate) |
