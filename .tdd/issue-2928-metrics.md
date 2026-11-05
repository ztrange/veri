### 📊 Metrics — issue 2928

Wall time for the issue: 3310 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/3067.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $6.29 over 118 turns, in 2 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 90295 tokens, largest 171220 tokens
Conductor context: first turn 90342 tokens, largest 173293 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.59 | 90295 |
| 2 | $0.09 | 97368 |
| 3 | $0.04 | 98973 |
| 4 | $0.04 | 100879 |
| 5 | $0.05 | 102743 |
| 6 | $0.03 | 103050 |
| 7 | $0.04 | 103467 |
| 8 | $0.03 | 103732 |
| 9 | $0.03 | 104036 |
| 10 | $0.04 | 104301 |
| 11 | $0.03 | 104935 |
| 12 | $0.05 | 106724 |
| 13 | $0.04 | 107562 |
| 14 | $0.04 | 109513 |
| 15 | $0.04 | 109989 |
| 16 | $0.03 | 110361 |
| 17 | $0.04 | 110969 |
| 18 | $0.04 | 111536 |
| 19 | $0.03 | 112121 |
| 20 | $0.04 | 112520 |
| 21 | $0.16 | 127933 |
| 22 | $0.03 | 128262 |
| 23 | $0.05 | 128968 |
| 24 | $0.04 | 129623 |
| 25 | $0.03 | 129873 |
| 26 | $0.05 | 130485 |
| 27 | $0.04 | 131329 |
| 28 | $0.04 | 132251 |
| 29 | $0.11 | 140645 |
| 30 | $0.04 | 141757 |
| 31 | $0.05 | 142704 |
| 32 | $0.04 | 143538 |
| 33 | $0.05 | 143903 |
| 34 | $0.04 | 144539 |
| 35 | $0.05 | 145254 |
| 36 | $0.04 | 145947 |
| 37 | $0.04 | 146647 |
| 38 | $0.05 | 147155 |
| 39 | $0.04 | 147978 |
| 40 | $0.05 | 148738 |
| 41 | $0.05 | 150337 |
| 42 | $0.05 | 151265 |
| 43 | $0.05 | 152210 |
| 44 | $0.05 | 153168 |
| 45 | $0.04 | 153789 |
| 46 | $0.05 | 154122 |
| 47 | $0.05 | 155206 |
| 48 | $0.05 | 156579 |
| 49 | $0.04 | 157292 |
| 50 | $0.05 | 157900 |
| 51 | $0.05 | 158831 |
| 52 | $0.05 | 159818 |
| 53 | $0.05 | 160814 |
| 54 | $0.05 | 161689 |
| 55 | $0.05 | 163233 |
| 56 | $0.06 | 164605 |
| 57 | $0.08 | 169367 |
| 58 | $0.05 | 170299 |
| 59 | $0.05 | 171220 |
| 60 | $0.58 | 90342 |
| 61 | $0.08 | 97590 |
| 62 | $0.03 | 99331 |
| 63 | $0.03 | 101189 |
| 64 | $0.06 | 106498 |
| 65 | $0.06 | 111285 |
| 66 | $0.05 | 115352 |
| 67 | $0.03 | 116116 |
| 68 | $0.03 | 116586 |
| 69 | $0.03 | 116985 |
| 70 | $0.03 | 117451 |
| 71 | $0.03 | 117780 |
| 72 | $0.03 | 118131 |
| 73 | $0.03 | 118848 |
| 74 | $0.03 | 119454 |
| 75 | $0.10 | 129120 |
| 76 | $0.03 | 130200 |
| 77 | $0.04 | 131604 |
| 78 | $0.03 | 132502 |
| 79 | $0.03 | 133070 |
| 80 | $0.03 | 133502 |
| 81 | $0.03 | 134159 |
| 82 | $0.03 | 134919 |
| 83 | $0.04 | 136385 |
| 84 | $0.03 | 137223 |
| 85 | $0.03 | 137963 |
| 86 | $0.04 | 138907 |
| 87 | $0.09 | 147236 |
| 88 | $0.04 | 148120 |
| 89 | $0.04 | 148886 |
| 90 | $0.04 | 149792 |
| 91 | $0.04 | 150657 |
| 92 | $0.04 | 151633 |
| 93 | $0.04 | 152769 |
| 94 | $0.04 | 153557 |
| 95 | $0.04 | 154395 |
| 96 | $0.04 | 155693 |
| 97 | $0.04 | 157008 |
| 98 | $0.04 | 157698 |
| 99 | $0.04 | 158563 |
| 100 | $0.04 | 159016 |
| 101 | $0.04 | 160637 |
| 102 | $0.05 | 162730 |
| 103 | $0.04 | 163663 |
| 104 | $0.05 | 165434 |
| 105 | $0.04 | 166136 |
| 106 | $0.04 | 167017 |
| 107 | $0.04 | 167994 |
| 108 | $0.04 | 168640 |
| 109 | $0.04 | 169181 |
| 110 | $0.04 | 170130 |
| 111 | $0.04 | 170491 |
| 112 | $0.04 | 170909 |
| 113 | $0.04 | 171243 |
| 114 | $0.04 | 171726 |
| 115 | $0.04 | 172036 |
| 116 | $0.04 | 172460 |
| 117 | $0.04 | 172781 |
| 118 | $0.04 | 173293 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 6 | 4 | 1 | 2 | 489 | 0 | 31733 | 0.08 |
| red | 13 | 4 | 1 | 0 | 539 | 252 | 63 | 126 | 24208 | 1862230 | 334445 | 1.62 |
| green | 12 | 4 | 2 | 0 | 1564 | 240 | 68 | 134 | 20784 | 2009915 | 214464 | 1.21 |
| refactor | 7 | 2 | 0 | 0 | 210 | 64 | 22 | 42 | 5277 | 511394 | 156301 | 0.49 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 14 | 11 | 3 | 0 | 1283 | 179 | 55 | 110 | 16833 | 1533045 | 229613 | 0.90 |
| developer | claude-sonnet-5-5 | 8 | 0 | 0 | 0 | 327 | 109 | 36 | 70 | 9568 | 990741 | 205618 | 0.71 |
| developer | claude-opus-5-5 | 11 | 0 | 0 | 0 | 709 | 272 | 63 | 124 | 24357 | 1859753 | 301712 | 1.80 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 174 | 0.55 | 0 | 0.00 |
| green | 1146 | 0.95 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| supervise.sh given a run-leaf.sh launch whose prompt file exists but is empty exits 2, writes a launch-refused event naming the leaf, and writes no launch event; pinned by one case ⟦criterion 1⟧ | 7 | 2 | 1 | 0 | 0 | 0 | 166 | 38 | 74 | 13018 | 1116562 | 169467 | 0.81 | 996 | 1/2 | 0/5 | nothing-left |  |  | full |
| supervise.sh given a run-leaf.sh launch whose prompt file does not exist exits 2, writes a launch-refused event naming the leaf, and writes no launch event; pinned by one case ⟦criterion 1⟧ | 11 | 2 | 2 | 0 | 0 | 0 | 175 | 50 | 100 | 17577 | 1422271 | 247895 | 1.18 | 2476 | green 1/2, red 1/2 | 0/5 | nothing-left |  |  | full |
| supervise.sh given a launch whose command is not run-leaf.sh and whose first argument is an empty existing file launches the leaf normally, writing a launch event and no launch-refused event: the empty-prompt refusal applies to run-leaf.sh launches only; pinned by one case ⟦criterion 2⟧ | 7 | 3 | 0 | 0 | 0 | 0 | 100 | 32 | 64 | 9918 | 918460 | 154502 | 0.68 | 648 | 1/2 | 1/5 | nothing-left |  |  | full |
| supervise.sh given a run-leaf.sh launch with no prompt argument exits 2 with a message naming the missing prompt argument on stderr, not a traceback; pinned by one case ⟦criterion 3⟧ | 7 | 3 | 0 | 0 | 0 | 0 | 115 | 33 | 64 | 9756 | 926246 | 133346 | 0.65 | 564 | 1/2 | 1/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| supervise.sh given a run-leaf.sh launch whose prompt file exists but is empty exits 2, writes a launch-refused event naming the leaf, and writes no launch event; pinned by one case ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 14 | 0.09 |
| supervise.sh given a run-leaf.sh launch whose prompt file does not exist exits 2, writes a launch-refused event naming the leaf, and writes no launch event; pinned by one case ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 23 | 0.18 |
| supervise.sh given a launch whose command is not run-leaf.sh and whose first argument is an empty existing file launches the leaf normally, writing a launch event and no launch-refused event: the empty-prompt refusal applies to run-leaf.sh launches only; pinned by one case ⟦criterion 2⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 86 | 0.12 |
| supervise.sh given a run-leaf.sh launch with no prompt argument exits 2 with a message naming the missing prompt argument on stderr, not a traceback; pinned by one case ⟦criterion 3⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 87 | 0.11 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 13 | 4 | 12 | 15 | 13 | 12 | 14 | 1 | 3 | 10 | 12 | 10 | 12 | 14 | 15 | 5 | 4 | 3 | 4 | 13 | 1 | 14 | 14 | 14 | 13 | 10 | 10 | 10 | 14 | 15 | 15 |
| fast | 64 | 43 | 45 | 29 | 32 | 36 | 31 | 33 | 37 | 43 | 30 | 30 | 36 | 29 | 29 | 36 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 5 | 3 | 4 | 4 | 4 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 154 | 304 | 50758 | 4383539 | 736943 | 9.70 (estimate) |
