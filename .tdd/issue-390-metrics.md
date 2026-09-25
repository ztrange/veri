### 📊 Metrics — issue 390

Wall time for the issue: 2336 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 6 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/468.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 7 | 1 | 2 | 515 | 11207 | 33824 | 0.28 |
| red | 10 | 4 | 0 | 0 | 495 | 361 | 96 | 190 | 34640 | 4718948 | 466050 | 5.37 |
| green | 10 | 4 | 1 | 0 | 827 | 286 | 73 | 146 | 27200 | 3247461 | 369674 | 4.15 |
| refactor | 8 | 4 | 0 | 0 | 323 | 215 | 65 | 128 | 19758 | 2936674 | 329949 | 3.62 |
| pin | 2 | 2 | 0 | 0 | 63 | 32 | 8 | 16 | 3075 | 303028 | 74347 | 0.72 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 513 | 1.46 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| status.sh renders a run whose log ends with a stop mark as `stopped <mode>`, and with STATUS_JSON/--json reports "state": "stopped" with the mode in a stop_mode key ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 177 | 50 | 98 | 16377 | 2304989 | 258871 | 2.86 | 375 | unknown | 1/5 | structural-owed |
| a resume mark after a stop mark makes status.sh render that run as running again ⟦criterion 2⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 236 | 64 | 128 | 22235 | 2991625 | 301123 | 3.45 | 783 | 1/2 | 2/5 | nothing-structural |
| metrics.sh prints an Outcome line naming the stop mode and the at boundary for a log whose ending mark is stop, and ends the issue wall at that stop mark ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 181 | 50 | 100 | 17495 | 2372485 | 262207 | 2.92 | 315 | unknown | 0/5 | nothing-left |
| a resume mark after a stop mark makes metrics.sh print the no-ending-mark Outcome for a run that has not ended since ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 179 | 47 | 92 | 16920 | 2079812 | 249581 | 2.75 | 305 | unknown | 1/5 | nothing-structural |
| classify-bail.sh exits 2 for stopped, stop, at-ledger, at-leaf and now ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 50 | 13 | 26 | 4818 | 569348 | 78282 | 0.84 | unknown | unknown | unknown | unknown |
| dashboard_endpoints.py run_ended answers false for a run whose log carries a stop mark and no done or bail ⟦criterion 6⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 71 | 18 | 36 | 6828 | 887852 | 89956 | 1.03 | unknown | unknown | unknown | unknown |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 7 | 7 | 8 | 18 | 8 | 0 | 7 | 7 | 0 | 8 | 8 | 8 | 8 | 8 | 0 | 8 | 8 | 8 | 8 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 0 | 4 | 0 | 0 | 11 |
| fast | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 2 | 2 | 2 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 8 | 8 | 8 | 3 | 3 | 3 | 0 | 0 | 10 | 11 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 290 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 243 | 482 | 85188 | 11217318 | 1273844 | 14.14 |
