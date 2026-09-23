### 📊 Metrics — issue 428

Wall time for the issue: 1630 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/432.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 5 | 2 | 0 | 0 | 388 | 355 | 62 | 106 | 29580 | 2744365 | 245564 | 4.57 |
| green | 4 | 2 | 0 | 0 | 339 | 293 | 55 | 100 | 22087 | 2510046 | 182746 | 3.64 |
| refactor | 4 | 2 | 0 | 0 | 349 | 318 | 47 | 86 | 23320 | 2193100 | 192030 | 3.60 |
| pin | 1 | 1 | 0 | 0 | 37 | 33 | 10 | 18 | 2431 | 406019 | 39977 | 0.66 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| A PREDICTION line carrying a trailing clause after the verdict word is read as that verdict ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 411 | 72 | 132 | 30824 | 3326714 | 280617 | 5.24 | 578 | unknown | 2/5 | structural-owed |
| A PREDICTION line with no recognisable verdict word is still exit 2 ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 115 | 24 | 42 | 9070 | 1015239 | 87185 | 1.61 | unknown | unknown | unknown | unknown |
| The leaf prompt and the parser state the same contract, and a test pins that they agree ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 473 | 78 | 136 | 37524 | 3511577 | 292515 | 5.62 | 592 | unknown | 1/5 | nothing-structural |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 1 | 2 | 4 | 0 | 1 |
| fast | 2 | 2 | 2 | 2 | 2 | 2 | 3 |  |  |  |  |  |  |  |  |
| target | 0 | 1 | 0 | 1 |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 174 | 310 | 77418 | 7853530 | 660317 | 12.47 |
