### 📊 Metrics — issue 2145

Wall time for the issue: 1801 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2162.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $3.31 over 73 turns, in 2 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 86238 |
| 2 | $0.03 | 87400 |
| 3 | $0.05 | 89518 |
| 4 | $0.02 | 89908 |
| 5 | $0.03 | 90275 |
| 6 | $0.03 | 90682 |
| 7 | $0.03 | 91037 |
| 8 | $0.02 | 91325 |
| 9 | $0.03 | 91733 |
| 10 | $0.03 | 92177 |
| 11 | $0.03 | 92970 |
| 12 | $0.03 | 93448 |
| 13 | $0.55 | 86205 |
| 14 | $0.02 | 86647 |
| 15 | $0.03 | 88522 |
| 16 | $0.02 | 88857 |
| 17 | $0.02 | 89651 |
| 18 | $0.02 | 90269 |
| 19 | $0.02 | 90820 |
| 20 | $0.02 | 91436 |
| 21 | $0.02 | 92262 |
| 22 | $0.02 | 93030 |
| 23 | $0.06 | 98037 |
| 24 | $0.03 | 99090 |
| 25 | $0.02 | 99392 |
| 26 | $0.03 | 100200 |
| 27 | $0.02 | 100773 |
| 28 | $0.02 | 101269 |
| 29 | $0.02 | 101727 |
| 30 | $0.03 | 103153 |
| 31 | $0.03 | 104140 |
| 32 | $0.02 | 104502 |
| 33 | $0.03 | 105231 |
| 34 | $0.03 | 105996 |
| 35 | $0.03 | 106697 |
| 36 | $0.03 | 108201 |
| 37 | $0.03 | 108978 |
| 38 | $0.08 | 116257 |
| 39 | $0.03 | 117393 |
| 40 | $0.03 | 118492 |
| 41 | $0.03 | 119303 |
| 42 | $0.03 | 119936 |
| 43 | $0.03 | 120688 |
| 44 | $0.03 | 121453 |
| 45 | $0.03 | 122216 |
| 46 | $0.04 | 123559 |
| 47 | $0.03 | 124287 |
| 48 | $0.03 | 125208 |
| 49 | $0.03 | 125911 |
| 50 | $0.03 | 126907 |
| 51 | $0.03 | 127999 |
| 52 | $0.03 | 128786 |
| 53 | $0.04 | 130028 |
| 54 | $0.03 | 130680 |
| 55 | $0.03 | 131376 |
| 56 | $0.03 | 132451 |
| 57 | $0.03 | 132875 |
| 58 | $0.03 | 133155 |
| 59 | $0.03 | 133514 |
| 60 | $0.03 | 134011 |
| 61 | $0.03 | 134478 |
| 62 | $0.03 | 134937 |
| 63 | $0.03 | 135322 |
| 64 | $0.03 | 136093 |
| 65 | $0.03 | 136946 |
| 66 | $0.03 | 137829 |
| 67 | $0.03 | 138558 |
| 68 | $0.03 | 139294 |
| 69 | $0.03 | 139923 |
| 70 | $0.03 | 140470 |
| 71 | $0.03 | 140928 |
| 72 | $0.03 | 141271 |
| 73 | $0.03 | 141636 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 22 | 19 | 1 | 2 | 861 | 0 | 29984 | 0.08 |
| red | 4 | 2 | 0 | 0 | 165 | 87 | 19 | 38 | 7983 | 591645 | 85181 | 0.35 |
| green | 6 | 2 | 1 | 0 | 472 | 151 | 35 | 70 | 10633 | 1014754 | 101879 | 0.59 |
| refactor | 4 | 2 | 0 | 0 | 157 | 67 | 14 | 26 | 3196 | 319525 | 74977 | 0.25 |
| cover | 1 | 0 | 0 | 0 | 45 | 18 | 5 | 10 | 1585 | 116383 | 30585 | 0.10 |
| predicate | 1 | 0 | 0 | 0 | 15 | 9 | 3 | 6 | 352 | 72763 | 10261 | 0.04 |
| structural | 1 | 0 | 0 | 0 | 22 | 6 | 4 | 8 | 779 | 103100 | 11770 | 0.05 |
| transform | 1 | 1 | 0 | 0 | 33 | 16 | 4 | 8 | 928 | 84317 | 29506 | 0.09 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 9 | 8 | 1 | 0 | 472 | 162 | 32 | 64 | 10079 | 807487 | 149334 | 0.56 |
| developer | claude-sonnet-5-5 | 8 | 0 | 0 | 0 | 303 | 145 | 38 | 74 | 12064 | 1045515 | 171596 | 0.65 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 156 | 66 | 15 | 30 | 4174 | 449485 | 53213 | 0.35 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 350 | 0.46 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| cover | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| While every pending check run of the head commit is still `queued` (none `in_progress`), wait-ci.sh records no `<total-seconds>` deadline and keeps answering 3 at the end of each slice, even past where the old deadline would have run out; the deadline is recorded from the first call that sees a check `in_progress` for that head, and a later call that finds the checks finished answers 0 — pinned in-process in tests/py/unit/test_wait_ci.py with a fake clock and a faked rollup ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 220 | 45 | 90 | 14444 | 1319970 | 166355 | 0.82 | 675 | 1/2 | 1/5 | nothing-structural |  |  | full |
| A head whose pending check runs stay `queued` (none ever `in_progress`) for more than `VERI_CI_QUEUE_WAIT` seconds (default 3600) since the first call that saw them queued makes wait-ci.sh exit 2 with a stderr line saying the checks never started — pinned in-process in tests/py/unit/test_wait_ci.py with a fake clock and a faked rollup, for both the default and a set `VERI_CI_QUEUE_WAIT` ⟦criterion 1⟧ | 10 | 4 | 0 | 0 | 0 | 0 | 134 | 39 | 76 | 11012 | 982517 | 177804 | 0.65 | 375 | unknown | 0/5 | structural-owed |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| While every pending check run of the head commit is still `queued` (none `in_progress`), wait-ci.sh records no `<total-seconds>` deadline and keeps answering 3 at the end of each slice, even past where the old deadline would have run out; the deadline is recorded from the first call that sees a check `in_progress` for that head, and a later call that finds the checks finished answers 0 — pinned in-process in tests/py/unit/test_wait_ci.py with a fake clock and a faked rollup ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 97 | 0.15 |
| A head whose pending check runs stay `queued` (none ever `in_progress`) for more than `VERI_CI_QUEUE_WAIT` seconds (default 3600) since the first call that saw them queued makes wait-ci.sh exit 2 with a stderr line saying the checks never started — pinned in-process in tests/py/unit/test_wait_ci.py with a fake clock and a faked rollup, for both the default and a set `VERI_CI_QUEUE_WAIT` ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 60 | 0.10 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/10 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 11 | 11 | 11 | 13 | 11 | 11 | 14 | 11 | 13 | 11 | 13 | 12 | 11 | 10 | 11 | 11 | 11 | 12 |
| fast | 17 | 17 | 17 | 17 | 20 | 18 | 18 | 17 |  |  |  |  |  |  |  |  |  |  |
| target | 11 | 11 | 10 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 85 | 168 | 26317 | 2302487 | 374143 | 1.55 |
