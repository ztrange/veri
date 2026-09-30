### 📊 Metrics — issue 585

Wall time for the issue: 2056 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/586.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 8 | 5 | 1 | 2 | 502 | 11731 | 25978 | 0.11 |
| red | 5 | 2 | 0 | 0 | 1127 | 119 | 35 | 68 | 12820 | 1358221 | 181262 | 1.13 |
| green | 2 | 1 | 0 | 0 | 89 | 44 | 15 | 28 | 4859 | 554822 | 70519 | 0.44 |
| refactor | 2 | 1 | 0 | 0 | 38 | 23 | 8 | 16 | 1711 | 273255 | 64537 | 0.33 |
| pin | 1 | 1 | 0 | 0 | 23 | 12 | 4 | 8 | 1350 | 134485 | 32051 | 0.17 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| metrics.sh renders a complete report when the log's only structural-pass mark has just stopped=nothing-structural ⟦criterion 1⟧ | 8 | 4 | 0 | 0 | 0 | 0 | 150 | 49 | 94 | 14901 | 1801012 | 278750 | 1.62 | 1282 | 1/2 | 0/5 | nothing-left |  |  | full |
| the report's structural row shows that stop reason without a spent/budget figure ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 48 | 13 | 26 | 5839 | 519771 | 69619 | 0.44 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| metrics.sh renders a complete report when the log's only structural-pass mark has just stopped=nothing-structural ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 38 | 0.33 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 4 | 0 | 4 | 4 | 3 | 4 | 0 | 4 |
| all | 488 |  |  |  |  |  |  |  |  |
| fast | 6 | 6 | 6 |  |  |  |  |  |  |
| target | 4 | 4 | 4 |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 63 | 122 | 21242 | 2332514 | 374347 | 2.18 |
