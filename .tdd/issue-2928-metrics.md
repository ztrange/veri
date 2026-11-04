### 📊 Metrics — issue 2928

Wall time for the issue: 2770 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 2 planned.
Outcome: the run bailed — revise-impossible, a process failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.71 over 57 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 90295 tokens, largest 169367 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.58 | 90295 |
| 2 | $0.07 | 97368 |
| 3 | $0.03 | 98973 |
| 4 | $0.04 | 100879 |
| 5 | $0.04 | 102743 |
| 6 | $0.02 | 103050 |
| 7 | $0.02 | 103467 |
| 8 | $0.02 | 103732 |
| 9 | $0.02 | 104036 |
| 10 | $0.02 | 104301 |
| 11 | $0.03 | 104935 |
| 12 | $0.04 | 106724 |
| 13 | $0.03 | 107562 |
| 14 | $0.04 | 109513 |
| 15 | $0.03 | 109989 |
| 16 | $0.02 | 110361 |
| 17 | $0.03 | 110969 |
| 18 | $0.03 | 111536 |
| 19 | $0.03 | 112121 |
| 20 | $0.03 | 112520 |
| 21 | $0.15 | 127933 |
| 22 | $0.03 | 128262 |
| 23 | $0.03 | 128968 |
| 24 | $0.03 | 129623 |
| 25 | $0.03 | 129873 |
| 26 | $0.03 | 130485 |
| 27 | $0.03 | 131329 |
| 28 | $0.03 | 132251 |
| 29 | $0.09 | 140645 |
| 30 | $0.04 | 141757 |
| 31 | $0.04 | 142704 |
| 32 | $0.04 | 143538 |
| 33 | $0.03 | 143903 |
| 34 | $0.03 | 144539 |
| 35 | $0.03 | 145254 |
| 36 | $0.03 | 145947 |
| 37 | $0.03 | 146647 |
| 38 | $0.03 | 147155 |
| 39 | $0.04 | 147978 |
| 40 | $0.04 | 148738 |
| 41 | $0.04 | 150337 |
| 42 | $0.04 | 151265 |
| 43 | $0.04 | 152210 |
| 44 | $0.04 | 153168 |
| 45 | $0.04 | 153789 |
| 46 | $0.03 | 154122 |
| 47 | $0.04 | 155206 |
| 48 | $0.04 | 156579 |
| 49 | $0.04 | 157292 |
| 50 | $0.04 | 157900 |
| 51 | $0.04 | 158831 |
| 52 | $0.04 | 159818 |
| 53 | $0.04 | 160814 |
| 54 | $0.04 | 161689 |
| 55 | $0.04 | 163233 |
| 56 | $0.04 | 164605 |
| 57 | $0.07 | 169367 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 6 | 4 | 1 | 2 | 489 | 0 | 31733 | 0.08 |
| red | 7 | 2 | 1 | 0 | 277 | 126 | 33 | 66 | 12675 | 986288 | 169723 | 0.78 |
| green | 8 | 2 | 2 | 0 | 1146 | 184 | 49 | 96 | 15985 | 1459283 | 151160 | 0.95 |
| refactor | 2 | 0 | 0 | 0 | 29 | 24 | 4 | 8 | 1327 | 62086 | 64582 | 0.18 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 5 | 3 | 0 | 826 | 122 | 34 | 68 | 11680 | 980705 | 121690 | 0.52 |
| developer | claude-sonnet-5-5 | 3 | 0 | 0 | 0 | 73 | 51 | 12 | 24 | 4143 | 339205 | 110403 | 0.35 |
| developer | claude-opus-5-5 | 7 | 0 | 0 | 0 | 559 | 165 | 41 | 80 | 14653 | 1187747 | 185105 | 1.12 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 174 | 0.55 |
| green | 676 | 0.49 | 470 | 0.46 |
| refactor | 0 | 0.00 | 15 | 0.09 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| supervise.sh given a run-leaf.sh launch whose prompt file exists but is empty exits 2, writes a launch-refused event naming the leaf, and writes no launch event; pinned by one case ⟦criterion 1⟧ | 7 | 2 | 1 | 0 | 0 | 0 | 166 | 38 | 74 | 13018 | 1116562 | 169467 | 0.81 | 996 | 1/2 | 0/5 | nothing-left |  |  | full |
| supervise.sh given a run-leaf.sh launch whose prompt file does not exist exits 2, writes a launch-refused event naming the leaf, and writes no launch event; pinned by one case ⟦criterion 1⟧ | 10 | 2 | 2 | 0 | 0 | 0 | 168 | 48 | 96 | 16969 | 1391095 | 215998 | 1.09 | unknown | green 1/2, red 1/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| supervise.sh given a run-leaf.sh launch whose prompt file exists but is empty exits 2, writes a launch-refused event naming the leaf, and writes no launch event; pinned by one case ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 14 | 0.09 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 13 | 4 | 12 | 15 | 13 | 12 | 14 | 1 | 3 | 10 | 12 | 10 | 12 | 14 | 15 | 5 | 4 |
| fast | 64 | 43 | 45 | 29 | 32 | 36 | 31 | 33 | 37 | 43 |  |  |  |  |  |  |  |
| target | 5 | 3 | 4 | 4 |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 87 | 172 | 30476 | 2507657 | 417198 | 4.70 (estimate) |
