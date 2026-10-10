### 📊 Metrics — issue 1421

Wall time for the issue: 1623 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1441.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 6 | 4 | 1 | 2 | 524 | 12489 | 31422 | 0.13 |
| red | 4 | 2 | 0 | 0 | 136 | 95 | 27 | 54 | 9187 | 1261310 | 173923 | 1.43 |
| green | 6 | 2 | 1 | 0 | 370 | 113 | 41 | 82 | 12619 | 1861573 | 250496 | 2.00 |
| refactor | 4 | 2 | 0 | 0 | 100 | 39 | 15 | 30 | 4083 | 586436 | 162912 | 1.13 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 7 | 1 | 0 | 267 | 100 | 39 | 78 | 12114 | 1635134 | 311216 | 1.53 |
| developer | claude-opus-5-5 | 7 | 0 | 0 | 0 | 345 | 151 | 45 | 90 | 14299 | 2086674 | 307537 | 3.16 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 260 | 1.31 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `build-develop-prompt.sh exhausted` prints a prompt that tells the leaf not to modify, revert or remove anything in the working tree ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 148 | 47 | 94 | 15102 | 2103411 | 335649 | 2.62 | 461 | 1/2 | 0/5 | nothing-left |  |  | full |
| the `exhausted` prompt tells the leaf that any statement that the criterion already holds must cite a run of the test command it was given ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 99 | 36 | 72 | 10787 | 1605908 | 251682 | 1.94 | 283 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `build-develop-prompt.sh exhausted` prints a prompt that tells the leaf not to modify, revert or remove anything in the working tree ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 51 | 0.55 |
| the `exhausted` prompt tells the leaf that any statement that the criterion already holds must cite a run of the test command it was given ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 49 | 0.58 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 5 | 6 | 5 | 3 | 2 | 2 | 23 | 5 | 1 | 2 | 1 |
| fast | 24 | 24 | 25 | 25 | 24 | 22 | 23 |  |  |  |  |  |  |
| target | 2 | 1 | 24 | 1 |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 84 | 168 | 26413 | 3721808 | 618753 | 4.69 |
