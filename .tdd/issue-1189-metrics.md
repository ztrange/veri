### 📊 Metrics — issue 1189

Wall time for the issue: 1164 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 1 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1209.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 7 | 4 | 1 | 2 | 450 | 10759 | 31306 | 0.13 |
| red | 2 | 1 | 0 | 0 | 61 | 53 | 13 | 24 | 4641 | 548867 | 84381 | 0.71 |
| green | 2 | 1 | 0 | 0 | 132 | 67 | 17 | 34 | 6426 | 792686 | 86397 | 0.80 |
| refactor | 2 | 1 | 0 | 0 | 64 | 31 | 11 | 22 | 3024 | 464945 | 80716 | 0.62 |
| predicate | 1 | 0 | 0 | 0 | 29 | 26 | 5 | 10 | 2408 | 198048 | 36739 | 0.38 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 4 | 4 | 0 | 0 | 128 | 57 | 19 | 38 | 5621 | 778852 | 149482 | 0.81 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 165 | 124 | 28 | 54 | 11328 | 1236453 | 170057 | 1.83 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A command started by detach-leaf.sh has SIGXFSZ at its default disposition: past a `ulimit -f` it dies of SIGXFSZ rather than getting EFBIG ⟦criterion 1⟧ | 7 | 3 | 0 | 0 | 0 | 0 | 177 | 46 | 90 | 16499 | 2004546 | 288233 | 2.51 | 365 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A command started by detach-leaf.sh has SIGXFSZ at its default disposition: past a `ulimit -f` it dies of SIGXFSZ rather than getting EFBIG ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 64 | 0.62 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s |
| --- | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 1 | 1 | 3 | 1 |
| fast | 25 | 26 | 25 |  |  |
| target | 1 |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 47 | 92 | 16949 | 2015305 | 319539 | 2.64 |
