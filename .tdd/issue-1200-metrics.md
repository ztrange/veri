### 📊 Metrics — issue 1200

Wall time for the issue: 1646 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 1 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1235.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 6 | 3 | 1 | 2 | 314 | 12385 | 29778 | 0.12 |
| red | 2 | 1 | 0 | 0 | 54 | 47 | 13 | 26 | 5119 | 596897 | 84423 | 0.73 |
| green | 2 | 1 | 0 | 0 | 161 | 40 | 14 | 28 | 4656 | 615420 | 79748 | 0.68 |
| refactor | 2 | 1 | 0 | 0 | 83 | 23 | 9 | 18 | 2514 | 356667 | 78119 | 0.57 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 4 | 4 | 0 | 0 | 165 | 43 | 16 | 32 | 5352 | 618304 | 143773 | 0.75 |
| developer | claude-opus-5-5 | 3 | 0 | 0 | 0 | 139 | 70 | 21 | 42 | 7251 | 963065 | 128295 | 1.36 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| An owner pid in .tdd/leaf.owner that is not a whole number of at least 1 (0, or a negative number) is never taken as a live leaf: supervise.sh treats the owner file as stale and launches the new leaf ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 110 | 36 | 72 | 12289 | 1568984 | 242290 | 1.99 | 387 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| An owner pid in .tdd/leaf.owner that is not a whole number of at least 1 (0, or a negative number) is never taken as a live leaf: supervise.sh treats the owner file as stale and launches the new leaf ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 83 | 0.57 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 31 | 0 | 28 | 28 |
| fast | 27 | 28 | 25 |  |  |  |
| target | 1 |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 37 | 74 | 12603 | 1581369 | 272068 | 2.12 |
