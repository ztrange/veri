### 📊 Metrics — issue 2913

Wall time for the issue: 642 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 3 planned.
Outcome: the run bailed — ci-timeout, a system failure.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.82 over 41 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 88079 tokens, largest 131615 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 88079 |
| 2 | $0.07 | 94776 |
| 3 | $0.03 | 96076 |
| 4 | $0.03 | 97730 |
| 5 | $0.03 | 99072 |
| 6 | $0.03 | 99883 |
| 7 | $0.02 | 100230 |
| 8 | $0.02 | 100577 |
| 9 | $0.03 | 101230 |
| 10 | $0.03 | 102947 |
| 11 | $0.03 | 104103 |
| 12 | $0.03 | 105218 |
| 13 | $0.03 | 106599 |
| 14 | $0.03 | 107368 |
| 15 | $0.03 | 107968 |
| 16 | $0.03 | 108708 |
| 17 | $0.03 | 109148 |
| 18 | $0.03 | 110530 |
| 19 | $0.03 | 111485 |
| 20 | $0.03 | 113033 |
| 21 | $0.03 | 113799 |
| 22 | $0.03 | 114543 |
| 23 | $0.03 | 115089 |
| 24 | $0.03 | 115781 |
| 25 | $0.03 | 116391 |
| 26 | $0.03 | 117436 |
| 27 | $0.03 | 118257 |
| 28 | $0.03 | 118853 |
| 29 | $0.03 | 119541 |
| 30 | $0.03 | 120269 |
| 31 | $0.03 | 120694 |
| 32 | $0.03 | 121833 |
| 33 | $0.03 | 122508 |
| 34 | $0.03 | 123309 |
| 35 | $0.03 | 123772 |
| 36 | $0.03 | 124024 |
| 37 | $0.03 | 124627 |
| 38 | $0.03 | 125197 |
| 39 | $0.03 | 126090 |
| 40 | $0.03 | 127016 |
| 41 | $0.06 | 131615 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 20 | 18 | 1 | 2 | 697 | 16152 | 15311 | 0.05 |
| red | 2 | 1 | 0 | 0 | 67 | 39 | 8 | 16 | 3440 | 215512 | 53408 | 0.19 |
| green | 2 | 1 | 0 | 0 | 94 | 33 | 12 | 20 | 2771 | 289154 | 31629 | 0.14 |
| refactor | 1 | 0 | 0 | 0 | 5 | 3 | 2 | 4 | 138 | 48458 | 13803 | 0.04 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 3 | 3 | 0 | 0 | 99 | 39 | 8 | 16 | 3046 | 204454 | 45644 | 0.17 |
| developer | claude-sonnet-5-5 | 3 | 0 | 0 | 0 | 87 | 54 | 15 | 26 | 4000 | 364822 | 68507 | 0.25 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| wait-ci | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| When a step's frozen record holds two titles missing at HEAD and the file holds two new cases (in the opposite file order) whose bodies match neither recorded body digest, rerecording the committed record (via tick-ledger.sh --refactor-pending, a process case in skills/tdd/scripts/tests/py/test_tick_ledger_process.py) exits 2 with stderr naming the record file and an unpaired title, and leaves the record file byte-for-byte unchanged, never pairing a title with a case by file position ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 75 | 22 | 40 | 6349 | 553124 | 98840 | 0.37 | 399 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| When a step's frozen record holds two titles missing at HEAD and the file holds two new cases (in the opposite file order) whose bodies match neither recorded body digest, rerecording the committed record (via tick-ledger.sh --refactor-pending, a process case in skills/tdd/scripts/tests/py/test_tick_ledger_process.py) exits 2 with stderr naming the record file and an unpaired title, and leaves the record file byte-for-byte unchanged, never pairing a title with a case by file position ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 5 | 0.04 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 2 | 3 | 9 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 19 | 19 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 1 | 2 | 2 | 2 | 2 | 3 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 2 | 0 | 2 | 2 | 2 | 2 | 2 | 3 | 2 | 2 | 2 | 2 | 2 | 2 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 23 | 42 | 7046 | 569276 | 114151 | 2.23 (estimate) |
