### 📊 Metrics — issue 1252

Wall time for the issue: 3418 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 1 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1254.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 5 | 1 | 2 | 383 | 11966 | 39581 | 0.16 |
| red | 2 | 1 | 0 | 0 | 56 | 38 | 10 | 20 | 3017 | 453576 | 86603 | 0.66 |
| green | 2 | 1 | 0 | 0 | 274 | 56 | 11 | 22 | 3795 | 501070 | 85127 | 0.67 |
| refactor | 2 | 1 | 0 | 0 | 146 | 34 | 13 | 26 | 3135 | 615949 | 86723 | 0.70 |
| predicate | 1 | 0 | 0 | 0 | 26 | 14 | 4 | 8 | 1139 | 164310 | 40957 | 0.38 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 4 | 4 | 0 | 0 | 281 | 54 | 16 | 32 | 4453 | 679264 | 166109 | 0.84 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 233 | 93 | 23 | 46 | 7016 | 1067607 | 172882 | 1.74 |

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
| strip_session_env given a session id keeps PATH, dropping only the PATH entries that carry the session id and keeping the rest in their order ⟦criterion 1⟧ | 7 | 3 | 0 | 0 | 0 | 0 | 142 | 38 | 76 | 11086 | 1734905 | 299410 | 2.42 | 589 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| strip_session_env given a session id keeps PATH, dropping only the PATH entries that carry the session id and keeping the rest in their order ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 146 | 0.70 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s |
| --- | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 2 | 3 | 1 |
| fast | 95 | 96 | 98 |  |  |
| target | 0 |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 39 | 78 | 11469 | 1746871 | 338991 | 2.58 |
