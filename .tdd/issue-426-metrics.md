### 📊 Metrics — issue 426

Wall time for the issue: 5525 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/430.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 8 | 4 | 0 | 0 | 964 | 867 | 129 | 228 | 65653 | 7021442 | 474028 | 9.89 |
| green | 8 | 4 | 0 | 0 | 2330 | 1065 | 180 | 322 | 87097 | 11417397 | 506695 | 12.95 |
| refactor | 8 | 4 | 0 | 0 | 1457 | 819 | 138 | 256 | 66252 | 7429983 | 438460 | 9.76 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| A verdict launcher script runs verify.sh with the step title passed as an argument, so a title containing an apostrophe reaches the verifier intact ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 710 | 101 | 190 | 54245 | 5834482 | 348861 | 7.76 | 1345 | unknown | 2/5 | structural-owed |
| Every documented verifier launch line in SKILL.md invokes that verdict launcher rather than an inlined bash -c command string ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 952 | 145 | 244 | 77365 | 9713321 | 438569 | 11.18 | 2069 | unknown | 1/5 | structural-owed |
| A verdict launcher that cannot start the verifier records 2, the no-answer code, and never 1 ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 515 | 98 | 180 | 42128 | 4872110 | 313765 | 6.63 | 921 | unknown | 3/5 | structural-owed |
| The verdict launcher clears the phase reason file before the verifier runs, so a reason left by an earlier step can never be read as this verdict ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 574 | 103 | 192 | 45264 | 5448909 | 317988 | 7.04 | 847 | unknown | 4/5 | structural-owed |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 47 | 54 | 56 | 57 | 63 | 0 | 0 | 0 | 0 | 54 | 134 | 132 | 113 | 113 | 113 | 0 | 1 | 1 | 1 | 1 | 14 | 14 | 8 | 66 | 1 | 1 | 0 | 0 | 1 | 1 | 1 | 0 | 1 | 1 | 41 | 1 | 1 | 1 | 40 |
| fast | 2 | 2 | 3 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 2 | 2 | 1 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 0 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 447 | 806 | 219002 | 25868822 | 1419183 | 32.61 |
