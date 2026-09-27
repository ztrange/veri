### 📊 Metrics — issue 488

Wall time for the issue: 1349 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/516.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 22 | 17 | 4 | 8 | 1359 | 146944 | 38219 | 0.36 |
| red | 5 | 1 | 0 | 0 | 281 | 213 | 53 | 100 | 21251 | 2577686 | 247118 | 2.92 |
| green | 2 | 1 | 0 | 0 | 188 | 74 | 20 | 40 | 7163 | 944453 | 86070 | 1.02 |
| refactor | 2 | 1 | 0 | 0 | 90 | 52 | 14 | 28 | 4241 | 594365 | 76139 | 0.81 |
| pin | 3 | 3 | 0 | 0 | 112 | 64 | 15 | 30 | 6235 | 603758 | 117892 | 1.19 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| A step whose revise marks name more than one phase renders its `#### By step` revise cell as one `<phase> <used>/<budget>` entry per revised phase, rather than one step-wide total ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 200 | 54 | 106 | 18648 | 2540818 | 262471 | 2.98 | 487 | unknown | 1/5 | nothing-structural |
| A step that revised two phases once each under `REVISE_BUDGET` 2 renders each phase as `1/2`, with no count above the budget anywhere in its revise cell ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 68 | 14 | 26 | 6979 | 579899 | 84561 | 0.93 | unknown | unknown | unknown | unknown |
| A step that revised one phase `REVISE_BUDGET` times renders that phase as `<budget>/<budget>` in its revise cell ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 79 | 19 | 36 | 7900 | 899765 | 91282 | 1.07 | unknown | unknown | unknown | unknown |
| A step with no revise marks renders its revise cell exactly as today, the unknown placeholder ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 56 | 15 | 30 | 5363 | 699780 | 88905 | 0.96 | unknown | unknown | unknown | unknown |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 4 | 0 | 5 | 5 | 0 | 12 | 4 | 2 | 0 | 1 | 1 | 40 | 1 | 1 | 5 | 5 | 5 | 5 | 5 | 5 |
| fast | 4 | 3 | 4 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 106 | 206 | 40249 | 4867206 | 565438 | 6.30 |
