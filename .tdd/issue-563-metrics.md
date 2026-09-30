### 📊 Metrics — issue 563

Wall time for the issue: 4717 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/584.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 8 | 2 | 4 | 902 | 49231 | 32629 | 0.15 |
| red | 4 | 2 | 0 | 0 | 321 | 129 | 35 | 68 | 14719 | 1551978 | 163964 | 1.11 |
| green | 8 | 2 | 2 | 0 | 2399 | 195 | 68 | 136 | 19727 | 2912735 | 240207 | 1.74 |
| refactor | 6 | 2 | 1 | 0 | 969 | 117 | 40 | 78 | 12148 | 1588975 | 214548 | 1.30 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 2399 | 1.74 | 0 | 0.00 |
| refactor | 609 | 0.75 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| supervise.sh's awake clock advances across separate processes under a python3 whose time.monotonic() restarts per process: with a stub python3 on PATH mimicking that, the hard timeout and the heartbeat kill still fire ⟦criterion 1⟧ | 10 | 3 | 2 | 0 | 0 | 0 | 246 | 77 | 152 | 26542 | 3261853 | 347796 | 2.31 | 2726 | green 1/2, refactor 1/2 | 2/5 | nothing-structural |  |  | full |
| event.sh's awake reading (which metrics.sh subtracts across processes) comes from the same system-wide clock as supervise.sh, so it advances across processes under that stub python3 ⟦criterion 3⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 195 | 66 | 130 | 20052 | 2791835 | 270923 | 1.84 | 1180 | 1/2 | 2/5 | nothing-structural |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| supervise.sh's awake clock advances across separate processes under a python3 whose time.monotonic() restarts per process: with a stub python3 on PATH mimicking that, the hard timeout and the heartbeat kill still fire ⟦criterion 1⟧ | 1 | 2/5 | nothing-structural | PASS | 1 | 609 | 0.75 |
| event.sh's awake reading (which metrics.sh subtracts across processes) comes from the same system-wide clock as supervise.sh, so it advances across processes under that stub python3 ⟦criterion 3⟧ | 1 | 2/5 | nothing-structural | PASS | 0 | 360 | 0.55 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/10 | nothing-structural |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 31 | 29 | 29 | 29 | 0 | 28 | 1 | 33 | 0 | 1 | 0 | 23 | 1 | 21 | 3 | 0 | 0 | 0 | 1 | 1 | 22 | 1 | 1 | 25 |
| fast | 19 | 6 | 6 | 6 | 5 | 5 | 5 | 5 | 5 | 5 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 22 | 21 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 502 | 456 | 439 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 145 | 286 | 47496 | 6102919 | 651348 | 4.30 |
