### 📊 Metrics — issue 2663

Wall time for the issue: 2406 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2670.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.95 over 47 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 85357 tokens, largest 129827 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.54 | 85357 |
| 2 | $0.07 | 92166 |
| 3 | $0.03 | 93120 |
| 4 | $0.03 | 95071 |
| 5 | $0.02 | 95688 |
| 6 | $0.02 | 96366 |
| 7 | $0.02 | 96626 |
| 8 | $0.02 | 96860 |
| 9 | $0.02 | 97147 |
| 10 | $0.02 | 97764 |
| 11 | $0.03 | 98713 |
| 12 | $0.03 | 99849 |
| 13 | $0.03 | 101003 |
| 14 | $0.02 | 101312 |
| 15 | $0.03 | 101992 |
| 16 | $0.02 | 102545 |
| 17 | $0.03 | 103383 |
| 18 | $0.08 | 110970 |
| 19 | $0.04 | 113379 |
| 20 | $0.03 | 114038 |
| 21 | $0.02 | 114273 |
| 22 | $0.03 | 114864 |
| 23 | $0.03 | 115265 |
| 24 | $0.03 | 116594 |
| 25 | $0.03 | 117288 |
| 26 | $0.03 | 117606 |
| 27 | $0.03 | 118047 |
| 28 | $0.03 | 118370 |
| 29 | $0.03 | 119463 |
| 30 | $0.03 | 120316 |
| 31 | $0.03 | 120887 |
| 32 | $0.03 | 121140 |
| 33 | $0.03 | 121821 |
| 34 | $0.04 | 123261 |
| 35 | $0.03 | 124120 |
| 36 | $0.03 | 124920 |
| 37 | $0.03 | 125692 |
| 38 | $0.03 | 126535 |
| 39 | $0.03 | 127041 |
| 40 | $0.03 | 127464 |
| 41 | $0.03 | 127649 |
| 42 | $0.03 | 127934 |
| 43 | $0.03 | 128685 |
| 44 | $0.03 | 128892 |
| 45 | $0.03 | 129153 |
| 46 | $0.03 | 129519 |
| 47 | $0.03 | 129827 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 6 | 1 | 2 | 686 | 0 | 31439 | 0.09 |
| red | 4 | 1 | 0 | 0 | 198 | 65 | 20 | 40 | 7969 | 601788 | 92910 | 0.37 |
| pin | 2 | 2 | 0 | 0 | 45 | 19 | 7 | 14 | 1979 | 186524 | 30889 | 0.12 |
| green | 2 | 1 | 0 | 0 | 186 | 24 | 10 | 20 | 2332 | 284086 | 29766 | 0.13 |
| refactor | 1 | 0 | 0 | 0 | 7 | 3 | 2 | 4 | 134 | 48445 | 13599 | 0.04 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 5 | 5 | 0 | 0 | 206 | 42 | 15 | 30 | 4340 | 373560 | 91705 | 0.31 |
| developer | claude-sonnet-5-5 | 5 | 0 | 0 | 0 | 240 | 75 | 25 | 50 | 8760 | 747283 | 106898 | 0.43 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `check --step` on a step carrying `⟦guard-subject: <path>⟧` still exits 1 naming a recorded test file that the marker does not name and whose content changed since the record (pin: already holds) ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 38 | 11 | 22 | 4633 | 328227 | 55422 | 0.22 | unknown | unknown | unknown | unknown |  |  | pin |
| `check --step` exits 1 naming a recorded guard-subject file (the file the step's `⟦guard-subject: <path>⟧` marker names, captured by the record) that was deleted since the record, as an unrecorded deleted guard subject does (pin: already holds) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 26 | 9 | 18 | 3145 | 266367 | 35379 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |
| `check --step` exempts a recorded guard-subject file whose content changed since the record: with the file the step's `⟦guard-subject: <path>⟧` marker names captured by the record and then edited, it exits 0 and prints nothing ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 47 | 19 | 38 | 4636 | 526249 | 76363 | 0.29 | 413 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `check --step` exempts a recorded guard-subject file whose content changed since the record: with the file the step's `⟦guard-subject: <path>⟧` marker names captured by the record and then edited, it exits 0 and prints nothing ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.04 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 27 | 12 | 11 | 12 | 16 | 19 |
| target | 4 | 4 | 2 | 3 | 19 |  |
| fast | 34 | 33 |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 40 | 80 | 13100 | 1120843 | 198603 | 2.69 (estimate) |
