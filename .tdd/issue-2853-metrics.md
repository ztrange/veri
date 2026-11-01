### 📊 Metrics — issue 2853

Wall time for the issue: 2933 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 5 planned.
Outcome: the run bailed — pr-ready-failed, a system failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.87 over 32 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 86600 tokens, largest 154899 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.55 | 86600 |
| 2 | $0.07 | 93604 |
| 3 | $0.03 | 94990 |
| 4 | $0.04 | 97034 |
| 5 | $0.03 | 98300 |
| 6 | $0.06 | 103144 |
| 7 | $0.02 | 103511 |
| 8 | $0.04 | 106201 |
| 9 | $0.05 | 109190 |
| 10 | $0.03 | 110197 |
| 11 | $0.06 | 115017 |
| 12 | $0.06 | 119540 |
| 13 | $0.04 | 121422 |
| 14 | $0.04 | 123550 |
| 15 | $0.05 | 126533 |
| 16 | $0.03 | 127407 |
| 17 | $0.04 | 129115 |
| 18 | $0.03 | 129948 |
| 19 | $0.03 | 130655 |
| 20 | $0.05 | 133304 |
| 21 | $0.04 | 135360 |
| 22 | $0.03 | 136219 |
| 23 | $0.04 | 137980 |
| 24 | $0.04 | 139385 |
| 25 | $0.05 | 142495 |
| 26 | $0.04 | 143954 |
| 27 | $0.03 | 144314 |
| 28 | $0.03 | 144979 |
| 29 | $0.03 | 145195 |
| 30 | $0.04 | 146041 |
| 31 | $0.06 | 149292 |
| 32 | $0.07 | 154899 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 8 | 7 | 1 | 2 | 816 | 0 | 31874 | 0.09 |
| red | 6 | 1 | 0 | 0 | 248 | 131 | 31 | 60 | 15540 | 937469 | 153098 | 0.63 |
| pin | 4 | 4 | 0 | 0 | 108 | 66 | 18 | 36 | 6396 | 505546 | 64350 | 0.28 |
| green | 4 | 1 | 1 | 0 | 431 | 59 | 17 | 32 | 5597 | 443653 | 59560 | 0.25 |
| refactor | 2 | 1 | 0 | 0 | 101 | 24 | 8 | 16 | 1806 | 221822 | 28698 | 0.11 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 9 | 8 | 1 | 0 | 515 | 133 | 37 | 72 | 12634 | 984604 | 160836 | 0.63 |
| developer | claude-sonnet-5-5 | 8 | 0 | 0 | 0 | 381 | 154 | 38 | 74 | 17521 | 1123886 | 176744 | 0.73 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 431 | 0.25 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A verified refactor that deletes an assertion line of a frozen case leaves its record stale: `rerecord-refactored` leaves the record unchanged and `check-earlier` still exits 1 (a `process` case in a real git repository under tmp_path; no production change expected) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 42 | 11 | 22 | 5015 | 337023 | 65010 | 0.25 | unknown | unknown | unknown | unknown |  |  | pin |
| A verified refactor that deletes one of two identical assertion lines of a frozen case leaves its record stale: `rerecord-refactored` leaves the record unchanged and `check-earlier` still exits 1, so the comparison counts duplicates (a `process` case in a real git repository under tmp_path; no production change expected) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 40 | 9 | 18 | 4227 | 262206 | 35134 | 0.16 | unknown | unknown | unknown | unknown |  |  | pin |
| A verified refactor that extracts a frozen Go case's setup `t.Fatal` lines, from before its later assertions, into a helper the case calls is re-recorded by `rerecord-refactored` although the head's lines followed by the helper's differ in order from the verified body's: the record is rewritten and `check-earlier` exits 0 (a `process` case in a real git repository under tmp_path) ⟦criterion 1⟧ | 10 | 4 | 1 | 0 | 0 | 0 | 161 | 46 | 88 | 15933 | 1280973 | 169128 | 0.71 | 913 | unknown | 1/5 | nothing-structural |  |  | already-satisfied |
| Re-running `rerecord-refactored` with the same green sha heals an order-changing helper extraction's record already stale from an earlier run, which left it unchanged: a record holding the verified body's digest while HEAD holds the refactored body is rewritten and `check-earlier` exits 0 (a `process` case in a real git repository under tmp_path) ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 37 | 8 | 16 | 4164 | 228288 | 36434 | 0.16 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A verified refactor that extracts a frozen Go case's setup `t.Fatal` lines, from before its later assertions, into a helper the case calls is re-recorded by `rerecord-refactored` although the head's lines followed by the helper's differ in order from the verified body's: the record is rewritten and `check-earlier` exits 0 (a `process` case in a real git repository under tmp_path) ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 101 | 0.11 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 3 | 3 | 0 | 4 | 29 | 26 | 20 | 16 | 20 | 25 | 17 |  |  |  |  |  |  |  |  |  |  |  |
| target | 3 | 4 | 4 | 4 | 4 | 3 | 3 | 4 | 3 | 4 | 2 | 2 | 3 | 3 | 2 | 3 | 3 | 2 | 3 | 3 | 4 | 4 |
| fast | 44 | 41 | 31 | 33 | 30 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 75 | 146 | 30155 | 2108490 | 337580 | 3.23 (estimate) |
