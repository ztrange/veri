### 📊 Metrics — issue 2995

Wall time for the issue: 629 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2996.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $5.43 over 96 turns, in 2 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 89838 tokens, largest 188913 tokens
Conductor context: first turn 89851 tokens, largest 125539 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.59 | 89838 |
| 2 | $0.09 | 96982 |
| 3 | $0.04 | 98225 |
| 4 | $0.05 | 100115 |
| 5 | $0.04 | 101782 |
| 6 | $0.04 | 102235 |
| 7 | $0.03 | 102563 |
| 8 | $0.04 | 102948 |
| 9 | $0.03 | 103567 |
| 10 | $0.11 | 112218 |
| 11 | $0.06 | 115330 |
| 12 | $0.04 | 116860 |
| 13 | $0.04 | 117612 |
| 14 | $0.04 | 118174 |
| 15 | $0.04 | 118391 |
| 16 | $0.04 | 119118 |
| 17 | $0.05 | 120474 |
| 18 | $0.04 | 121295 |
| 19 | $0.05 | 122352 |
| 20 | $0.04 | 123095 |
| 21 | $0.04 | 124106 |
| 22 | $0.06 | 125854 |
| 23 | $0.05 | 127572 |
| 24 | $0.04 | 128827 |
| 25 | $0.05 | 129320 |
| 26 | $0.04 | 130389 |
| 27 | $0.05 | 132103 |
| 28 | $0.05 | 133461 |
| 29 | $0.05 | 134375 |
| 30 | $0.05 | 135461 |
| 31 | $0.04 | 136428 |
| 32 | $0.05 | 137346 |
| 33 | $0.05 | 138113 |
| 34 | $0.10 | 146204 |
| 35 | $0.06 | 148377 |
| 36 | $0.05 | 149318 |
| 37 | $0.04 | 149651 |
| 38 | $0.06 | 151292 |
| 39 | $0.05 | 152282 |
| 40 | $0.04 | 152995 |
| 41 | $0.06 | 153966 |
| 42 | $0.04 | 154643 |
| 43 | $0.05 | 155444 |
| 44 | $0.07 | 158625 |
| 45 | $0.05 | 158847 |
| 46 | $0.04 | 159200 |
| 47 | $0.05 | 160076 |
| 48 | $0.06 | 161382 |
| 49 | $0.05 | 162674 |
| 50 | $0.07 | 165380 |
| 51 | $0.05 | 166054 |
| 52 | $0.07 | 168773 |
| 53 | $0.05 | 169599 |
| 54 | $0.05 | 169871 |
| 55 | $0.06 | 171528 |
| 56 | $0.05 | 172439 |
| 57 | $0.05 | 173274 |
| 58 | $0.06 | 175126 |
| 59 | $0.06 | 175923 |
| 60 | $0.06 | 177991 |
| 61 | $0.09 | 182695 |
| 62 | $0.09 | 188060 |
| 63 | $0.05 | 188913 |
| 64 | $0.59 | 89851 |
| 65 | $0.07 | 96833 |
| 66 | $0.03 | 98142 |
| 67 | $0.02 | 98667 |
| 68 | $0.03 | 100520 |
| 69 | $0.02 | 101046 |
| 70 | $0.02 | 101215 |
| 71 | $0.03 | 102192 |
| 72 | $0.05 | 105416 |
| 73 | $0.02 | 105837 |
| 74 | $0.03 | 107107 |
| 75 | $0.05 | 111199 |
| 76 | $0.03 | 111653 |
| 77 | $0.02 | 111916 |
| 78 | $0.03 | 112342 |
| 79 | $0.03 | 113107 |
| 80 | $0.04 | 114886 |
| 81 | $0.03 | 115619 |
| 82 | $0.03 | 116248 |
| 83 | $0.02 | 116436 |
| 84 | $0.03 | 117749 |
| 85 | $0.03 | 118658 |
| 86 | $0.05 | 121497 |
| 87 | $0.03 | 122028 |
| 88 | $0.03 | 122490 |
| 89 | $0.03 | 122879 |
| 90 | $0.03 | 123735 |
| 91 | $0.03 | 124172 |
| 92 | $0.03 | 124361 |
| 93 | $0.03 | 124895 |
| 94 | $0.03 | 125256 |
| 95 | $0.03 | 125539 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 23 | 17 | 1 | 2 | 1289 | 17154 | 14244 | 0.05 |
| red | 9 | 2 | 0 | 0 | 785 | 245 | 51 | 90 | 25265 | 1336009 | 232278 | 1.30 |
| green | 7 | 1 | 2 | 0 | 1596 | 149 | 40 | 78 | 14559 | 1196883 | 117053 | 0.74 |
| red-contradicted | 1 | 0 | 0 | 0 | 69 | 30 | 7 | 14 | 3581 | 231457 | 23666 | 0.12 |
| refactor | 2 | 1 | 0 | 0 | 196 | 27 | 9 | 18 | 1885 | 237048 | 47196 | 0.16 |
| pin | 5 | 3 | 2 | 0 | 265 | 98 | 19 | 38 | 7310 | 525224 | 64289 | 0.29 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 12 | 8 | 4 | 0 | 1787 | 216 | 46 | 92 | 18042 | 1305731 | 151372 | 0.69 |
| developer | claude-sonnet-5-5 | 5 | 0 | 0 | 0 | 277 | 117 | 29 | 54 | 12149 | 827064 | 118689 | 0.50 |
| developer | claude-opus-5-5 | 8 | 0 | 0 | 0 | 870 | 233 | 52 | 94 | 23698 | 1410980 | 228665 | 1.46 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 85 | 0.37 |
| green | 2794 | 1.17 | 0 | 0.00 |
| red-contradicted | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 116 | 0.09 | 51 | 0.06 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A run an earlier watch-runs.sh saw live, whose conductor exited after that watch returned and before the next one started, is reported by the next watch-runs.sh at its start with its `exited <n> <state>` line and exit 0 (in-process case in tests/py/unit/test_watch_runs.py; the record of runs seen live persists between watches under the main working tree's `.tdd/` as status.main_working_tree() names it, so a case places it in its tmp_path; every existing case stays green unchanged) ⟦criterion 1⟧ | 13 | 4 | 2 | 0 | 0 | 0 | 255 | 69 | 134 | 24879 | 2003778 | 238731 | 1.22 | 2937 | 2/2 | 1/5 | nothing-left |  |  | full |
| A run whose exit was reported by the watch that was running when it exited is not reported again by the next watch-runs.sh at its start (in-process case in tests/py/unit/test_watch_runs.py) ⟦criterion 2⟧ | 4 | 1 | 1 | 0 | 0 | 0 | 149 | 21 | 40 | 12577 | 590921 | 97668 | 0.63 | unknown | 1/2 | unknown | unknown |  |  | pin |
| A run whose exit a watch-runs.sh reported at its start is not reported again by a later watch-runs.sh at its start (in-process case in tests/py/unit/test_watch_runs.py) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 40 | 9 | 18 | 3855 | 261787 | 36989 | 0.16 | unknown | unknown | unknown | unknown |  |  | pin |
| A run an earlier watch saw live whose conductor is still live when the next watch-runs.sh starts is not reported as exited at that start: the watch keeps watching it (in-process case in tests/py/unit/test_watch_runs.py) ⟦criterion 3⟧ | 3 | 0 | 1 | 0 | 0 | 0 | 66 | 17 | 28 | 6834 | 398250 | 74580 | 0.43 | unknown | 1/2 | unknown | unknown |  |  | full |
| Runs 5 and 7 seen live by one watch-runs.sh; 7 exits between watches while 5 stays live; the next watch-runs.sh reports `exited 7` at its start and never `exited 5`, and keeps watching 5 (in-process case in tests/py/unit/test_watch_runs.py) ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 39 | 10 | 18 | 4455 | 271885 | 36514 | 0.16 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A run an earlier watch-runs.sh saw live, whose conductor exited after that watch returned and before the next one started, is reported by the next watch-runs.sh at its start with its `exited <n> <state>` line and exit 0 (in-process case in tests/py/unit/test_watch_runs.py; the record of runs seen live persists between watches under the main working tree's `.tdd/` as status.main_working_tree() names it, so a case places it in its tmp_path; every existing case stays green unchanged) ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 196 | 0.16 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 10 | 31 | 37 | 27 | 32 | 31 | 29 | 27 | 32 | 34 | 32 | 30 | 29 | 9 | 34 | 9 | 7 | 27 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 59 | 87 | 80 | 107 | 78 | 84 | 94 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 8 | 11 | 8 | 12 | 40 | 9 | 23 | 6 | 9 | 7 | 6 | 8 | 11 | 10 | 10 | 9 | 9 | 7 | 10 | 10 | 10 | 7 | 8 | 10 | 8 | 9 | 10 | 9 | 10 | 10 | 10 | 7 | 9 | 11 | 12 | 10 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 127 | 240 | 53889 | 3543775 | 498726 | 8.08 (estimate) |
