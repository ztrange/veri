### 📊 Metrics — issue 486

Wall time for the issue: 7875 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/510.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 24 | 19 | 2 | 4 | 1936 | 57351 | 36551 | 0.34 |
| red | 14 | 7 | 0 | 0 | 694 | 518 | 125 | 242 | 48878 | 6373490 | 692328 | 7.79 |
| green | 18 | 7 | 2 | 0 | 2664 | 661 | 180 | 360 | 62443 | 8595433 | 712731 | 8.67 |
| refactor | 20 | 7 | 3 | 0 | 3544 | 633 | 168 | 330 | 61168 | 7794713 | 848670 | 9.57 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 1787 | 3.55 | 0 | 0.00 |
| refactor | 3178 | 5.59 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| event.sh writes an awake-clock reading on every event it appends, taken from the clock VERI_AWAKE_CLOCK names when set and otherwise from the same sleep-excluding clock supervise.sh uses for its windows ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 276 | 66 | 128 | 26658 | 3037680 | 353841 | 3.97 | 936 | 1/2 | 0/5 | structural-owed |
| supervise.sh's per-attempt secs on its exit event is the difference of two awake-clock readings, so a wall-clock jump the awake clock does not make is not counted ⟦criterion 6⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 214 | 59 | 116 | 19572 | 2682513 | 334664 | 3.61 | 1063 | 1/2 | 0/5 | nothing-left |
| metrics.sh's issue wall, given a log whose wall timestamps span a gap its awake-clock readings do not, excludes the gap and a figure beside it names the excluded seconds ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 204 | 58 | 114 | 19946 | 2792974 | 270626 | 3.12 | 355 | unknown | 1/5 | nothing-left |
| metrics.sh computes each step's wall from the awake-clock readings of its step-start and step-done events, so a sleep gap inside a step is not counted in that step's wall ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 198 | 55 | 110 | 19511 | 2679662 | 267729 | 3.07 | 445 | unknown | 1/5 | nothing-left |
| metrics.sh computes each phase's wall from awake-clock readings, so a sleep gap inside a leaf's attempt is not counted in that phase's wall ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 210 | 56 | 110 | 19515 | 2717842 | 274190 | 3.13 | 359 | unknown | 1/5 | nothing-left |
| metrics.sh, given a log with no awake-clock readings at all, prints every figure as the wall-clock one it prints today and says in its output that the figures are wall-clock ⟦criterion 4⟧ | 10 | 3 | 2 | 0 | 0 | 0 | 381 | 96 | 190 | 34829 | 4572100 | 399316 | 4.81 | 3278 | 2/2 | 2/5 | nothing-left |
| metrics.sh, given a log where only some events carry an awake-clock reading, prints no figure computed from a mix of the two clocks and says which clock its figures are on ⟦criterion 5⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 329 | 83 | 164 | 32458 | 4280865 | 353363 | 4.33 | 969 | 1/2 | 2/5 | nothing-left |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 2 | 2 | 2 | 0 | 2 | 30 | 0 | 2 | 2 | 2 | 31 | 31 | 32 | 33 | 33 | 33 | 3 | 3 | 3 | 15 | 4 | 3 | 3 | 0 | 4 | 3 | 0 | 55 | 56 | 3 | 4 | 0 | 4 | 4 | 3 | 4 | 4 | 3 | 0 | 3 | 4 | 4 | 3 | 4 | 4 | 0 | 4 | 4 | 0 | 4 | 4 | 4 | 5 | 4 | 4 | 4 | 4 | 4 | 4 | 4 |
| fast | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 4 | 4 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 2 | 32 | 4 | 3 | 4 | 4 | 3 | 4 | 4 | 4 | 4 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 419 | 429 | 431 | 429 | 426 | 428 | 427 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 475 | 936 | 174425 | 22820987 | 2290280 | 26.38 |
