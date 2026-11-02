### 📊 Metrics — issue 2825

Wall time for the issue: 638 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: unknown of 2 planned.
Outcome: the run bailed — step-added-off-route, a process failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.46 over 21 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87200 tokens, largest 142103 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 87200 |
| 2 | $0.07 | 94256 |
| 3 | $0.03 | 95269 |
| 4 | $0.04 | 97531 |
| 5 | $0.02 | 98113 |
| 6 | $0.06 | 103289 |
| 7 | $0.02 | 103593 |
| 8 | $0.02 | 103863 |
| 9 | $0.02 | 104127 |
| 10 | $0.02 | 104548 |
| 11 | $0.04 | 106770 |
| 12 | $0.14 | 121261 |
| 13 | $0.04 | 123620 |
| 14 | $0.04 | 125973 |
| 15 | $0.05 | 128609 |
| 16 | $0.08 | 134962 |
| 17 | $0.03 | 135853 |
| 18 | $0.04 | 137394 |
| 19 | $0.03 | 138238 |
| 20 | $0.05 | 140604 |
| 21 | $0.04 | 142103 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER haiku, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-haiku-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 9 | 6 | 1 | 2 | 721 | 0 | 30423 | 0.08 |
| red | 2 | 1 | 0 | 0 | 179 | 102 | 21 | 36 | 20873 | 946165 | 97324 | 0.08 |
| green | 2 | 1 | 0 | 0 | 285 | 52 | 19 | 32 | 9110 | 569347 | 45446 | 0.08 |
| refactor | 1 | 0 | 0 | 0 | 44 | 41 | 9 | 14 | 8503 | 233814 | 23977 | 0.01 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 3 | 3 | 0 | 0 | 240 | 26 | 10 | 18 | 2794 | 216368 | 60735 | 0.20 |
| developer | claude-haiku-5-5 | 3 | 0 | 0 | 0 | 277 | 175 | 40 | 66 | 36413 | 1532958 | 136435 | 0.05 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 179 | 0.08 |
| green | 0 | 0.00 | 285 | 0.08 |
| refactor | 0 | 0.00 | 44 | 0.01 |
| develop-green | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `tests-frozen.sh rerecord-rebased` given an earlier step's frozen record whose case title is missing at HEAD exits 2 with no traceback and no `KeyError`, its stderr naming the record file and the missing title, and rewrites no record ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 195 | 49 | 82 | 38486 | 1749326 | 166747 | 0.17 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s |
| --- | ---: | ---: | ---: | ---: | ---: |
| affected | 8 | 7 | 7 | 6 | 40 |
| fast | 56 | 52 |  |  |  |
| target | 6 |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 50 | 84 | 39207 | 1749326 | 197170 | 1.71 (estimate) |
