### 📊 Metrics — issue 1199

Wall time for the issue: 2393 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run bailed — ci-red, a process failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 7 | 2 | 4 | 842 | 54720 | 36633 | 0.17 |
| red | 3 | 1 | 0 | 0 | 255 | 124 | 27 | 50 | 12653 | 1261212 | 140504 | 1.47 |
| green | 2 | 1 | 0 | 0 | 365 | 81 | 20 | 40 | 7645 | 963436 | 88070 | 0.88 |
| refactor | 2 | 1 | 0 | 0 | 91 | 31 | 10 | 20 | 3007 | 408779 | 78624 | 0.61 |
| pin | 1 | 1 | 0 | 0 | 79 | 13 | 6 | 10 | 1660 | 201558 | 38545 | 0.21 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 5 | 5 | 0 | 0 | 312 | 64 | 23 | 44 | 7710 | 861423 | 187760 | 1.00 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 488 | 192 | 42 | 80 | 18097 | 2028282 | 194616 | 2.32 |

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
| When supervise.sh kills a leaf for being stuck (heartbeat silence), no process of that leaf's process group is left running afterwards, even when the group leader dies on SIGTERM and another member of the group ignores SIGTERM: the group gets SIGKILL once the grace period ends, judged by the group, not by the group leader alone ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 192 | 48 | 92 | 18901 | 2181810 | 258755 | 2.38 | 688 | unknown | 0/5 | nothing-left |  |  | full |
| When supervise.sh kills a leaf for running past its hard timeout, no process of that leaf's process group is left running afterwards, even when the group leader dies on SIGTERM and another member of the group ignores SIGTERM ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 57 | 15 | 28 | 6064 | 653175 | 86988 | 0.78 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| When supervise.sh kills a leaf for being stuck (heartbeat silence), no process of that leaf's process group is left running afterwards, even when the group leader dies on SIGTERM and another member of the group ignores SIGTERM: the group gets SIGKILL once the grace period ends, judged by the group, not by the group leader alone ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 91 | 0.61 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 30 | 31 | 27 | 2 | 28 | 26 |
| fast | 25 | 26 | 25 | 25 |  |  |
| target | 27 | 28 | 34 |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 65 | 124 | 25807 | 2889705 | 382376 | 3.33 |
