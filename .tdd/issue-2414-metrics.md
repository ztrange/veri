### 📊 Metrics — issue 2414

Wall time for the issue: 1636 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 1 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2450.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.80 over 45 turns, in 1 sessions, on opus.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 88487 tokens, largest 123858 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 88487 |
| 2 | $0.02 | 89033 |
| 3 | $0.02 | 89711 |
| 4 | $0.03 | 91395 |
| 5 | $0.02 | 92047 |
| 6 | $0.02 | 92463 |
| 7 | $0.02 | 92794 |
| 8 | $0.02 | 93078 |
| 9 | $0.02 | 93669 |
| 10 | $0.02 | 94418 |
| 11 | $0.02 | 95008 |
| 12 | $0.02 | 95636 |
| 13 | $0.02 | 96036 |
| 14 | $0.02 | 96668 |
| 15 | $0.02 | 97257 |
| 16 | $0.02 | 97762 |
| 17 | $0.02 | 98308 |
| 18 | $0.03 | 99680 |
| 19 | $0.03 | 100588 |
| 20 | $0.03 | 101199 |
| 21 | $0.03 | 102033 |
| 22 | $0.03 | 102780 |
| 23 | $0.03 | 103488 |
| 24 | $0.02 | 103754 |
| 25 | $0.03 | 104460 |
| 26 | $0.03 | 105063 |
| 27 | $0.03 | 106119 |
| 28 | $0.03 | 107049 |
| 29 | $0.09 | 115295 |
| 30 | $0.03 | 116201 |
| 31 | $0.03 | 117213 |
| 32 | $0.03 | 117972 |
| 33 | $0.03 | 118751 |
| 34 | $0.03 | 119436 |
| 35 | $0.03 | 119761 |
| 36 | $0.03 | 120979 |
| 37 | $0.03 | 121286 |
| 38 | $0.03 | 121643 |
| 39 | $0.03 | 121898 |
| 40 | $0.03 | 122228 |
| 41 | $0.03 | 122645 |
| 42 | $0.03 | 122877 |
| 43 | $0.03 | 123165 |
| 44 | $0.03 | 123539 |
| 45 | $0.03 | 123858 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 8 | 6 | 1 | 2 | 515 | 0 | 30786 | 0.08 |
| red | 2 | 1 | 0 | 0 | 30 | 23 | 8 | 14 | 2827 | 174627 | 51547 | 0.17 |
| green | 4 | 1 | 1 | 0 | 176 | 75 | 23 | 46 | 6363 | 647473 | 64398 | 0.40 |
| refactor | 1 | 0 | 0 | 0 | 6 | 4 | 3 | 4 | 325 | 48095 | 13833 | 0.04 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 4 | 3 | 1 | 0 | 115 | 54 | 17 | 32 | 4983 | 427560 | 63057 | 0.25 |
| developer | claude-sonnet-5-5 | 2 | 0 | 0 | 0 | 25 | 19 | 7 | 12 | 2243 | 145414 | 50931 | 0.16 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 80 | 35 | 11 | 22 | 2804 | 297221 | 46576 | 0.28 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 176 | 0.40 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| merge-lock.sh gate refuses a --pid value that is not a positive integer: `gate --pid -- true`, `gate --pid abc -- true` and `gate --keep --pid 0 -- true` each exit 2, print the gate usage line on stderr, run no command and create no .tdd/ directory, pinned by small in-process cases for those three argument lists ⟦criterion 1⟧ | 7 | 2 | 1 | 0 | 0 | 0 | 102 | 34 | 64 | 9515 | 870195 | 129778 | 0.61 | 365 | 1/2 | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| merge-lock.sh gate refuses a --pid value that is not a positive integer: `gate --pid -- true`, `gate --pid abc -- true` and `gate --keep --pid 0 -- true` each exit 2, print the gate usage line on stderr, run no command and create no .tdd/ directory, pinned by small in-process cases for those three argument lists ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 6 | 0.04 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 1 | 0 | 3 | 1 | 1 | 0 | 3 |
| fast | 18 | 18 | 17 | 18 |  |  |  |  |  |
| target | 0 | 1 |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 35 | 66 | 10030 | 870195 | 160564 | 0.70 |
