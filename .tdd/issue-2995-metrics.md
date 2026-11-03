### 📊 Metrics — issue 2995

Wall time for the issue: 4227 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 5 planned.
Outcome: the run bailed — revise-impossible, a process failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $3.00 over 61 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 89838 tokens, largest 182695 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.58 | 89838 |
| 2 | $0.08 | 96982 |
| 3 | $0.03 | 98225 |
| 4 | $0.03 | 100115 |
| 5 | $0.03 | 101782 |
| 6 | $0.02 | 102235 |
| 7 | $0.02 | 102563 |
| 8 | $0.02 | 102948 |
| 9 | $0.03 | 103567 |
| 10 | $0.09 | 112218 |
| 11 | $0.05 | 115330 |
| 12 | $0.04 | 116860 |
| 13 | $0.03 | 117612 |
| 14 | $0.03 | 118174 |
| 15 | $0.03 | 118391 |
| 16 | $0.03 | 119118 |
| 17 | $0.03 | 120474 |
| 18 | $0.03 | 121295 |
| 19 | $0.03 | 122352 |
| 20 | $0.03 | 123095 |
| 21 | $0.03 | 124106 |
| 22 | $0.04 | 125854 |
| 23 | $0.04 | 127572 |
| 24 | $0.04 | 128827 |
| 25 | $0.03 | 129320 |
| 26 | $0.03 | 130389 |
| 27 | $0.04 | 132103 |
| 28 | $0.04 | 133461 |
| 29 | $0.03 | 134375 |
| 30 | $0.04 | 135461 |
| 31 | $0.03 | 136428 |
| 32 | $0.03 | 137346 |
| 33 | $0.03 | 138113 |
| 34 | $0.09 | 146204 |
| 35 | $0.05 | 148377 |
| 36 | $0.04 | 149318 |
| 37 | $0.03 | 149651 |
| 38 | $0.04 | 151292 |
| 39 | $0.04 | 152282 |
| 40 | $0.04 | 152995 |
| 41 | $0.04 | 153966 |
| 42 | $0.04 | 154643 |
| 43 | $0.04 | 155444 |
| 44 | $0.06 | 158625 |
| 45 | $0.03 | 158847 |
| 46 | $0.03 | 159200 |
| 47 | $0.04 | 160076 |
| 48 | $0.04 | 161382 |
| 49 | $0.04 | 162674 |
| 50 | $0.05 | 165380 |
| 51 | $0.04 | 166054 |
| 52 | $0.05 | 168773 |
| 53 | $0.04 | 169599 |
| 54 | $0.04 | 169871 |
| 55 | $0.05 | 171528 |
| 56 | $0.04 | 172439 |
| 57 | $0.04 | 173274 |
| 58 | $0.05 | 175126 |
| 59 | $0.04 | 175923 |
| 60 | $0.05 | 177991 |
| 61 | $0.07 | 182695 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 23 | 17 | 1 | 2 | 1289 | 17154 | 14244 | 0.05 |
| red | 8 | 2 | 0 | 0 | 717 | 218 | 44 | 78 | 21986 | 1140555 | 209721 | 1.19 |
| green | 7 | 1 | 2 | 0 | 1596 | 149 | 40 | 78 | 14559 | 1196883 | 117053 | 0.74 |
| red-contradicted | 1 | 0 | 0 | 0 | 69 | 30 | 7 | 14 | 3581 | 231457 | 23666 | 0.12 |
| refactor | 2 | 1 | 0 | 0 | 196 | 27 | 9 | 18 | 1885 | 237048 | 47196 | 0.16 |
| pin | 4 | 2 | 2 | 0 | 225 | 86 | 16 | 32 | 6134 | 448793 | 50332 | 0.23 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 11 | 7 | 4 | 0 | 1747 | 204 | 43 | 86 | 16866 | 1229300 | 137415 | 0.64 |
| developer | claude-sonnet-5-5 | 4 | 0 | 0 | 0 | 209 | 90 | 22 | 42 | 8870 | 631610 | 96132 | 0.39 |
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

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A run an earlier watch-runs.sh saw live, whose conductor exited after that watch returned and before the next one started, is reported by the next watch-runs.sh at its start with its `exited <n> <state>` line and exit 0 (in-process case in tests/py/unit/test_watch_runs.py; the record of runs seen live persists between watches under the main working tree's `.tdd/` as status.main_working_tree() names it, so a case places it in its tmp_path; every existing case stays green unchanged) ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 196 | 0.16 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 10 | 31 | 37 | 27 | 32 | 31 | 29 | 27 | 32 | 34 | 32 | 30 | 29 | 9 | 34 | 9 | 7 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 59 | 87 | 80 | 107 | 78 | 84 | 94 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 8 | 11 | 8 | 12 | 40 | 9 | 23 | 6 | 9 | 7 | 6 | 8 | 11 | 10 | 10 | 9 | 9 | 7 | 10 | 10 | 10 | 7 | 8 | 10 | 8 | 9 | 10 | 9 | 10 | 10 | 10 | 7 | 9 | 11 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 117 | 222 | 49434 | 3271890 | 462212 | 5.48 (estimate) |
